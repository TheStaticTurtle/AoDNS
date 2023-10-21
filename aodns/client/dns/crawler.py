from .resolver import AoDnsResolver
from ...common.sequence_controller import SequenceReconstructor, PastSequenceException


class AoDnsCrawler:
    def __init__(self, resolver: AoDnsResolver, reconstructor: SequenceReconstructor):
        self._resolver = resolver
        self._reconstructor = reconstructor

    def crawl(self):
        sequences = self._resolver.get_available_sequences()
        for sequence in sequences:
            if sequence < self._reconstructor.last_seq_number:
                # Sequence was already played, no need to even try to add it
                self._reconstructor.add_dummy(sequence)
            if not self._reconstructor.__contains__(sequence):
                pack = self._resolver.get_sequence(sequence)
                if pack:
                    try:
                        self._reconstructor.add_sequence(sequence, pack, raise_on_past=True)
                    except PastSequenceException:
                        # Just to make sure we don't re-query it, add it as a sequence that was already read
                        self._reconstructor.add_dummy(sequence)

        # Make sure that the reconstructor doesn't have a sequence that it should have
        self._reconstructor.cleanup_read(sequences)
