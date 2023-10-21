import datetime
import logging
import socketserver
import struct

import dnslib

from .request_handlers import DNSRequestHandler

class BaseDNSRequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger(f"dns/request-handler")
        super().__init__(request, client_address, server)

    def get_data(self):
        raise NotImplementedError
    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        data = self.get_data()
        try:
            response = self.server.dns_handler.handle(data, self.client_address)
            self.send_data(response)
        except dnslib.dns.DNSError as e:
            self.logger.error(f"Failed to create response for dns query: {e}")

class TCPDNSRequestHandler(BaseDNSRequestHandler):
    def get_data(self):
        data = self.request.recv(8192).strip()
        sz = struct.unpack('>H', data[:2])[0]
        if sz < len(data) - 2:
            raise Exception("Wrong size of TCP packet")
        elif sz > len(data) - 2:
            raise Exception("Too big TCP packet")
        return data[2:]

    def send_data(self, data):
        sz = struct.pack('>H', len(data))
        return self.request.sendall(sz + data)
class UDPDNSRequestHandler(BaseDNSRequestHandler):
    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


class ThreadedDNSTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, host_port_tuple, handler: DNSRequestHandler):
        super().__init__(host_port_tuple, TCPDNSRequestHandler)
        self.logger = logging.getLogger(f"dns/tcp-server({host_port_tuple[0]}:{host_port_tuple[1]})")
        self.logger.info("Hellow world")
        self.dns_handler = handler
class ThreadedDNSUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    def __init__(self, host_port_tuple, handler: DNSRequestHandler):
        super().__init__(host_port_tuple, UDPDNSRequestHandler)
        self.logger = logging.getLogger(f"dns/udp-server({host_port_tuple[0]}:{host_port_tuple[1]})")
        self.logger.info("Hellow world")
        self.dns_handler = handler

