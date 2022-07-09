#!/usr/bin/env python
# coding: utf-8

import sys, os

sys.path.insert(0, ".")

import ldogger.cmd

if __name__ == "__main__":
    name = os.path.basename(sys.argv[0]).replace("-linux-x86_64", "").replace("run-", "").replace(".py", "")
    getattr(ldogger.cmd, name)()
