import time
import typing
import zlib

import base91
import dns.resolver
import dns.nameserver
import logging

from ...common.data_packing import PackedData
from ...common.dns import DomainName

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
            self._logger.warning(f"Timeout while querying TXT/{domain} (retry={retry})")
            if retry >= 5:
                return []
            else:
                time.sleep(.1)
                return self._txt(domain, retry=retry+1)

    def get_available_sequences(self) -> typing.List[int]:
        try:
            txts = self._txt(self._root.__getattr__("sequence"))
            if len(txts) == 0:
                return []
        except dns.resolver.NoAnswer as e:
            self._logger.warning(f"Tried to query sequences but server responded with no answer")
            return []
        sequences_decoded = bytes(base91.decode(txts[0].decode("utf-8")))
        sequences_decompressed = zlib.decompress(sequences_decoded)
        seqs = [int(number) for number in sequences_decompressed.split(b",")]
        self._logger.debug(f"Available sequences on server: {seqs}")
        return seqs

    def get_sequence(self, number) -> typing.Optional[PackedData]:
        try:
            txts = self._txt(self._root.__getattr__(f"seq_{number}"))
            pack = PackedData()
            for txt in txts:
                index_bytes, frame = txt.split(pack.index_separator)
                pack.insert_indexed(int(index_bytes), frame)

            self._logger.info(f"Retrieved {pack} from sequence {number}")
            return pack
        except dns.resolver.NoAnswer as e:
            self._logger.warning(f"Tried to query sequence {number}, but server responded with no answers")
        return None
