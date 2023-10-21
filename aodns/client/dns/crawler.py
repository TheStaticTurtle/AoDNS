from .resolver import AoDnsResolver
from ...common.sequence_controller import SequenceReconstructor


class AoDnsCrawler:
    def __init__(self, resolver: AoDnsResolver, reconstructor: SequenceReconstructor):
        self._resolver = resolver
        self._reconstructor = reconstructor

    def crawl(self):
        sequences = self._resolver.get_available_sequences()
        for sequence in sequences:
            if sequence not in self._reconstructor:
                pack = self._resolver.get_sequence(sequence)
                if pack:
                    self._reconstructor.add_sequence(sequence, pack)

        # Make sure that the reconstructor doesn't have a sequence that it should have
        for reconstructor_sequence in self._reconstructor.nodata_sequences:
            if reconstructor_sequence not in sequences:
                self._reconstructor.remove_sequence(reconstructor_sequence)
