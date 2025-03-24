from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
import re

'''
TCP forwarding change data.

Command:
$ python3 tcp_forwarding_change_data.py --port=8002

http://develop-server:8002/

http://www.columbia.edu/~fdc/sample.html
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args):
        args.forwarding = 'tcp://www.columbia.edu:80'

    def pre_forwarding_send(self, conn_sock, binary):
        binary = re.sub(b'GET /.*? HTTP/1.1', b'GET /~fdc/sample.html HTTP/1.1', binary)
        binary = re.sub(b'Host: .+[\r\n]+', b'Host: www.columbia.edu\r\n', binary)
        binary = re.sub(b'Accept-Encoding: .+[\r\n]+', b'\r\n', binary)

        return binary

    def post_forwarding_receive(self, conn_sock, binary):
        binary = re.sub(b'HTML tutorial', b'HTML[CHANGED]', binary)

        return binary


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
