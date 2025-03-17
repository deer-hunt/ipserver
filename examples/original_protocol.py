from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
import re

'''
Original protocol - Calculation protocol

# python3 original_protocol.py --port=8002

Example:
----
Welcome to Calculation protocol.

4+6
ANSWER: 10

8*5+4+5*5
ANSWER: 69

9+1
ANSWER: 10

k=1
ANSWER: ERROR

8/5
ANSWER: 1.6
'''


class MyPipeline(Pipeline):
    def post_accept(self, conn_sock, conn_bucket):
        response = '\nWelcome to Calculation protocol.\n\n'

        conn_sock.send_queue(response.encode())

    def post_receive(self, conn_sock, binary):
        command = binary.decode().strip()

        if command:
            v = self._calc(command)
            response = 'ANSWER: ' + str(v) + '\n\n'
            conn_sock.send_queue(response.encode())

        return binary

    def _calc(self, command):
        v = ''

        try:
            if not re.search(r'^[ \d+\-*%/]+$', command):
                raise Exception()

            v = eval(command)
        except Exception:
            v = 'ERROR'

        return v

    def pre_send(self, conn_sock, binary):

        return binary


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
