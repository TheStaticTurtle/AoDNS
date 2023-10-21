import logging
import sys
import threading

from ..common.codecs.base import BaseCodec
from ..common.audio_streamers.base import BaseAudioStreamer
from ..common.frame_asciializer.base import BaseFrameAsciializer
from ..common.sequence_controller import SequenceReconstructor


class SequenceReader(threading.Thread):
    def __init__(
            self,
            reconstructor: SequenceReconstructor,
            asciializer: BaseFrameAsciializer,
            codec: BaseCodec,
            streamer: BaseAudioStreamer,
    ):
        super().__init__(daemon=True)
        self._logger = logging.getLogger(f"client/sequence-reader")
        self._reconstructor = reconstructor
        self._asciializer = asciializer
        self._codec = codec
        self._streamer = streamer

    def run(self):
        self._logger.info("Begin")
        for sequence, pack in self._reconstructor:
            self._logger.info(f"Reading sequence {sequence}: {pack}")

            for frame in pack.frames:
                compressed_data = self._asciializer.deasciialize(frame)
                pcm_data = self._codec.decode(compressed_data)
                self._streamer.write(pcm_data)

