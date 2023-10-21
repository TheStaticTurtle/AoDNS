import logging

from ..exception import AoDNSException

class AudioStreamerException(AoDNSException):
    pass

class BaseAudioStreamer:
    def __init__(self, frame_size, sample_rate, channels):
        self._logger = logging.getLogger(f"common/audio-streamer/{self.__class__.__name__[:-13].lower()}")
        self._logger_read = logging.getLogger(f"common/audio-streamer/{self.__class__.__name__[:-13].lower()}/read")
        self._logger_write = logging.getLogger(f"common/audio-streamer/{self.__class__.__name__[:-13].lower()}/write")
        self._frame_size = frame_size
        self._sample_rate = sample_rate
        self._channels = channels

    def read(self) -> bytes:
        raise NotImplementedError("Not implemented")

    def write(self, data: bytes):
        raise NotImplementedError("Not implemented")
