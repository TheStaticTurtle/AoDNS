import base91
from dnslib import TXT
import zlib

from .dns.zone import Zone
from ..common import const
from ..common.sequence_controller import SequenceGenerator
from ..common.dns import Record



class RecordsGenerator:
    def __init__(self, sequencer: SequenceGenerator, codec_frame_size):
        self._sequencer = sequencer
        self._codec_frame_size = codec_frame_size

    def update(self, zone: Zone):
        sequences_text = ",".join([str(n) for n in self._sequencer.sequences])
        sequences_compressed = base91.encode(zlib.compress(sequences_text.encode("utf-8"), level=9))

        zone.clear_records()
        zone.add_record(
            Record(
                zone.root.__getattr__("sequence"),
                [TXT(sequences_compressed)],
                ttl=10
            )
        )
        for sequence_number, pack in self._sequencer.dict.items():
            seq_duration = (self._codec_frame_size * pack.frame_count) / (const.AUDIO_SAMPLE_RATE * const.AUDIO_CHANNELS * 2)
            ttl = int(seq_duration * self._sequencer.max_concurrent_numbers * 0.8)
            ttl = 5 if ttl < 5 else ttl

            zone.add_record(
                Record(
                    zone.root.__getattr__(f"seq_{sequence_number}"),
                    [
                        TXT(frame)
                        for frame in pack.frames_indexed
                    ],
                    ttl=ttl
                )
            )
