#!/usr/bin/env python
# coding: utf-8

from ldogger.filter_machine import FilterMachine, FMFile


def test_re1():
    fmf = FMFile("t/files/re-1")

    assert len(fmf.patterns) == 5
    assert bool(fmf.search("aba")) is True


def test_filter_machine():
    fm = FilterMachine(["t/files/re-1"])

    assert fm.search("supz") is None
    assert fm.search("aba") is not None
    assert fm.search("aba") is not True
    assert fm("aba") is True
    assert fm("OK") is None
