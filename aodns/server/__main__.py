import sys
import threading
import logging
import coloredlogs

from ..common import const, codecs, frame_asciializer, data_packing, audio_streamers, sequence_controller
from .dns import Zone, DNSRequestHandler, servers
from .records_generator import RecordsGenerator

coloredlogs.install(stream=sys.stdout, level=logging.INFO)
logging.getLogger("common/data-packer").setLevel(logging.WARNING)
logging.getLogger("common/audio-streamer/pyaudio/read").setLevel(logging.WARNING)
logging.getLogger("common/audio-streamer/pyaudio/write").setLevel(logging.WARNING)
logging.getLogger("common/codec/opus/encode").setLevel(logging.WARNING)
logging.getLogger("common/codec/opus/decode").setLevel(logging.WARNING)

if __name__ == "__main__":
    codec = codecs.OpusCodec()
    streamer = audio_streamers.PyAudioAudioStreamer(codec.frame_size, en_input=True)
    asciializer = frame_asciializer.Base91FrameAsciializer()
    packer = data_packing.DataPacker(250, 2000)
    sequencer = sequence_controller.SequenceGenerator(50)

    dns_zone = Zone("music.internal.tugler.fr")
    dns_handler = DNSRequestHandler(dns_zone)

    records_gen = RecordsGenerator(sequencer, codec.frame_size)

    tcp_server = servers.ThreadedDNSUDPServer(('', 5053), dns_handler)
    udp_server = servers.ThreadedDNSTCPServer(('', 5053), dns_handler)
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





