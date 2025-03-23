import socket
import ssl


class SocketClient:
    PROTOCOL_TCP = 1
    PROTOCOL_SSL = 2
    PROTOCOL_UDP = 3

    def __init__(self):
        self.hostname = None
        self.port = None
        self.sock = None
        self.protocol = self.PROTOCOL_TCP
        self.timeout = -1

        self.ssl_context = None

    def initialize(self, protocol, timeout=8.0):
        self.protocol = protocol
        self.timeout = timeout
        self.ssl_context = None

    def set_ssl_context(self, ssl_context):
        self.ssl_context = ssl_context

    def create(self, hostname, port=0):
        if self.protocol != self.PROTOCOL_UDP:
            self.sock = self.create_tcp_socket(hostname, port)
        else:
            self.sock = self.create_udp_socket()

        self.hostname = hostname
        self.port = port

    def create_tcp_socket(self, hostname, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.timeout > 0:
            sock.settimeout(self.timeout)

        sock.connect((hostname, port))

        if self.protocol == self.PROTOCOL_SSL:
            if not self.ssl_context:
                context = ssl.create_default_context()
            else:
                context = ssl.SSLContext(self.ssl_context)

            sock = context.wrap_socket(sock, server_hostname=hostname)

        return sock

    def create_udp_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if self.timeout > 0:
            sock.settimeout(self.timeout)

        return sock

    def send(self, binary):
        if self.protocol != self.PROTOCOL_UDP:
            self.sock.sendall(binary)
        else:
            self.sock.sendto(binary, (self.hostname, self.port))

    def receive(self, bufsize=65565):
        if self.protocol != self.PROTOCOL_UDP:
            binary = self.sock.recv(bufsize)
        else:
            binary, _ = self.sock.recvfrom(bufsize)

        return binary

    def is_connected(self):
        if self.sock:
            error = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

            if error == 0:
                return True

        return False

    def close(self):
        if self.sock:
            self.sock.close()

            self.sock = None
            self.hostname = None
            self.port = None

    def __del__(self):
        self.close()
