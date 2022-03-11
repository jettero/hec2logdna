#!/usr/bin/env python
# coding: utf-8


import multiprocessing
import subprocess

from queue import Empty, Full


class Tailer:
    TIMEOUT = 0.1
    SENTINEL = "\x04\x04\x04\x04"

    def _start_tail(self):
        p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
        while line := p.stdout.readline():
            line = line.decode()
            line = line.strip()
            if self.verbose:
                print("putting line in queue:", line)
            try:
                self.q.put(line)
            except Full:
                if self.verbose:
                    print("queue stuffed, dropping log line")
        print(f"process running {self.cmd} finished. dropping sentinel and closing queue")
        self.q.put(self.SENTINEL)
        self.q.close()

    def __init__(self, *cmd, verbose=False):
        self.done = False
        self.verbose = verbose
        self.cmd = cmd
        self.q = multiprocessing.Queue()
        self.t = multiprocessing.Process(target=self._start_tail, daemon=True)
        # daemon
        #     The process’s daemon flag, a Boolean value. This must be set before
        #     start() is called.  The initial value is inherited from the creating
        #     process.  When a process exits, it attempts to terminate all of its
        #     daemonic child processes.  Note that a daemonic process is not allowed
        #     to create child processes. Otherwise a daemonic process would leave its
        #     children orphaned if it gets terminated when its parent process exits.
        #     Additionally, these are not Unix daemons or services, they are normal
        #     processes that will be terminated (and not joined) if non-daemonic
        #     processes have exited.
        self.t.start()
        if self.verbose:
            print(f"starting child process running {self.cmd}")

    def get(self, timeout=TIMEOUT):
        try:
            ret = self.q.get(timeout=timeout)
            if ret == self.SENTINEL:
                self.done = True
                self.q.close()
                return
            return ret
        except Empty:
            pass

    def __iter__(self, timeout=TIMEOUT):
        while line := self.get(timeout=timeout):
            yield line
