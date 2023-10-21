import logging

from ..exception import AoDNSException

class AudioStreamerException(AoDNSException):
    pass

class BaseAudioStreamer:
    def __init__(self, frame_size):
        self._logger = logging.getLogger(f"common/audio-streamer/{self.__class__.__name__[:-13].lower()}")
        self._logger_read = logging.getLogger(f"common/audio-streamer/{self.__class__.__name__[:-13].lower()}/read")
        self._logger_write = logging.getLogger(f"common/audio-streamer/{self.__class__.__name__[:-13].lower()}/write")
        self.frame_size = frame_size

    def read(self) -> bytes:
        raise NotImplementedError("Not implemented")

    def write(self, data: bytes):
        raise NotImplementedError("Not implemented")
