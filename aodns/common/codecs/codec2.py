import struct

import pycodec2
import numpy as np
from .base import BaseCodec


class Codec2Codec(BaseCodec):
    INT16_BYTE_SIZE = 2

    def __init__(self):
        super().__init__()
        assert self._sample_rate == 8000
        assert self._channels == 1

        self.c2 = pycodec2.Codec2(1200)
    
    @property
    def frame_size(self) -> int:
        return self.c2.samples_per_frame()

    @property
    def _packet_size(self) -> int:
        return self.frame_size * self.INT16_BYTE_SIZE

    @property
    def _struct_format(self) -> str:
        return '{}h'.format(self.c2.samples_per_frame())


    def encode(self, pcm: bytes) -> bytes:
        data = self.c2.encode(
            np.array(
                struct.unpack(self._struct_format, pcm),
                dtype=np.int16
            )
        )
        self._logger_enc.info(f"Compressed {len(pcm)} of pcm data to {len(data)} bytes")
        return data

    def decode(self, compressed: bytes) -> bytes:
        packet = self.c2.decode(compressed)
        data = struct.pack(self._struct_format, *packet)
        self._logger_dec.info(f"Decompressed {len(compressed)} of codec2 data to {len(data)} bytes")
        return data
