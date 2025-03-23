import argparse
import ipaddress
import json
import re
import ssl
import sys
from logging import getLogger

from ipserver.configs import Constant
from ipserver.core.pipeline import Pipeline
from ipserver.util.args_util import ArgsHelper
from ipserver.util.sys_util import AppException
from ipserver.util.sys_util import Output


class ArgsBuilder:
    def __init__(self, config, pipeline):
        self.config = config
        self.pipeline = pipeline  # type: Pipeline

    def parse(self):
        arguments = self.config.ARGUMENTS

        _, rawargs = ArgsHelper.init_parser(arguments, raw=True)

        conf_args = self._load_conf(rawargs.conf) if rawargs.conf else {}

        self.pipeline.init_configure(arguments, conf_args)

        parser = self._create_parser()

        self._add_arguments(parser, arguments, conf_args)

        args = parser.parse_args()

        self._setup_logging(args)

        self.pipeline.pre_configure(args)

        self._configure(parser, args, rawargs)

        self.pipeline.post_configure(args)

        return (args, parser)

    def _add_arguments(self, parser, arguments, conf_args):
        ArgsHelper.add_arguments(parser, arguments, conf_args, group_names=self.config.ARGUMENTS_GROUP_NAMES)

    def _load_conf(self, conf):
        if ArgsHelper.is_bool(conf):
            conf = Constant.CONF_FILE

        conf_args = {}

        try:
            with open(conf, 'r', encoding='utf-8') as file:
                conf_args = json.load(file)
        except Exception:
            raise AppException('Fail to load conf.({})'.format(conf))

        getLogger(__name__).info('CONF_VARS(' + conf + '):\n' + Output.get_formatted_data(conf_args))

        return conf_args

    def _create_parser(self):
        parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        desc = self._create_bottom_desc()

        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, parents=[parser], description=Constant.APP_DESCRIPTION, epilog=desc)

        return parser

    def _setup_logging(self, args):
        if args.info:
            args.verbose = 2

        if args.debug:
            args.verbose = 3

        if args.log is not None:
            if args.verbose == 0:
                args.verbose = 2

        ArgsHelper.setup_logging(args.verbose, args.log)

        if args.verbose > 0:
            getLogger(__name__).info('VERBOSE_LEVEL: ' + str(args.verbose) + ' [1:TRACE_ERROR, 2:INFO, 3:DEBUG]')

        if args.log is not None:
            getLogger(__name__).info('ENABLE_LOG: ' + args.log)

    def _configure(self, parser, args, rawargs):
        self._assign_shorten_option(args)

        if Output.is_logging():
            self._logging_args(args)

        self._fix_args(parser, args)

        self._validate_args(parser, args, rawargs)

    def _create_bottom_desc(self):
        desc = ''

        desc += Constant.APP_BOTTOM_DESC + "\n"

        return desc

    def _assign_shorten_option(self, args):
        if args.http_app:
            args.mode = Constant.MODE_HTTP if args.mode != Constant.MODE_HTTPS else Constant.MODE_HTTPS
            args.http_opt = Constant.HTTP_APP

            if not ArgsHelper.is_bool(args.http_app):
                args.http_path = args.http_app
        elif args.http_file_upload:
            args.mode = Constant.MODE_HTTP if args.mode != Constant.MODE_HTTPS else Constant.MODE_HTTPS
            args.http_opt = Constant.HTTP_FILE

            if ArgsHelper.is_bool(args.http_file_upload):
                args.enable_file_upload = 1
            elif args.http_file_upload == '2':
                args.enable_file_upload = 2
            else:
                args.http_path = args.http_file_upload
                args.enable_file_upload = 1

        elif args.http_file:
            args.mode = Constant.MODE_HTTP if args.mode != Constant.MODE_HTTPS else Constant.MODE_HTTPS
            args.http_opt = Constant.HTTP_FILE

            if not ArgsHelper.is_bool(args.http_file):
                args.http_path = args.http_file
        elif args.http_forwarding:
            args.mode = Constant.MODE_HTTP if args.mode != Constant.MODE_HTTPS else Constant.MODE_HTTPS
            args.http_opt = Constant.HTTP_FORWARDING

            if not ArgsHelper.is_bool(args.http_forwarding):
                args.forwarding = args.http_forwarding

    def _fix_args(self, parser, args):
        try:
            args.fixed_output_target = self._fix_output_target(args)
            args.fixed_ssl_context = self._fix_ssl_context(args)
            args.fixed_restrict_allow = self._fix_restrict_ips(args.restrict_allow)
            args.fixed_restrict_deny = self._fix_restrict_ips(args.restrict_deny)
        except Exception as e:
            getLogger(__name__).debug('Fix arguments error.', exc_info=True)

            parser.error(e)

    def _fix_output_target(self, args):
        v = Constant.DIRECTION_SEND | Constant.DIRECTION_RECEIVE

        if args.output_target == 'SEND':
            v = Constant.DIRECTION_SEND
        elif args.output_target == 'RECEIVE':
            v = Constant.DIRECTION_RECEIVE

        return v

    def _fix_ssl_context(self, args):
        if not args.ssl_context:
            ssl_context = None
        else:
            k = args.ssl_context.lower()

            if k in Constant.SSL_CONTEXTS:
                ssl_context = getattr(ssl, Constant.SSL_CONTEXTS[k], None)

                if ssl_context is None:
                    raise Exception('Not support SSL context.')
            else:
                raise Exception('Unknown SSL context.')

        return ssl_context

    def _fix_restrict_ips(self, v):
        ips = []

        if v is not None:
            entries = re.split(r'[;,]+', v)

            for entry in entries:
                entry = entry.strip()

                if entry:
                    try:
                        if '/' in entry:
                            ips.append(ipaddress.ip_network(entry))
                        else:
                            ips.append(ipaddress.ip_network(entry + '/32'))
                    except ValueError:
                        getLogger(__name__).error('Restrict ip format error.({})'.format(entry))

                        raise AppException('Restrict ip format error({})'.format(entry))

        return ips

    def _validate_args(self, parser, args, rawargs):
        if args.version or len(sys.argv) == 1:
            return

        mode = args.mode

        if args.port <= 0:
            parser.error('`--port` is required in `{}` mode.'.format(mode))

        if mode != Constant.MODE_SSL:
            self._validate_options_by_mode(mode, parser, rawargs, Constant.SSL_OPTIONS)

        if mode in Constant.HTTP_MODES:
            if args.http_opt != Constant.HTTP_FILE and args.enable_file_upload:
                parser.error('`--enable_file_upload` is available with --http_opt=FILE option.')

            if rawargs.output is None:
                args.output = Constant.OUTPUT_NONE
        else:
            self._validate_options_by_mode(mode, parser, rawargs, Constant.HTTP_OPTIONS)

        if args.enable_file_upload > 0 and rawargs.output is None:
            args.output = Constant.OUTPUT_NONE
            getLogger(__name__).info('Change --output option to `NONE` because --enable_file_upload option is enabled.')

    def _validate_options_by_mode(self, mode, parser, args, non_options):
        non_supports = []

        for key in non_options:
            if getattr(args, key):
                non_supports.append(key)

        if len(non_supports) > 0:
            msg = ', '.join(['`--' + key + '`' for key in non_supports])
            msg += ' option is not supported in `{}` mode.'.format(mode)
            parser.error(msg)

    def _logging_args(self, args):
        params = vars(args)

        getLogger(__name__).info('ARGUMENTS:\n' + Output.get_formatted_data(params))

        v = json.dumps(params, ensure_ascii=False)

        getLogger(__name__).info('ARGUMENTS_JSON:\n' + v)
