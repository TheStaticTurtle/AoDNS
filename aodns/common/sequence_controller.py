import logging
import time
import typing

from .data_packing import PackedData

class SequenceBase:
    def __init__(self):
        self.array = []

    @property
    def sequences(self) -> list[int]:
        return [seq for (seq, pack) in self.array if pack is not None]

    @property
    def nodata_sequences(self) -> list[int]:
        return [seq for (seq, pack) in self.array if pack is None]

    @property
    def all_sequences(self) -> list[int]:
        return [seq for (seq, pack) in self.array]

    @property
    def dict(self) -> dict[int, PackedData]:
        return {seq: obj for (seq, obj) in self.array}

    def __len__(self) -> int:
        return sum([len(pack) for seq, pack in self.array if pack is not None])

    def __contains__(self, item):
        if not isinstance(item, int):
            raise ValueError(f"{item.__class__} comparison not supported")
        return any([seq == item for seq, pack in self.array])

    @property
    def max(self):
        return max(self.sequences)

    @property
    def min(self):
        return min(self.sequences)

class SequenceGenerator(SequenceBase):
    def __init__(self, max_concurrent_numbers):
        super().__init__()
        self._logger = logging.getLogger(f"common/sequence-generator")
        self.max_concurrent_numbers = max_concurrent_numbers
        self._sequence_number = 0

    def add_sequence(self, pack: PackedData):
        self.array.append((self._sequence_number, pack))
        self._logger.info(f"Incremented sequence number to {self._sequence_number} currently storing {len(self)} bytes in {len(self.array)} blocks")

        self._sequence_number += 1
        while len(self.array) > self.max_concurrent_numbers:
            self.array = self.array[1:]

class SequenceReconstructor(SequenceBase):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(f"common/sequence-reconstructor")

    def add_sequence(self, number: int, pack: PackedData):
        self.array.append((number, pack))
        self._logger.info(f"Received new sequence number {number} currently storing {len(self)} bytes in {len(self.array)} blocks ({self.sequences})")

    def remove_sequence(self, number: int):
        try:
            seq_pack = next(filter(lambda x: x[0] != number, self.array))
            self.array.remove(seq_pack)
        except StopIteration:
            pass


    def get_first(self, blocking=False) -> typing.Optional[typing.Tuple[int, PackedData]]:
        while True:
            try:
                first_seq_number = self.min
            except ValueError:
                if not blocking:
                    return None
                continue
            seq_pack = next(filter(lambda x: x[0] == first_seq_number, self.array))
            self.array[self.array.index(seq_pack)] = (seq_pack[0], None)
            return seq_pack

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            return self.get_first(blocking=True)



