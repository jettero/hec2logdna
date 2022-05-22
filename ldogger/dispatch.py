#!/usr/bin/env python
# coding: utf-8

import os
import json
import time
import base64
import urllib3
import socket
import datetime

HTTP = urllib3.PoolManager()
HOSTNAME = socket.getfqdn()
ENDPOINT = "https://logs.logdna.com/logs/ingest"
MAX_CONTENT_BYTES = 1e5
MAX_READ = 500000


def gen_headers(content_type="application/json", charset="UTF-8", verbose=False):
    token = os.environ.get("LOGDNA_TOKEN", "")
    if token.startswith("@"):
        with open(token[1:], "r") as fh:
            token = fh.read()
    if not token:
        raise Exception("LOGDNA_TOKEN environment variable is required, but unset")
    btok = base64.b64encode(token.encode()).decode()
    if verbose:
        print("gen_headers():")
        print(f"  - token: {token[0:3]}…{token[-3:]}")
        print(f"  - Authorization: Basic {btok[0:3]}…{btok[-3:]}")
        print(f"  - Content-Type: {content_type}; charset={charset}")
    return {
        "Authorization": f"Basic {btok}",
        "Content-Type": f"{content_type}; charset={charset}",
    }


def gen_url(endpoint=ENDPOINT, tags=None, hostname=HOSTNAME, now=None, mac=None, ip=None, verbose=False):
    if verbose:
        print(f"gen_url():")
    if isinstance(now, datetime.datetime):
        now = int(now.timestamp())
    elif now is None:
        now = int(time.time())
    elif not isinstance(now, int):
        now = int(now)
    if verbose:
        print(f"  - computed now={now}")
    url = endpoint
    if verbose:
        print(f"  - starting with endpoint={endpoint}")
    args = [f"hostname={hostname}"]
    if mac:
        args.append(f"mac={mac}")
    if ip:
        args.append(f"ip={ip}")
    if tags:
        args.append(f"tags={','.join(sorted(tags))}")
    args.append(f"now={now}")
    if verbose:
        for arg in args:
            print(f"  - appended {arg}")
    return f"{endpoint}?{'&'.join(args)}"


def send(
    *lines,
    hostname=HOSTNAME,
    level=None,
    app=None,
    tags=None,
    now=None,
    mac=None,
    ip=None,
    env=None,
    verbose=False,
    dry_run=False,
    **meta,
):
    lines = [x for x in lines if x]
    if not lines:
        lines = ["NOP"]
    headers = gen_headers(verbose=verbose)
    url = gen_url(hostname=hostname, tags=tags, now=now, mac=mac, ip=ip, verbose=verbose)
    llines = list()
    for line in lines:
        l = dict(line=line)
        llines.append(l)
        if level is not None:
            l["level"] = level.upper()
        if app is not None:
            l["app"] = app
        if env is not None:
            l["env"] = env
        if meta:
            l["meta"] = meta
    msg = {"lines": llines}
    if dry_run or verbose:
        print(f"send() to {url}")
        print("  " + json.dumps(msg, indent=2).replace("\n", "\n  "))
    msg = json.dumps(msg).encode()
    if dry_run:
        return msg
    return HTTP.request("POST", url, body=msg, headers=headers)
