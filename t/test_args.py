#!/usr/bin/env python
# coding: utf-8

import pytest
from ldogger.args import get_arg_parser


def test_parse_args_and_process_first_pass():
    p = get_arg_parser()

    a0 = p.parse_args(["--meta", "test1=1"])
    a1 = p.process("--meta", "test1=1")

    assert hasattr(a0, "meta") and a0.meta == {"test1": 1}
    assert hasattr(a1, "meta") and a1.meta == {"test1": 1}


def test_process():
    p = get_arg_parser()

    a0 = p.process("--meta test1=1 --meta test2=2")
    assert a0.meta == {"test1": 1, "test2": 2}

    a1 = a0.reprocess("--meta test3=3")
    assert a1.meta == {"test1": 1, "test2": 2, "test3": 3}

    a2 = a0.reprocess("--meta test4=4")
    assert a2.meta == {"test1": 1, "test2": 2, "test4": 4}


def test_stupid_reprocess_args():
    p = get_arg_parser()
    a0 = p.process()
    with pytest.raises(SystemExit) as exc:
        a0.reprocess("--help")
    assert exc.value.code != 0
