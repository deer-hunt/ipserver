from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd

import re

'''
Pipeline customize.

Specification:
- Customizing Pipeline class.
- Creating ObjectFactory class.

Command:
$ python3 pipeline_customize.py --info
$ telnet localhost 8000
'''


class MyPipeline(Pipeline):
    def post_accept(self, conn_sock, conn_bucket):
        print('conn_id', conn_sock.conn_id)

        print('size:', len(conn_bucket.conn_socks))

    def complete_receive(self, conn_sock, binary):
        print('This is receive data.')
        print(binary, '\n')

        return binary

    def pre_send(self, conn_sock, binary):
        print('This is pre-send data.')
        print(binary, '\n')
        return binary


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
