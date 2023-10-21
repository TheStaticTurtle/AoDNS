import logging

from .zone import Zone
from dnslib import *

class DNSRequestHandler:
    def __init__(self, zone: Zone):
        self.logger = logging.getLogger(f"dns/request-handler")
        self.zone = zone

    def handle(self, request_data, client_address):
        request = DNSRecord.parse(request_data)

        reply = DNSRecord(
            DNSHeader(id=request.header.id, qr=1, aa=1, ra=1),
            q=request.q
        )

        question_name = str(request.q.qname)
        question_type = QTYPE[request.q.qtype]

        if question_name.endswith(self.zone.root):
            for name, record in self.zone.records.items():
                if name == question_name:
                    for record_data in record.fields:
                        record_data_type = record_data.__class__.__name__
                        if question_type in ['*', record_data_type]:
                            reply.add_answer(RR(
                                rname=request.q.qname,
                                rtype=getattr(QTYPE, record_data_type),
                                rclass=1,
                                ttl=record.ttl,
                                rdata=record_data
                            ))

            reply.add_auth(RR(rname=self.zone.root, rtype=QTYPE.SOA, rclass=1, ttl=self.zone.soa.ttl, rdata=self.zone.soa.fields[0]))

        if len(reply.rr) == 0:
            self.logger.warning(f"Request from \"{client_address[0]}\" for \"{QTYPE[request.q.qtype]}/{request.q.qname}\" yielded 0 results")
        else:
            self.logger.info(f"Responded to \"{QTYPE[request.q.qtype]}/{request.q.qname}\" from \"{client_address[0]}\" with {len(reply.rr)} answers")

        return reply.pack()

