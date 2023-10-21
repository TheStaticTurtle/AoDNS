import opuslib

from .base import BaseCodec
from .. import const


class OpusCodec(BaseCodec):
    def __init__(self):
        super().__init__()
        self.encoder = opuslib.Encoder(
            fs=const.AUDIO_SAMPLE_RATE,
            channels=const.AUDIO_CHANNELS,
            application="voip"
        )
        self.decoder = opuslib.Decoder(
            fs=const.AUDIO_SAMPLE_RATE,
            channels=const.AUDIO_CHANNELS,
        )

    @property
    def frame_size(self) -> int:
        return 60 * const.AUDIO_SAMPLE_RATE // 1000

    def encode(self, pcm: bytes) -> bytes:
        data = self.encoder.encode(pcm, self.frame_size)
        self._logger_enc.info(f"Compressed {len(pcm)} of pcm data to {len(data)} bytes")
        return data

    def decode(self, compressed: bytes) -> bytes:
        data = self.decoder.decode(compressed, self.frame_size)
        self._logger_dec.info(f"Decompressed {len(compressed)} of opus data to {len(data)} bytes")
        return data
