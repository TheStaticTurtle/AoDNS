import logging
import typing

class PackerException(Exception):
    pass
class PackFullException(PackerException):
    pass
class AppendTooLargeException(PackerException):
    pass

class PackedData:
    def __init__(self, index_separator=b"'''"):
        self.index_separator = index_separator
        self._frames = []

    @property
    def frame_count(self):
        return len(self._frames)

    def __len__(self):
        return len(b''.join([d for i, d in self._frames]))

    def __repr__(self):
        return f"<{self.__class__.__name__} frame_count={len(self._frames)} size={len(self)}>"

    def insert_indexed(self, index: int, frame: bytes):
        self._frames.append((index, frame))

    def append(self, frame: bytes):
        self.insert_indexed(len(self._frames), frame)

    @property
    def frames_indexed(self) -> typing.List[bytes]:
        sorted_frames = sorted(self._frames, key=lambda tup: tup[0])
        return [
            f"{index:03d}".encode("utf-8") + self.index_separator + frame
            for index, frame in sorted_frames
        ]

    @property
    def frames(self) -> typing.List[bytes]:
        sorted_frames = sorted(self._frames, key=lambda tup: tup[0])
        return [frame for (index, frame) in sorted_frames]

# PackedData class with size checking when appending/inserting frames
class FinitePackedData(PackedData):
    def __init__(self, max_len_per_feed, max_len_total, index_separator=b"'''"):
        super().__init__(index_separator)
        self.max_len_per_feed = max_len_per_feed
        self.max_len_total = max_len_total

    def _validate_data_len(self, data):
        total_dlen = 3 + len(self.index_separator) + len(data)
        if total_dlen > self.max_len_per_feed:
            raise AppendTooLargeException(f"Too much data to append len:{len(data)} (max: {self.max_len_per_feed})")
        if (len(self) + total_dlen) > self.max_len_total:
            raise PackFullException(f"Pack is full {len(self)} (max: {self.max_len_total})")

    def append(self, frame: bytes):
        self._validate_data_len(frame)
        super().append(frame)

    def insert_indexed(self, index: int, frame: bytes):
        self._validate_data_len(frame)
        super().insert_indexed(index, frame)



class DataPacker:
    def __init__(self, max_per_feed, max_bytes):
        self._logger = logging.getLogger(f"common/data-packer")
        self.max_per_feed = max_per_feed
        self.max_bytes = max_bytes
        self.pack = FinitePackedData(self.max_per_feed, self.max_bytes)

    def feed(self, data: bytes) -> typing.Optional[PackedData]:
        try:
            self.pack.append(data)
        except PackFullException as e:
            self._logger.info("Current pack is full, creating new one")
            ret = self.pack
            self.pack = FinitePackedData(self.max_per_feed, self.max_bytes)
            self.pack.append(data)
            return ret