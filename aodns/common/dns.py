from dnslib import RD

class DomainName(str):
    def __getattr__(self, item):
        return DomainName(item + '.' + self)

class Record:
    def __init__(self, domain: DomainName, fields: list[RD], ttl=60):
        self.domain = domain
        self.fields = fields
        self.ttl = ttl
