from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
from datetime import datetime
import re

'''
The forwarding protocol is SSL, however the listening protocol is not SSL. So you can debug the transmission data in detail.

# python3 tcp_forwarding_ssl_protocol.py --port=8000
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args):
        args.output_target = 'ALL'
        args.forwarding = 'ssl://wikipedia.org:443'

    def pre_forwarding_send(self, conn_sock, binary):
        binary = re.sub(b'Host: .+[\r\n]+', b'Host: www.wikipedia.org\r\n', binary)

        return binary

    def post_forwarding_receive(self, conn_sock, binary):
        return binary

    def pre_send(self, conn_sock, binary):
        return binary


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
