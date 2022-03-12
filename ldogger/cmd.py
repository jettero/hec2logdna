#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import argparse
import shlex
import time

import rich.traceback

import ldogger.dispatch as d
from ldogger.tailer import Tailer
from ldogger.args import get_arg_parser


def send_message(args):
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
    rc = 0
    if not args.dry_run:
        if args.verbose:
            print("send_message()")
            dat = json.loads(res.data.decode())
            dat["http_status"] = f"{res.status} {res.reason}"
            print(" ", json.dumps(dat, indent=2).replace("\n", "\n  "))
        if not (200 <= res.status < 300):
            rc = res.status
    if args.noise_marks:
        if rc == 0:
            print(f"\x1b[32m.", end=" ")
        else:
            print(f"\x1b[31mxx", end=" ")
    return rc


def main(args):
    to = [Tailer("tail", "-n0", "-F", tname, verbose=args.verbose) for tname in args.tail]
    to += [Tailer(*cmd, verbose=args.verbose) for cmd in args.tail_shell_process]
    if to:
        while to:
            if args.verbose:
                print("main-loop-tick")
            for t in to:
                if line := t.get():
                    args.msg = [line]
                    rc = send_message(args)
            time.sleep(0.5 if args.verbose else 0.1)
            to = [t for t in to if not t.done]
        print()
    else:
        ec = send_message(args)
        print()
        sys.exit(ec)


def ldogger():
    """
    The entrypoint for the ldogger command
    """
    parser = get_arg_parser()
    args = parser.process()

    # This is a circular ref, but we should only do this once, so it probably
    # doesn't matter ... until it does.
    args.reprocess = parser.process

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
