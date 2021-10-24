#!/usr/bin/env python
# coding: utf-8


import os
import logdna.dispatch as d


def test_headers():
    os.environ["LOGDNA_TOKEN"] = "feeddeadbeeffeeddeadbeeffeeddead"
    h = d.gen_headers()
    assert h["Content-Type"] == "application/json; charset=UTF-8"
    assert h["Authorization"] == "Basic ZmVlZGRlYWRiZWVmZmVlZGRlYWRiZWVmZmVlZGRlYWQ="


def test_url():
    url = d.gen_url(hostname="white-rabit", now=94712411)
    assert url == "https://logs.logdna.com/logs/ingest?hostname=white-rabit&now=94712411"

    url = d.gen_url(hostname="white-rabit", tags=["supz", "mang"], now=94712417)
    assert url == "https://logs.logdna.com/logs/ingest?hostname=white-rabit&tags=supz,mang&now=94712417"
