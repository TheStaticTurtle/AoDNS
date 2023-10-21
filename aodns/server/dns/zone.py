from dnslib import *

from ...common.dns import DomainName, Record


class Zone:
    def __init__(self, root_domain):
        self.root = DomainName(f"{root_domain}.")

        self._soa_record = Record(self.root, [
            SOA(
                times=(
                    201307231,  # serial number
                    60 * 60 * 1,  # refresh
                    60 * 60 * 3,  # retry
                    60 * 60 * 24,  # expire
                    60 * 60 * 1,  # minimum
                )
            )
        ], ttl=60)


        self._base_records = {
            self.soa.domain: self.soa,
        }
        self._user_records = {
        }

    @property
    def soa(self):
        return self._soa_record

    @property
    def records(self):
        return self._base_records | self._user_records

    def clear_records(self):
        self._user_records.clear()

    def add_record(self, record: Record):
        self._user_records[record.domain] = record
