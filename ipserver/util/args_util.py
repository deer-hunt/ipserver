import argparse
import json
import logging
import os
import select
import sys
from abc import ABC, abstractmethod
from distutils.util import strtobool
from logging import getLogger


class StrAction(argparse.Action):
    def __call__(self, parser, namespace, v, option_string=None):
        setattr(namespace, self.dest, v.replace('\\t', '\t'))


class ArgValidator(ABC):
    def __init__(self, debug=False):
        self.name = None

        self.debug = debug
        self.error = 'Argument value error.'

    def validate(self, args):
        try:
            r = self._validate(args)
        except Exception as e:
            if isinstance(e, argparse.ArgumentError) or self.debug:
                raise e
            else:
                raise self.arg_error(self.error)

        return r

    @abstractmethod
    def _validate(self, args):  # pragma: no cover
        return None

    def arg_error(self, msg):
        e = argparse.ArgumentError(None, msg)

        e.argument_name = '--' + self.name

        return e


class ArgsHelper:
    @staticmethod
    def init_parser(arguments, formatter_class=argparse.ArgumentDefaultsHelpFormatter, raw=False, group_names=None):
        parser = argparse.ArgumentParser(add_help=False, formatter_class=formatter_class)

        ArgsHelper.add_arguments(parser, arguments, [], raw=raw, group_names=group_names)

        args, unknown = parser.parse_known_args()

        return parser, args

    @staticmethod
    def add_arguments(parser, arguments, overrides, raw=False, group_names=None):
        groups = {}

        for arg, options in arguments.items():
            if raw:
                options = {'action': options['action']} if 'action' in options else {}

            if 'group' in options:
                group_key = options['group']

                if group_key not in groups:
                    name = group_names[group_key] if group_names is not None and group_key in group_names else group_key
                    target_parser = parser.add_argument_group(name)
                    groups[group_key] = target_parser
                else:
                    target_parser = groups[group_key]

                del options['group']
            else:
                target_parser = parser

            if arg in overrides:
                options['default'] = overrides[arg]

            if options.get('action') == 'StrAction':
                options['action'] = StrAction

            if 'type' in options and 'choices' not in options and 'metavar' not in options:
                options['metavar'] = ''

            if not options.get('nargs'):
                params = []

                format = '--{}'

                if 'shorten' in options:
                    if options['shorten'] is not True:
                        params.append(options['shorten'])
                    else:
                        format = '-{}'

                    del options['shorten']

                params.append(format.format(arg))

                target_parser.add_argument(*params, **options)
            else:
                target_parser.add_argument(arg, **options)

    @staticmethod
    def setup_logging(verbose, log):
        if verbose > 0:
            if verbose == 1:
                level = logging.ERROR
            elif verbose == 2:
                level = logging.INFO
            else:
                level = logging.DEBUG
        else:
            level = logging.CRITICAL

        opts = {
            'level': level,
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        }

        if log is None:
            opts['stream'] = sys.stdout
        else:
            opts['filename'] = log

        logging.basicConfig(**opts)

    @staticmethod
    def is_bool(v, strict=False):
        v = str(v).strip()

        try:
            if len(v) > 0 and strtobool(v):
                return True
        except Exception:
            if strict:
                return None

        return False


class StdinLoader:
    @staticmethod
    def read_stdin(timeout=2.0):
        r, _, _ = select.select([sys.stdin], [], [], timeout)

        if r:
            input_data = sys.stdin.read()
            lines = input_data.splitlines()
        else:
            lines = []

        return lines

    @staticmethod
    def load_env(name):
        error = False

        env = {}

        v = os.getenv(name)

        if v is not None and v != '':
            try:
                tv = json.loads(v)

                if type(env) is dict:
                    env = tv
                else:
                    error = True

            except Exception:
                getLogger(__name__).error('Env parse error.(' + name + ')')
                error = True

        if error:
            getLogger(__name__).info('Fail to load env.(' + name + ')')

        return env
