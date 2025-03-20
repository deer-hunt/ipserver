from ipserver.core.object_factory import ObjectFactory
from ipserver.configs import Config

from ipserver.ipserver_cmd import IpServerCmd


'''
Customizing Config class.

Specification:
- Customizing Config class.
- Creating ObjectFactory class.

Command:
# python3 config_customize.py --info
# telnet localhost 8000
'''


class MyObjectFactory(ObjectFactory):
    def get_config(self):
        Config.ARGUMENTS['timeout']['default'] = 120
        Config.ARGUMENTS['dumpfile']['default'] = True

        return Config


if __name__ == '__main__':
    factory = MyObjectFactory()

    cmd = IpServerCmd(factory)

    cmd.run()
