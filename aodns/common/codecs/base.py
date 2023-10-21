import logging


class BaseCodec:
    def __init__(self, sample_rate=8000, channels=1):
        self._logger = logging.getLogger(f"common/codec/{self.__class__.__name__[:-5].lower()}")
        self._logger_enc = logging.getLogger(f"common/codec/{self.__class__.__name__[:-5].lower()}/encode")
        self._logger_dec = logging.getLogger(f"common/codec/{self.__class__.__name__[:-5].lower()}/decode")
        self._sample_rate = sample_rate
        self._channels = channels
        pass

    @property
    def channels(self):
        return self._channels

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def frame_size(self):
        raise NotImplementedError("Not implemented")

    def encode(self, pcm: bytes) -> bytes:
        raise NotImplementedError("Not implemented")

    def decode(self, compressed: bytes) -> bytes:
        raise NotImplementedError("Not implemented")