#!/usr/bin/env python
# encoding: utf-8

import argparse


def main(args):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ldogger like logdna logger, like /bin/logger, get it??",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("filename", nargs="?", default="/dev/stdin")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        pass
