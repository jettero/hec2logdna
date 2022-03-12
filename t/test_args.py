#!/usr/bin/env python
# coding: utf-8

from ldogger.args import get_arg_parser


def test_parse_args_and_process_first_pass():
    p = get_arg_parser()

    a0 = p.parse_args(["--meta", "test1=1"])
    a1 = p.process("--meta", "test1=1")

    assert hasattr(a0, "meta") and a0.meta == {"test1": 1}
    assert hasattr(a1, "meta") and a1.meta == {"test1": 1}

    d0 = a0.__dict__
    d1 = a1.__dict__
    assert d0 != d1
    del d0["tags"]
    del d1["tags"]
    assert d0 == d1


def test_process():
    p = get_arg_parser()

    a0 = p.process("--meta test1=1 --meta test2=2")
    assert a0.meta == {"test1": 1, "test2": 2}

    a1 = p.process("--meta test3=3")
    assert a1.meta == {"test1": 1, "test2": 2, "test3": 3}

    a2 = p.process("--meta test4=4")
    assert a2.meta == {"test1": 1, "test2": 2, "test4": 4}
