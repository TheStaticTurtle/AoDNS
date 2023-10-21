import base64
from .base import BaseFrameAsciializer

class Base16FrameAsciializer(BaseFrameAsciializer):

    def asciialize(self, audio_frame: bytes) -> bytes:
        return base64.b16encode(audio_frame)

    def deasciialize(self, data: bytes) -> bytes:
        return base64.b16decode(data)
