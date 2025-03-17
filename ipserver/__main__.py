from ipserver.core.object_factory import ObjectFactory
from ipserver.ipserver_cmd import IpServerCmd


def main():
    factory = ObjectFactory()

    ips_cap_cmd = IpServerCmd(factory)

    ips_cap_cmd.run()


if __name__ == '__main__':
    main()
