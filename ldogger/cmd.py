#!/usr/bin/env python
# coding: utf-8

import sys
import json, yaml
import argparse
import ldogger.dispatch as d
import rich.traceback


def main(args):
    line = " ".join(args.msg)
    res = d.send(
        line,
        hostname=args.hostname,
        tags=args.tags,
        app=args.app,
        level=args.level,
        mac=args.mac,
        ip=args.ip,
        verbose=args.verbose,
        dry_run=args.dry_run,
        **args.meta,
    )
    if not args.dry_run:
        dat = json.loads(res.data.decode())
        dat["http_status"] = res.status
        print(yaml.dump(dat))


def ldogger():
    """
    The entrypoint for the ldogger command
    """
    parser = argparse.ArgumentParser(
        description="""
        ldogger — logdna + logger => ldogger

        The purpose of this app is to send logs to app.logdna.com.

        It has:
          log tail modes that track positions to avoid dups in re-processing,
          regexp systems to produce metadata fields,
          probably other features we forgot to mention here.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    class KV(argparse.Action):
        def __call__(self, parser, namespace, values, opiton_string=None):
            nv = getattr(namespace, self.dest)
            for i in values:
                try:
                    k, v = i.split("=")
                    try:
                        nv[k] = int(v)
                    except:
                        try:
                            nv[k] = float(v)
                        except:
                            nv[k] = str(v)
                except Exception as e:
                    raise Exception(f"{i} not understood, should be key=value format: {e}")

    parser.add_argument("msg", nargs="*", type=str, help="words to put in the 'line' field")
    parser.add_argument(
        "-m",
        "--meta",
        type=str,
        default={},
        metavar="key=value",
        nargs="+",
        action=KV,
        help="key value pairs for the meta field",
    )
    parser.add_argument("--tags", type=str, help="a comma separated list of tags")
    parser.add_argument("--ip", type=str, help="ip address, one of the base fields")
    parser.add_argument("--mac", type=str, help="mac address, one of the base fields")
    parser.add_argument("--app", default="ldogger", type=str, help="another base field, the name of the app")
    parser.add_argument("--level", default="info", choices="trace debug info warning error critical".split())
    parser.add_argument(
        "-H", "--hostname", type=str, default=d.HOSTNAME, help="a required base field, hostname for the hostname field"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="please tell me about internal things now")
    parser.add_argument(
        "-d", "--dry-run", action="store_true", help="don't actually send, just turn on verbose and print things"
    )

    args = parser.parse_args()

    args.tags = [x.strip() for x in args.tags.split(",")]

    if args.dry_run:
        args.verbose = True

    try:

        def recognize_me(x):
            if "ldogger" in x:
                return False
            if "/logdna/logdna/" in x:
                return False
            return True

        rich.traceback.install(width=119, show_locals=True, suppress=[recognize_me])
        main(args)
        sys.exit(0)

    except KeyboardInterrupt:
        pass