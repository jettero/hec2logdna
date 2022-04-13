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
from ldogger.args import get_ldogger_arg_parser, get_sj2l_arg_parser
from ldogger.decoder import decode_journald_json


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
        mark = "32mo" if rc == 0 else "31mx"
        print(f"\x1b[{mark}", end="")
        sys.stdout.flush()
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
                    templates = list()
                    for rt in args.regex_template:
                        if m := rt.pat.search(line):
                            gd = m.groupdict()
                            templates.extend([x.format(**gd) for x in rt.args])
                    rc = send_message(args.reprocess(*templates) if templates else args)
            time.sleep(0.5 if args.verbose else 0.1)
            to = [t for t in to if not t.done]
        print()
    else:
        ec = send_message(args)
        print()
        sys.exit(ec)


def ldogger(*args):
    """
    The entrypoint for the ldogger command
    """
    args = get_ldogger_arg_parser().process(*args)

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


def just_tail_journalctl(args):
    if args.only_n < 1:
        t = Tailer("journalctl", "-o", "json", "-fn0")
    else:
        t = Tailer("journalctl", "-o", "json", f"-n{args.only_n}")

    while not t.done:
        while line := t.get():
            decode_journald_json(args, line)
            send_message(args)
        time.sleep(0.5 if args.verbose else 0.1)
    print()


def sj2l(*args):
    """
    The entrypoint for the systemd-journald to logdna command
    """

    args = get_sj2l_arg_parser().process(*args)

    try:

        def recognize_me(x):
            if "sj2l" in x:
                return False
            if "ldogger" in x:
                return False
            if "/logdna/logdna/" in x:
                return False
            return True

        rich.traceback.install(width=119, show_locals=True, suppress=[recognize_me])
        just_tail_journalctl(args)
        sys.exit(0)

    except KeyboardInterrupt:
        pass
