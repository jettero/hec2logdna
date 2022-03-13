#!/usr/bin/env python
# coding: utf-8

import re
import sys
import shlex
import argparse
from collections import namedtuple
from ldogger.dispatch import HOSTNAME

RT = namedtuple("RT", ["pat", "args"])


class TV(argparse.Action):
    def __call__(self, parser, namespace, tv, opiton_string=None):
        nv = getattr(namespace, self.dest)
        nv.update(set([x.strip() for x in tv.split(",") if x]))


class KV(argparse.Action):
    shell_parsing = False

    def __call__(self, parser, namespace, kv, opiton_string=None):
        nv = getattr(namespace, self.dest)
        try:
            if self.shell_parsing:
                k, *v = shlex.split(kv, posix=False)
            else:
                k, v = kv.split("=")
                # we really want v to always be a string, or logdna will get
                # confused about the meta field types eventually.
                #
                # try:
                #     nv[k] = int(v)
                # except:
                #     try:
                #         nv[k] = float(v)
                #     except:
                #         nv[k] = str(v)
        except Exception as e:
            raise Exception(f"{kv} not understood, should be key=value format: {e}")


class SKV(KV):
    shell_parsing = True


def get_arg_parser():
    parser = argparse.ArgumentParser(
        description="""
        ldogger — logdna + logger => ldogger

        The purpose of this app is to send logs to app.logdna.com.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-p",
        "--tail-shell-process",
        nargs="*",
        action="append",
        default=list(),
        help="""tail shell commands.
        Arguments are washed through shlex.split(posix=False) and joined as a single flat list.
        `-p "ps auxfw"` comes out the same as `-p ps auxfw` => `["ps", "auxfw"]`.
        """,
    )

    parser.add_argument(
        "-t",
        "--tail",
        nargs="*",
        type=str,
        default=list(),
        help="""tail logfiles. (If -t is specified, any msg values are assumed
        to be filenames for tailing as well.)""",
    )

    parser.add_argument("msg", nargs="*", type=str, help="words to put in the 'line' field")

    parser.add_argument(
        "-n",
        "--noise-marks",
        action="store_true",
        help="""
    if not in verbose mode, print green '.'s for send_message() successes and
    red 'x's for send_message() errors. -n is forced true when outputting to a
    console and forced to false when in verbose mode.
    """,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="please tell me about internal things now")
    parser.add_argument(
        "-d", "--dry-run", action="store_true", help="don't actually send, just turn on verbose and print things"
    )

    parser.add_argument(
        "--grok-args", action="store_true", help="process switches and config files, report the results, and exit"
    )
    parser.add_argument(
        "-r",
        "--regex-template",
        type=str,
        default=[],
        action="append",
        help=r"""
        Add a regex pattern that adds tags, meta, app, or level arguments to
        the line.  Note that -r takes a single string and splits it with shell
        parsing rules (shlex.split(posix=False)).

        If matched,
            `-r '"(?P<aaa>aaa)...(?P<bbb>bbb)" --meta aaa={aaa} --meta bbb={bbb}'`
        this regex will make the log entry seem as if it had --meta aaa=aaa --meta bbb=bbb
        switches given on the command line.

        And this,
            `-r "'(?P<app>\w+)\[(?P<pid>\d+)\]' --app {app} --meta pid={pid}"`
        will be as iff `--app MATCHED --meta pid=01234` was added.
        """,
    )

    # XXX: Should --ip and --hostname be macroable? I definitley think not.
    # They should be statically reported by the host sending the log lines ...
    # right? right?  OTOH, what about hosts that process logs for other hosts
    # (e.g., syslog forwarding). Let's figure this out later if we need it.

    parser.add_argument("--ip", type=str, help="ip address, one of the base fields")
    parser.add_argument(
        "-H", "--hostname", type=str, default=HOSTNAME, help="a required base field, hostname for the hostname field"
    )

    _add_macroables(parser)

    # bind _process_arguments to parser
    parser.process = _process_arguments.__get__(parser)

    return parser


def _add_macroables(parser):
    parser.add_argument(
        "-m",
        "--meta",
        type=str,
        default={},
        metavar="key=val",
        action=KV,
        help="key value pairs for the meta field",
    )
    parser.add_argument("--tags", type=str, default=set(), action=TV, help="a comma separated list of tags")
    parser.add_argument("--mac", type=str, help="mac address, one of the base fields")
    parser.add_argument("--app", default="ldogger", type=str, help="another base field, the name of the app")
    parser.add_argument("--level", default="info", choices="trace debug info warning error critical".split())
    return parser


def _reprocess_arguments(namespace, *args):
    args = _special_pre_processing(args)
    parser = argparse.ArgumentParser(add_help=False)
    _add_macroables(parser)
    ns = argparse.Namespace(**namespace.as_dict())
    ns.meta = dict(ns.meta)  # copy
    ns.tags = set(ns.tags)  # copy
    args = parser.parse_args(args, namespace=ns)
    add_other_janky_instance_methods(args)
    return args


def _special_pre_processing(args):
    # convenience thing to avoid this horrible syntax
    # args.process(*("--meta test1=1".split()))
    if len(args) == 1 and isinstance(args[0], str) and " " in args[0]:
        return shlex.split(args[0], posix=False)
    return args


def add_other_janky_instance_methods(args):
    # this raw uncooked jank is to fix the way we just broke __repr__ in
    # _AttributeHolder
    okwa = args._get_kwargs

    def our_kwargs(self):
        return [x for x in okwa() if not callable(x[1])]

    args._get_kwargs = our_kwargs.__get__(args)

    # This is mainly used as a convenience in t/test_args.py
    # … hopefully anway, cuz it's pretty janky
    def as_dict(self):
        def cp(v):
            try:
                return v.copy()
            except:
                pass
            return v

        return {k: cp(v) for k, v in self._get_kwargs()}

    args.as_dict = as_dict.__get__(args)


def _process_arguments(parser, *args):  # aka def process()
    args = _special_pre_processing(args)
    args = parser.parse_args(args) if args else parser.parse_args()  # passing empty args still ignores sys.argv

    def flatten(x):
        def _f(x):
            for w in x:
                yield from shlex.split(w, posix=False)

        return list(_f(x))

    args.tail_shell_process = [flatten(x) for x in args.tail_shell_process]

    if args.dry_run:
        args.verbose = True

    if args.tail:
        args.tail += args.msg
        args.msg = list()

    def split_regex_templates(x):
        for item in x:
            pat, *args = shlex.split(item, posix=False)
            compiled_re = re.compile(pat)
            yield RT(compiled_re, args)

    args.regex_template = list(split_regex_templates(args.regex_template))

    if args.verbose:
        args.noise_marks = False

    elif sys.stdout.isatty():
        args.noise_marks = True

    if args.grok_args:
        import json

        def encode_helper(o):
            if isinstance(o, re.Pattern):
                return o.pattern
            return o

        print("args:", json.dumps(args.__dict__, default=encode_helper, indent=2))
        sys.exit(0)

    # bind our namespace to the reprocessor
    args.reprocess = _reprocess_arguments.__get__(args)

    # do this for a few more silly callables
    add_other_janky_instance_methods(args)

    return args
