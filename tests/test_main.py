import pytest
from unittest.mock import patch
from ipserver.__main__ import main
from ipserver.util.args_util import StdinLoader
import re
import sys
import io


class TestMain:
    def test_main(self, capsys, monkeypatch):
        monkeypatch.setattr(sys, 'argv', ['ipserver.py'])
        monkeypatch.setattr(sys, 'exit', lambda v: 0)

        with patch('ipserver.util.args_util.StdinLoader.read_stdin', return_value=[]):
            main()

            captured = capsys.readouterr()

            assert re.search(r'simple server', captured.out)
