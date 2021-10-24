#!/usr/bin/env python
# coding: utf-8

import os
import time
import base64
import urllib3
import socket
import datetime

HTTP = urllib3.PoolManager()
HOSTNAME = socket.getfqdn()
ENDPOINT = "https://logs.logdna.com/logs"
MAX_CONTENT_BYTES = 1e5
MAX_READ = 500000


def gen_headers(content_type="application/json", charset="UTF-8"):
    token = os.environ.get("LOGDNA_TOKEN")
    if token.startswith("@"):
        with open(token[1:], "r") as fh:
            token = fh.read()
    if not token:
        raise Exception("LOGDNA_TOKEN environment variable is required, but unset")
    btok = base64.b64encode(token.encode()).decode()
    return {
        "Authorization": f"Basic {btok}",
        "Content-Type": f"{content_type}; charset={charset}",
    }


def gen_url(endpoint=ENDPOINT, tags=None, hostname=HOSTNAME, now=None):
    if isinstance(now, datetime.datetime):
        now = int(now.timestamp())
    elif now is None:
        now = int(time.time())
    elif not isinstance(now, int):
        now = int(now)
    if tags is not None:
        if not isinstance(tags, (list, tuple)):
            tags = [tags]
    url = endpoint
    args = [f"hostname={hostname}", f"now={now}"]
    if tags:
        args.append(f"tags={','.join(tags)}")
    return f"{endpoint}?{'&'.join(args)}"


def send(dat, hostname=HOSTNAME, tags=None, now=None):
    headers = gen_headers()
    url = gen_url(hostname=hostname, tags=tags, now=now)
    res = HTTP.request("POST", url, body=dat, headers=headers)
