#!/usr/bin/env python
# coding: utf-8

from ldogger.tailer import Tailer


def test_tailer_n5():
    t = Tailer(*("head -n5 -v t/files/test.log".split()))
    l = list(t)

    assert "==>" in l[0]
    assert l[-1] == "test-5"


def test_tailer_nm5():
    t = Tailer(*("tail -n4 t/files/test.log".split()))
    l = list(t)

    assert l[0] == "test-97"
    assert l[-1] == "test-100"


def test_tailer_append():
    with open("t/files/test.new", "w") as fh:
        t = Tailer(*("tail -n0 -F t/files/test.new".split()))

        l = list(t)
        assert l == []

        fh.write("supz\n")
        fh.flush()

        l = list(t)
        assert l == ["supz"]

        fh.write("this\nworks\n")
        fh.flush()

        l = list(t)
        assert l == ["this", "works"]
