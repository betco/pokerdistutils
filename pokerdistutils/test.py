# -*- coding: utf-8 -*-

import distutils.core
import sys, os, subprocess
from glob import glob

def _import(m):
    from imp import load_module as _load, find_module as _find
    m, _m = m.split('.'), None
    for i in range(len(m)):
        _m = _load(".".join(m[:i+1]), *_find(m[i], _m and [_m.__file__.rsplit('/', 1)[0]]))
    return _m

class test(distutils.core.Command):

    description = "runs all tests"

    user_options = [
        ('parallel', 'p', 'parallel execution of tests')
    ]

    boolean_options = ['parallel']

    def initialize_options(self):
        self.parallel = False
        self.verbosity = 1
        self.files = []

    def finalize_options(self):
        if self.files:
            _tmp, self.files = self.files.split(), []
            for _glob in _tmp:
                self.files.extend(glob(_glob))

    def run(self):
        """
        Runs all tests
        """
	returnval = 0
        test_processes = ((test, subprocess.Popen(['/usr/bin/env', 'python', test], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)) for test in self.files if os.access(test, os.X_OK))
        if self.parallel:
            test_processes = list(test_processes)
        for test, p in test_processes:
            print "\nrunning", test
            while True:
                buf = p.stdout.read(1)
                if not buf:
                    break
                sys.stdout.write(buf)
                sys.stdout.flush()
            returnval += p.wait()
        sys.exit(returnval)
