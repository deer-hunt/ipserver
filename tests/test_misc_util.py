import pytest

from ipserver.util.args_util import StrAction, ArgsHelper
import re


class TestStrAction:
    def test_method(self, mocker):
        namespace = mocker.Mock()
        namespace.abc = None

        strAction = StrAction(option_strings='', dest='abc')

        strAction({}, namespace, '\\\t')

        assert re.search(r'\t', namespace.abc)


class TestArgsHelper:
    def test_init_parser(self):
        argsHelper = ArgsHelper()

        arguments = {
            'abc': {'default': 'abc', 'type': None, 'help': 'Test.'}
        }

        parser, args = argsHelper.init_parser(arguments)

        assert args.abc == 'abc'
