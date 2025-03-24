import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
from ipserver.util.sys_util import Output

'''
Benchmark download speed by downloading dummy image. Default: 200MB
You can test by using browser or curl or any other client tool.

$ python3 benchmark_download_speed.py --port=8002
$ curl http://develop-server:8002/bench?mb=250
'''


class MyPipeline(Pipeline):
    def __init__(self):
        super().__init__()

        self.total_byte = 0

    def pre_configure(self, args):
        args.quiet = 2

    def start_listen(self, socket_server, conn_bucket):
        Output.warn('[BENCHMARK - Transfer speed]\n')
        Output.line('You can test by `http://your-host:8002/bench`.\n')
        Output.warn('Waiting for request from client... ')

    def _parse_path(self, data):
        match = re.search(r'GET\s+(/[^\s]*)', data)

        if match:
            return urlparse(match.group(1))

        return None

    def _get_mb_size(self, parsed_url):
        mb_size = None

        if parsed_url:
            params = parse_qs(parsed_url.query)

            mb = params.get('mb')

            if mb:
                mb_size = int(mb[0])

        if mb_size is None:
            mb_size = 200

        self.total_byte = mb_size * 1024 * 1024

        return mb_size

    def post_receive(self, conn_sock, binary):
        data = binary.decode().strip()

        if data:
            parsed_url = self._parse_path(data)

            if parsed_url.path == '/bench':
                mb_size = self._get_mb_size(parsed_url)
                self._send_test(conn_sock, mb_size)
            else:
                self._send_not_found(conn_sock)

        return binary

    def _send_not_found(self, conn_sock):
        response = '''HTTP/1.1 404 OK
Server: IpServer
Content-Type: text/html
Content-Length: 0

'''

        conn_sock.send_queue(response.encode())

    def _send_test(self, conn_sock, mb_size):
        conn_sock.data['sent_byte'] = 0

        data = self._create_http_header()
        conn_sock.send_queue(data)

        Output.warn('\nStarting BENCHMARK... ')

        conn_sock.send_queue(b'TEST_START\n')

        conn_sock.data['begin_tm'] = datetime.now()

        for i in range(mb_size):
            data = self._create_mbyte_data(conn_sock)
            conn_sock.send_queue(data)

        conn_sock.send_queue(b'TEST_FINISH\n')

    def _create_http_header(self):
        response = '''HTTP/1.1 200 OK
Server: IpServer
Content-Type: image/png
Content-Length: {}

'''

        response = response.format(self.total_byte)

        return response.encode()

    def _create_mbyte_data(self, conn_sock):
        basic = b'\0\1\2\3'
        data = basic * 256 * 1024

        conn_sock.data['sent_byte'] += len(data)

        return data

    def complete_send(self, conn_sock, binary):
        if len(binary) < 48:
            if re.search(b'TEST_FINISH', binary):
                conn_sock.close()

                end_tm = datetime.now()

                tm_diff = end_tm - conn_sock.data['begin_tm']
                sending_time = round(tm_diff.total_seconds(), 3)

                Output.line('')
                Output.line('* RESULT '.ljust(80, '*'))
                Output.line('')

                total_mb = round(self.total_byte / (1024 * 1024), 1)

                Output.line('Total Mbytes: {} MB'.format(total_mb))
                Output.line('Total bytes: {} byte'.format(self.total_byte))
                Output.line('Sending time: {} s'.format(sending_time))
                Output.line('')

                Output.line('[Transfer speed]')

                byte_s = round(conn_sock.data['sent_byte'] / sending_time, 1)
                kb_s = round(byte_s / 1024, 1)
                mb_s = round(kb_s / 1024, 1)

                bps = round(byte_s * 8, 1)
                m_bps = round(bps / (1000 * 1000), 1)
                g_bps = round(m_bps / 1000, 2)

                Output.line('{} Byte/s'.format(byte_s))
                Output.line('{} KB/s'.format(kb_s))
                Output.line('{} MB/s'.format(mb_s))
                Output.line('')

                Output.line('{} bps'.format(bps))
                Output.line('{} Mbps'.format(m_bps))
                Output.line('{} Gbps'.format(g_bps))

                Output.line('')

                Output.line(''.ljust(80, '*'))
                Output.line('')


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
