import base64
from .base import BaseFrameAsciializer

class HexFrameAsciializer(BaseFrameAsciializer):

    def asciialize(self, audio_frame: bytes) -> bytes:
        return audio_frame.hex().encode("utf-8")

    def deasciialize(self, data: bytes) -> bytes:
        return bytes.fromhex(data.decode("utf-8"))
