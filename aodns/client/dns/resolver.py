import time
import typing
import zlib
import base91
import dns.resolver
import dns.nameserver
import logging

from ...common.data_packing import PackedData
from ...common.dns import DomainName
from ...common.function_cache import TimedCache


class AoDnsResolver:
    def __init__(self, root: DomainName, resolver_addr, resolver_port=53):
        self._logger = logging.getLogger(f"dns/aodns-resolver")
        self._root = root

        self._resolver = dns.resolver.Resolver()
        self._resolver.lifetime = 0.1
        self._resolver.nameservers = [
            dns.nameserver.Do53Nameserver(resolver_addr, port=resolver_port)
        ]

    def _txt(self, domain: DomainName, retry=0):
        try:
            response = self._resolver.resolve(domain, "TXT").response
            assert len(response.answer) == 1

            return [
                bytes(txt.strings[0])
                for txt in response.answer[0].items.keys()
            ]
        except dns.resolver.LifetimeTimeout:
            if retry >= 10:
                # self._logger.warning(f"Timeout while querying TXT/{domain} (retry={retry})")
                raise dns.resolver.NoAnswer(f"Timeout while querying TXT/{domain} exceeded retries")
            else:
                time.sleep(.25)
                return self._txt(domain, retry=retry+1)
        except dns.resolver.NoNameservers as e:
            self._logger.error(f"Error while querying TXT/{domain}: {e}")

    @TimedCache(period=4)
    def get_available_sequences(self) -> typing.List[int]:
        txts = []
        while len(txts) == 0:
            try:
                txts = self._txt(self._root.__getattr__("sequence"))
            except dns.resolver.NoAnswer:
                pass
            if len(txts) == 0:
                self._logger.warning(f"Tried to query sequences but server responded with no answer")

        sequences_decoded = bytes(base91.decode(txts[0].decode("utf-8")))
        sequences_decompressed = zlib.decompress(sequences_decoded)
        seqs = [int(number) for number in sequences_decompressed.split(b",")]
        self._logger.info(f"Available sequences on server: {seqs}")
        return seqs

    def get_sequence(self, number) -> typing.Optional[PackedData]:
        try:
            txts = self._txt(self._root.__getattr__(f"seq_{number}"))
            if txts is None:
                self._logger.warning(f"Tried to query sequence {number}, but server responded with no answers")
                return txts

            pack = PackedData()
            for txt in txts:
                index_bytes, frame = txt.split(pack.index_separator)
                pack.insert_indexed(int(index_bytes), frame)

            self._logger.info(f"Retrieved {pack} from sequence {number}")
            return pack
        except dns.resolver.NoAnswer as e:
            self._logger.warning(f"Tried to query sequence {number}, but server responded with no answers")
        return None
