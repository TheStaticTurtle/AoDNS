import argparse
import sys
import threading
import logging
import coloredlogs

from ..common import codecs, frame_asciializer, data_packing, audio_streamers, sequence_controller
from .dns import Zone, DNSRequestHandler, servers
from .records_generator import RecordsGenerator

coloredlogs.install(stream=sys.stdout, level=logging.INFO)
logging.getLogger("common/data-packer").setLevel(logging.WARNING)
logging.getLogger("common/audio-streamer/pyaudio/read").setLevel(logging.WARNING)
logging.getLogger("common/audio-streamer/pyaudio/write").setLevel(logging.WARNING)
logging.getLogger("common/codec/opus/encode").setLevel(logging.WARNING)
logging.getLogger("common/codec/opus/decode").setLevel(logging.WARNING)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='AoDNS server')
    parser.add_argument('root-domain', type=str, help="Root domain of the AoDNS server", default="music.example.com")
    server_arg_grp = parser.add_argument_group("data")
    server_arg_grp.add_argument('--max-data-per-feed', type=int, default=250)
    server_arg_grp.add_argument('--max-bytes-per-record', type=int, default=2000)
    server_arg_grp.add_argument('--max-sequences', type=int, default=75)
    server_arg_grp = parser.add_argument_group("audio")
    server_arg_grp.add_argument('--channels', type=int, help="Audio channel count", default=1, choices=[1, 2])
    server_arg_grp.add_argument('--sample-rate', type=int, help="Audio sample rate", default=16000, choices=[8000, 12000, 16000])
    server_arg_grp = parser.add_argument_group("server")
    server_arg_grp.add_argument('--dns-port', type=int, help="Port of the server", default=5053)
    args = parser.parse_args()


    codec = codecs.OpusCodec(sample_rate=args.sample_rate, channels=args.channels)
    streamer = audio_streamers.PyAudioAudioStreamer(codec.frame_size, codec.sample_rate, codec.channels, en_input=True)
    asciializer = frame_asciializer.Base91FrameAsciializer()
    packer = data_packing.DataPacker(args.max_data_per_feed, args.max_bytes_per_record)
    sequencer = sequence_controller.SequenceGenerator(args.max_sequences)

    dns_zone = Zone(getattr(args, "root-domain"))
    dns_handler = DNSRequestHandler(dns_zone)

    records_gen = RecordsGenerator(sequencer, codec)

    tcp_server = servers.ThreadedDNSUDPServer(('', args.dns_port), dns_handler)
    udp_server = servers.ThreadedDNSTCPServer(('', args.dns_port), dns_handler)
    threading.Thread(target=tcp_server.serve_forever, daemon=True).start()
    threading.Thread(target=udp_server.serve_forever, daemon=True).start()


    while True:
        pcm = streamer.read()
        compressed = codec.encode(pcm)
        ascii_data = asciializer.asciialize(compressed)

        pack = packer.feed(ascii_data)
        if pack is not None:
            sequencer.add_sequence(pack)
            records_gen.update(dns_zone)





