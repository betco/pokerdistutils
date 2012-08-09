#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import Command
import re, os
from glob import glob
from config import Config

class configure(Command):
    
    description = 'configure .in files'
        
    user_options = [
        ('reset', 'r', 'reset config.json'),
        ('set=', 's', 'set attribute in config.json'),
        ('build', 'b', 'build .in files')
    ]

    boolean_options = ['reset', 'build']

    def initialize_options(self):
        self.set = None
        self.reset = 0
        self.build = 0
        self.files = []

    def finalize_options(self):
        if self.set:
            self.set = [(p,v) for p, v in [p.split('=') for p in self.set.split(',')]]
        if self.files:
            _tmp, self.files = self.files.split(), []
            for _glob in _tmp:
                self.files.extend(glob(_glob))

    def run(self):
        '''
        Finds all .in files and execute replacements
        '''
        config = Config('default.json', 'config.json')
        
        if self.reset:
            config.reset()
            if os.path.exists(config._local_file):
                os.unlink(config._local_file)
        
        if self.set:
            for path, value in self.set:
                config.set(path, value)
            config.save()
        
        if self.build:
            _re = re.compile(r'@([a-zA-Z\._]*)@')
            
            for _file in self.files:
                _out_file = _file[:-3]
                print _file, '->', _out_file
                _fd_i = open(_file, 'r')
                _fd_o = open(_out_file, 'w')
                try:
                    _fd_o.write(_re.sub(lambda m: str(eval(m.group(1), {
                        'version': self.distribution.get_version(),
                        'srcdir': os.getcwd(),
                        'config': config
                    })), _fd_i.read()))
                except NameError as e:
                    e.args = (e.args[0]+' (is looked up in config)',)
                    raise
