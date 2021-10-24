#!/usr/bin/env python
# coding: utf-8

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def read_file(x, *more):
    def _inner():
        with open(x, "r") as fh:
            for line in fh:
                yield line.strip()

    ret = list(_inner())
    for item in more:
        for i in item:
            if i not in ret:
                ret.append(i)
    return ret


require = read_file("requirements.txt")
tests_require = [x for x in read_file("test-requirements.txt", require) if not x.startswith("-r ")]
setup_require = require + ["setuptools_scm"]

setup(
    name="ldogger",
    use_scm_version={
        "write_to": "version.py",
        "tag_regex": r"^(?P<prefix>v)(?P<version>\d+\.\d+\.\d+)(?P<suffix>.*)?$",
        # NOTE: use ./setup.py --version to regenerate version.py and print the
        # computed version
    },
    description="ldogger — a collection of gadgets for using logdna from loonix shells",
    author="Paul Miller",
    author_email="paul@jettero.pl",
    url="https://github.com/jettero/ldogger",
    cmdclass={"test": PyTest},
    packages=find_packages(),
    install_requires=require,
    tests_require=tests_require,
    setup_requires=setup_require,
    entry_points={
        "console_scripts": ["ldogger = ldogger.cmd:entry_point"],
    },
)
