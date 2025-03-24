from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
import re

'''
HTTP forwarding HTML append.

Command:
$ python3 http_forwarding_html_append.py --info

http://develop-server:8000/
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args):
        args.http_forwarding = 'https://www.wikipedia.org/'

    def pre_http_forwarding_request(self, httpio, forwarding_url, req_headers):
        return forwarding_url

    def post_http_forwarding_request(self, httpio, forwarding_url, req_headers, res_headers, response, binary):
        if httpio.request_path == '/':
            # Content-length will be changed automatically.
            binary = re.sub(b'<main>', b'<main><div>This is sample message.</div>', binary)

        return binary


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
