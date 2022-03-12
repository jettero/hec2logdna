#!/usr/bin/env python
# coding: utf-8

import sys
import shlex
import argparse
from ldogger.dispatch import HOSTNAME


def get_arg_parser():
    """
    Get the argparse.ArgumentParser object with the special .process() wrapper -- e.g.:

        parser = get_arg_parser()
        args_o = parser.process('--meta', 'neat=stuff')
        args_s = parser.process('--meta', 'moar=stuff')

    Note that args.process() has some special behavior:

    The first call to args.process() stores/caches the args (either given or
    from sys.argv[1:].  The resulting argparse.Namespace object is based on
    those arguments.

    Subsequent calls produce a new Namespace object based on whatever new args
    are received merged with the previous arguments.

    This allows for some switches to be added/learned/discovered after the
    initial processing (useful for --regex-template processing, which is
    per-input-line switch parsing/generation).
    """
    parser = argparse.ArgumentParser(
        description="""
        ldogger — logdna + logger => ldogger

        The purpose of this app is to send logs to app.logdna.com.

        It has:
          log tail modes that track positions to avoid dups in re-processing,
          TODO: regexp systems to produce metadata fields,
          TODO: probably other features we forgot to mention here.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    class KV(argparse.Action):
        shell_parsing = False

        def __call__(self, parser, namespace, kv, opiton_string=None):
            nv = getattr(namespace, self.dest)
            try:
                if self.shell_parsing:
                    k, *v = shlex.split(kv)
                else:
                    k, v = kv.split("=")
                    try:
                        nv[k] = int(v)
                    except:
                        try:
                            nv[k] = float(v)
                        except:
                            nv[k] = str(v)
            except Exception as e:
                raise Exception(f"{kv} not understood, should be key=value format: {e}")

    class SKV(KV):
        shell_parsing = True

    parser.add_argument(
        "-p",
        "--tail-shell-process",
        nargs="*",
        action="append",
        default=list(),
        help="""tail shell commands.
        Arguments are washed through shlex.split() and joined as a single flat list.
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
        "-m",
        "--meta",
        type=str,
        default={},
        metavar="key=val",
        action=SKV,
        help="key value pairs for the meta field",
    )
    parser.add_argument(
        "-r",
        "--regex-template",
        type=str,
        default={},
        action=KV,
        help="""
        Add a regex pattern that adds tags, meta, app, or level arguments to the line.

        If matched,
            `-r '"(?P<aaa>aaa)...(?P<bbb>bbb)" --meta aaa={aaa} --meta bbb={bbb}'`
        this regex will make the log entry seem as if it had --meta aaa=aaa --meta bbb=bbb
        switches given on the command line.

        And this,
            `-r "'(?P<app>\w+)\[(?P<pid>\d+)\]' --app {app} --meta pid={pid}"`
        will be as iff `--app MATCHED --meta pid=01234` was added.
        """,
    )
    parser.add_argument("--tags", type=str, default="", help="a comma separated list of tags")
    parser.add_argument("--ip", type=str, help="ip address, one of the base fields")
    parser.add_argument("--mac", type=str, help="mac address, one of the base fields")
    parser.add_argument("--app", default="ldogger", type=str, help="another base field, the name of the app")
    parser.add_argument("--level", default="info", choices="trace debug info warning error critical".split())
    parser.add_argument(
        "-H", "--hostname", type=str, default=HOSTNAME, help="a required base field, hostname for the hostname field"
    )

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

    # bind _process_arguments to parser
    parser.process = _process_arguments.__get__(parser)

    return parser


def _process_arguments(parser, *args, initial=False):
    # This is the first time we're in here if it's the first time or someone
    # says we shold pretend it is.
    if not hasattr(parser, "oargs"):
        initial = True

    # This is a little weird …
    if initial:
        # The first time we call parser.process() we establish the "original args"
        parser.oargs = args = list(args or sys.argv[1:])
    else:
        # On subsequent calls, we append the new args to the oargs (but not permanently)
        args = parser.oargs + args

    # we do the above so we can do things like
    # args = parser.process() to process sys.argv
    # then later learn we have to add additional arguments via the -r templates (or whatever)
    # so we need to be able to say: but our actual arguments are:
    # args = parser.process("--new", "shit", "for", "this", "line", "only")

    args = parser.parse_args(args)

    # XXX: But now we have to reprocess EVERYTHING for each input line? Is this
    # really a good idea?  are we overcomitting to these --regex-templates?
    #
    # We try to skip certain things below, but probably what we really need is
    # a smaller argparser for the subsequent runs that only accepts --meta and
    # --app and things.
    #
    # Maybe we can multiple inheritence the instances together or something? Is
    # that a thing? merging Namespace instances via some kind of dumb
    # inheritence trick? I rather doubt it …
    #
    # I know what I need to do, but I don't know if I have the syntax to do it.
    #  - kylo

    args.tags = [x.strip() for x in args.tags.split(",")]
    args.tags = [x for x in args.tags if x]

    def flatten(x):
        def _f(x):
            for w in x:
                yield from shlex.split(w)

        return list(_f(x))

    args.tail_shell_process = [flatten(x) for x in args.tail_shell_process]

    if initial:
        if args.dry_run:
            args.verbose = True

        if args.tail:
            args.tail += args.msg
            args.msg = list()

        if args.grok_args:
            import json

            print("args:", json.dumps(args.__dict__, indent=2))
            print("\nconfig: TODO")
            sys.exit(0)

        if args.verbose:
            args.noise_marks = False

        elif sys.stdout.isatty():
            args.noise_marks = True

    return args
