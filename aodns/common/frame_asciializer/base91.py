import base91
from .base import BaseFrameAsciializer

class Base91FrameAsciializer(BaseFrameAsciializer):

    def asciialize(self, audio_frame: bytes) -> bytes:
        return base91.encode(audio_frame).encode("utf-8")

    def deasciialize(self, data: bytes) -> bytes:
        return bytes(base91.decode(data.decode("utf-8")))
