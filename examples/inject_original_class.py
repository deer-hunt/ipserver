from ipserver.core.object_factory import ObjectFactory
from ipserver.core.pipeline import Pipeline
from ipserver.ipserver_cmd import IpServerCmd

import re

'''
Injecting original class.

Specification:
- Customizing Pipeline class object.

Command:
$ python3 inject_original_class.py --info

http://localhost:8000/
'''


# Original class
class ClassObject():
    def show(self):
        print('This is EntityObject')


class InjectionObject():
    def show(self):
        print('This is InjectionObject')


class MyPipeline(Pipeline):
    def __init__(self, injection_object):
        super().__init__()

        self.class_object = ClassObject()
        self.injection_object = injection_object

    def initialize(self, config, socket_server):
        print('This is original message. Initialized.\n')

    def complete(self):
        print('')
        print('This is original message. Complete.\n')

        self.class_object.show()
        self.injection_object.show()


class MyObjectFactory(ObjectFactory):
    def __init__(self, injection_object):
        self.injection_object = injection_object

    def create_pipeline(self):
        return MyPipeline(self.injection_object)


if __name__ == '__main__':
    injection_object = InjectionObject()

    factory = MyObjectFactory(injection_object)

    cmd = IpServerCmd(factory)

    cmd.run()
