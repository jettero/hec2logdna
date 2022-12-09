import os, sys, re


class FMFile:
    patterns = mtime = None
    comment_pattern = re.compile(r"^\s*#")

    def __init__(self, fname):
        self.fname = fname
        self.already = set()
        self.read_file()

    def read_file(self):
        try:
            mtime = os.stat(self.fname).st_mtime
            if self.mtime is None or self.mtime != mtime:
                self.patterns = list()
                self.mtime = mtime
                with open(self.fname, "r") as fh:
                    for line in [y for y in [x.strip() for x in fh] if y and not self.comment_pattern.search(y)]:
                        try:
                            self.patterns.append(re.compile(line))
                        except re.error as e:
                            if line not in already:
                                already.add(line)
                                sys.stderr.write(f'RE="{line}" from {self.fname} not understood: {e}')
        except FileNotFoundError:
            pass

    def search(self, line):
        self.read_file()
        for p in self.patterns:
            if m := p.search(line):
                return m


class FilterMachine:
    def __init__(self, files):
        self.files = [FMFile(x) for x in files]
        self.loaded = dict()

    def search(self, line):
        for fmf in self.files:
            if m := fmf.search(line):
                return m

    def __call__(self, line):
        if self.search(line):
            return True
