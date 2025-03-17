import pprint
import logging
import os
import sys
import platform


class AppException(Exception):
    pass


class System:
    @classmethod
    def get_python_ver(cls):
        major = sys.version_info.major
        minor = sys.version_info.minor

        return float(major) + minor / 10

    @classmethod
    def verify_os(cls, windows=False, macos=False, linux=False):
        os_name = platform.system()

        if windows and os_name == 'Windows':
            return True

        if macos and os_name == 'Darwin':
            return True

        if linux and os_name == 'Linux':
            return True

        return False

    @classmethod
    def load_module(cls, name):
        module = None

        try:
            module = __import__(name)
        except ImportError:
            pass

        return module

    @classmethod
    def exit(cls, msg, error=False):
        if error is False:
            Output.line(msg)
        else:
            Output.warn(msg)

        os._exit(error)


class Output:
    @classmethod
    def is_logging(cls, min_level=logging.INFO):
        level = cls.get_log_level()

        if level > 0 and level <= min_level:
            return True

        return False

    @classmethod
    def get_log_level(cls):
        logger = logging.getLogger()
        level = logger.getEffectiveLevel()

        return level

    @classmethod
    def get_formatted_data(cls, data, indent=2):
        return pprint.pformat(data, indent=indent)

    @classmethod
    def line(cls, msg):
        print(msg, flush=True)

    @classmethod
    def warn(cls, msg):
        print('\033[33m' + msg + '\033[0m', flush=True)

    @classmethod
    def info(cls, msg):
        print('\033[32m' + msg + '\033[0m', flush=True)
