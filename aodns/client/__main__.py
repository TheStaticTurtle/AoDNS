import sys
import threading
import logging
import time

import coloredlogs

from ..common import const, codecs, frame_asciializer, data_packing, audio_streamers, sequence_controller, dns
from .dns import AoDnsResolver, AoDnsCrawler
from .sequence_reader import SequenceReader

coloredlogs.install(stream=sys.stdout, level=logging.INFO)
logging.getLogger("dns/aodns-resolver").setLevel(logging.WARNING)
logging.getLogger("common/audio-streamer/pyaudio/read").setLevel(logging.WARNING)
logging.getLogger("common/audio-streamer/pyaudio/write").setLevel(logging.WARNING)
logging.getLogger("common/codec/opus/encode").setLevel(logging.WARNING)
logging.getLogger("common/codec/opus/decode").setLevel(logging.WARNING)

if __name__ == "__main__":
    root = dns.DomainName("music.internal.tugler.fr")
    # resolver = AoDnsResolver(root, "10.10.15.219", resolver_port=5053)
    resolver = AoDnsResolver(root, "10.10.15.13", resolver_port=53)
    reconstructor = sequence_controller.SequenceReconstructor()

    crawler = AoDnsCrawler(resolver, reconstructor)

    codec = codecs.OpusCodec()
    streamer = audio_streamers.PyAudioAudioStreamer(codec.frame_size, en_output=True)
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


    # while True:
    #     pcm = reader.read()
    #     compressed = codec.encode(pcm)
    #     ascii_data = asciializer.asciialize(compressed)
    #
    #     pack = packer.feed(ascii_data)
    #     if pack is not None:
    #         sequencer.add_sequence(pack)
    #         records_gen.update(dns_zone)
    #