import opuslib

from .base import BaseCodec


class OpusCodec(BaseCodec):
    def __init__(self, sample_rate=16000, channels=1):
        super().__init__(sample_rate=sample_rate, channels=channels)
        self.encoder = opuslib.Encoder(
            fs=self._sample_rate,
            channels=self._channels,
            application="voip"
        )
        self.decoder = opuslib.Decoder(
            fs=self._sample_rate,
            channels=self._channels,
        )

    @property
    def frame_size(self) -> int:
        return 60 * self._sample_rate // 1000

    def encode(self, pcm: bytes) -> bytes:
        data = self.encoder.encode(pcm, self.frame_size)
        self._logger_enc.info(f"Compressed {len(pcm)} of pcm data to {len(data)} bytes")
        return data

    def decode(self, compressed: bytes) -> bytes:
        data = self.decoder.decode(compressed, self.frame_size)
        self._logger_dec.info(f"Decompressed {len(compressed)} of opus data to {len(data)} bytes")
        return data
