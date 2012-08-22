# -*- coding: utf-8 -*-

import distutils.core
import sys
from glob import glob
import unittest
from imp import load_source
import os.path

def _import(m):
    from imp import load_module as _load, find_module as _find
    m, _m = m.split('.'), None
    for i in range(len(m)):
        _m = _load(".".join(m[:i+1]), *_find(m[i], _m and [_m.__file__.rsplit('/', 1)[0]]))
    return _m

class test(distutils.core.Command):

    description = "runs all tests"

    user_options = [
        ('failfast', 'f', 'exit on first failing test')
    ]

    boolean_options = ['failfast']

    def initialize_options(self):
        self.failfast = False
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
        fail = 0
        for test in self.files:
            test_mod = load_source(os.path.basename(test)[:-3], test)
            test_mod_path = os.path.dirname(os.path.realpath(test_mod.__file__))
            print "\nrunning", test
            if test_mod_path not in sys.path:
                sys.path.append(test_mod_path)
            runner = unittest.TextTestRunner(verbosity=self.verbosity)
            result = runner.run(test_mod.GetTestSuite())
            if len(result.failures) > 0 or len(result.errors):
                fail += len(result.failures) + len(result.errors)
                if self.failfast:
                    break
        sys.exit(fail)
