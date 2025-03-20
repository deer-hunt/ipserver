from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd
import re
import random

'''
HTTP forwarding, Change request header. Set random Accept-Language.

Command:
# python3 http_forwarding_change_header.py --port=8002

http://develop-server:8002/
'''


class MyPipeline(Pipeline):
    def pre_configure(self, args, conf_args):
        args.http_forwarding = 'https://support.google.com/youtube/'

    def pre_http_forwarding_request(self, httpio, forwarding_url, req_headers):
        langs = ['ko-KR', 'en-US', 'zh-CN', 'zh-Hans', 'fr-FR', 'ar-eg', 'de-CH', 'ja']

        lang = random.choice(langs)

        req_headers.replace_header('Accept-Language', lang)

        print(req_headers)
        return forwarding_url

    def post_http_forwarding_request(self, httpio, forwarding_url, req_headers, res_headers, response, binary):
        return binary


class MyObjectFactory(ObjectFactory):
    def create_pipeline(self):
        return MyPipeline()


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
