#!/usr/bin/env python
# coding: utf-8

from ldogger.args import get_arg_parser


def test_reg_pats():
    ap = get_arg_parser()
    args = ap.process("--meta", "test1=1")

    assert hasattr(args, "meta") and args.meta == {"test1": 1}
