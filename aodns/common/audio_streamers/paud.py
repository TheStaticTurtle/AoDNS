from .base import BaseAudioStreamer, AudioStreamerException
from .. import const

import pyaudio

class PyAudioStreamerException(AudioStreamerException):
    pass

class DirectionDisabledException(PyAudioStreamerException):
    pass


class PyAudioAudioStreamer(BaseAudioStreamer):
    def __init__(self, frame_size, en_input=False, en_output=False):
        super().__init__(frame_size)

        self._frame_size = frame_size
        self._en_input = en_input
        self._en_output = en_output

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=const.AUDIO_SAMPLE_RATE,
            input=en_input,
            output=en_output,
            input_device_index=self.p.get_default_input_device_info()["index"] if en_input else None,
            output_device_index=self.p.get_default_output_device_info()["index"] if en_output else None,
            frames_per_buffer=self.frame_size
        )

    def read(self) -> bytes:
        if not self._en_input:
            raise DirectionDisabledException("Input is not enabled on this streamer")

        data = self.stream.read(self.frame_size)
        self._logger_read.info(f"Read {len(data)} bytes from source")
        return data

    def write(self, data: bytes):
        if not self._en_output:
            raise DirectionDisabledException("Output is not enabled on this streamer")

        # self._logger_write.warning(f"{len(data)} -> {self.frame_size}")
        self.stream.write(data)
        self._logger_write.info(f"Wrote {len(data)} bytes to sink")
