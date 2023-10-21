import argparse
import sys
import logging
import time

import coloredlogs

from ..common import codecs, frame_asciializer, audio_streamers, sequence_controller, dns
from .dns import AoDnsResolver, AoDnsCrawler
from .sequence_reader import SequenceReader

coloredlogs.install(stream=sys.stdout, level=logging.INFO)
logging.getLogger("dns/aodns-resolver").setLevel(logging.WARNING)
logging.getLogger("common/audio-streamer/pyaudio/read").setLevel(logging.WARNING)
logging.getLogger("common/audio-streamer/pyaudio/write").setLevel(logging.WARNING)
logging.getLogger("common/codec/opus/encode").setLevel(logging.WARNING)
logging.getLogger("common/codec/opus/decode").setLevel(logging.WARNING)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='AoDNS client')
    parser.add_argument('root-domain', type=str, help="Root domain of the AoDNS server", default="music.example.com")
    server_arg_grp = parser.add_argument_group("dns")
    server_arg_grp.add_argument('dns-server', type=str, help="Address of the DNS resolver", default="127.0.0.1")
    server_arg_grp.add_argument('--dns-port', type=int, help="Port of the DNS resolver", default=5053)
    server_arg_grp = parser.add_argument_group("audio")
    server_arg_grp.add_argument('--channels', type=int, help="Audio channel count", default=1, choices=[1, 2])
    server_arg_grp.add_argument('--sample-rate', type=int, help="Audio sample rate", default=16000, choices=[8000, 12000, 16000])
    args = parser.parse_args()

    root = dns.DomainName(getattr(args, "root-domain"))
    resolver = AoDnsResolver(root, getattr(args, "dns-server"), resolver_port=args.dns_port)
    reconstructor = sequence_controller.SequenceReconstructor()

    crawler = AoDnsCrawler(resolver, reconstructor)

    codec = codecs.OpusCodec(sample_rate=args.sample_rate, channels=args.channels)
    streamer = audio_streamers.PyAudioAudioStreamer(codec.frame_size, codec.sample_rate, codec.channels, en_output=True)
    asciializer = frame_asciializer.Base91FrameAsciializer()

    reader = SequenceReader(
        reconstructor,
        asciializer,
        codec,
        streamer
    )
    reader.start()

    while True:
        crawler.crawl()
        time.sleep(.5)
