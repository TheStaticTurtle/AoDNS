
class BaseFrameAsciializer:

    def asciialize(self, audio_frame: bytes) -> bytes:
        raise NotImplementedError("Not implemented")

    def deasciialize(self, audio_frame: bytes) -> bytes:
        raise NotImplementedError("Not implemented")
