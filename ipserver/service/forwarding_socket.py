from ipserver.util.socket_client import SocketClient
from ipserver.util.urlparser import URLParser


class ForwardingSocket:
    def __init__(self, args, socket=None):
        if not socket:
            self.socket = SocketClient()

        (protocol, hostname, port) = self.parse_destination(args.forwarding)

        self.protocol = protocol
        self.hostname = hostname
        self.port = port

        self.timeout = args.timeout

    def create_parsed_url(self, forwarding):
        url_parser = URLParser()

        parsed_url = url_parser.parse(forwarding)

        return parsed_url

    def parse_destination(self, forwarding):
        parsed_url = self.create_parsed_url(forwarding)

        if parsed_url.scheme == 'tcp':
            protocol = SocketClient.PROTOCOL_TCP
        elif parsed_url.scheme == 'udp':
            protocol = SocketClient.PROTOCOL_UDP
        elif parsed_url.scheme == 'ssl':
            protocol = SocketClient.PROTOCOL_SSL
        else:
            protocol = SocketClient.PROTOCOL_TCP

        port = parsed_url.port if parsed_url.port else 80

        return (protocol, parsed_url.hostname, port)

    def initialize(self):
        if self.socket:
            if self.socket.is_connected():
                self.socket.close()

            self.socket.initialize(self.protocol, self.timeout)

            self.socket.create(self.hostname, self.port)

    def receive(self, buf):
        if not self.is_connected():
            self.initialize()

        return self.socket.receive(buf)

    def send(self, binary):
        if not self.is_connected():
            self.initialize()

        self.socket.send(binary)

    def is_connected(self):
        if self.socket and self.socket.is_connected():
            return True

        return False

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def __del__(self):
        self.close()
