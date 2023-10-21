import logging
import time
import typing
from .data_packing import PackedData
from .exception import AoDNSException

class SequenceException(AoDNSException):
    pass
class PastSequenceException(SequenceException):
    pass
class FutureSequenceException(SequenceException):
    pass

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
        for seq, pack in self.array:
            if seq == item or pack == item:
                return True
        return False

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
        self.last_seq_number = -1

    def add_dummy(self, number: int):
        self.array.append((number, None))
        self._logger.debug(f"Added dummy sequence number {number}")

    def add_sequence(self, number: int, pack: PackedData, raise_on_past=False):
        if number < self.last_seq_number:
            if raise_on_past:
                self._logger.error(f"Tried to insert sequence {number} which is lower than the last sequence number read {self.last_seq_number}")
                raise PastSequenceException(f"Last sequence number read was {self.last_seq_number} tried to insert sequence {number}")
            self._logger.warning(f"Insert sequence {number} which is lower than the last sequence number read {self.last_seq_number}")

        self.array.append((number, pack))
        self._logger.info(f"Received new sequence number {number} currently storing {len(self)} bytes in {len(self.array)} blocks ({self.sequences})")

    def remove_sequence(self, number: int):
        try:
            if number in self.nodata_sequences:
                self.array = list(filter(lambda x: x[0] != number, self.array))
                self._logger.info(f"Removing old read sequence {number}")
        except StopIteration:
            pass

    def cleanup_read(self, ignore_these: list[int]):
        tmp_copy = [seq for seq in self.nodata_sequences if seq not in ignore_these]
        if len(tmp_copy) > 0:
            self.array = list(filter(lambda x: x[0] not in tmp_copy, self.array))
            self._logger.info(f"Removed old read sequences: {tmp_copy}")


    def get_first(self, blocking=False) -> typing.Optional[typing.Tuple[int, PackedData]]:

        while True:
            try:
                first_seq_number = self.min
            except ValueError:
                if not blocking:
                    return None
                continue
            if self.last_seq_number != -1 and (self.last_seq_number + 1) < first_seq_number:
                self._logger.warning(f"Skipping sequences, expected sequence {self.last_seq_number + 1}, got {first_seq_number}")
            if self.last_seq_number != -1 and (self.last_seq_number + 1) > first_seq_number:
                self._logger.warning(f"Reading past sequences, expected sequence {self.last_seq_number + 1}, got {first_seq_number}")
            self.last_seq_number = first_seq_number

            seq_pack = next(filter(lambda x: x[0] == first_seq_number, self.array))
            self.array[self.array.index(seq_pack)] = (seq_pack[0], None)
            return seq_pack

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            return self.get_first(blocking=True)



