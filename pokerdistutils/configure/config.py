# -*- coding: utf-8 *-*

import os
from simplejson import loads as decode, dumps as encode

def _find_config(_path, _file):
    while True:
        _fpath = os.path.join(_path, _file)
        if os.path.exists(_fpath):
            return _fpath
        if len(_path) < 2:
            return None
        _path = os.path.abspath(os.path.join(_path, '..'))

class ConfigError(Exception):
    pass

class Node(object):
    
    def __init__(self, _path, _config):
        self._config = _config
        self._path = _path
    
    def __getattribute__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            try:
                _gkey = self._config._get_global("%s" % (self._get_path(key)))
            except KeyError:
                raise ConfigError("'%s' not in default config" % (self._get_path(key),))
            if type(_gkey) is dict:
                return Node(self._get_path(key), self._config)
            else:
                try:
                    return self._config._get_local(self._get_path(key))
                except (AttributeError, KeyError):
                    return _gkey

    def _get_path(self, key=None):
        if not key:
            return self._path
        return "%s.%s" % (self._path, key) if self._path else key

    def __repr__(self):
        return "<Node @%s>" % (self._path,)

class Config(Node):
    
    def __init__(self, _global, _local):
        super(Config, self).__init__(None, self)
        self._load_global(_global)
        self._load_local(_local)

    def _load_global(self, _file):
        self._global = {}
        self._global_file = _find_config(os.getcwd(), _file)
        if self._global_file:
            self._load(self._global_file, self._global)
        else:
            raise ConfigError("global config '%s' is mandatory" % (_file,))

    def _load_local(self, _file):
        self._local = {}
        self._local_file = _find_config(os.getcwd(), _file)
        if self._local_file:
            self._load(self._local_file, self._local)
        else:
            self._local_file = os.path.join(os.path.dirname(self._global_file), _file)

    def _load(self, _path, _dict):
        _dict.update(decode(open(_path).read()))

    def _get_local(self, path):
        return self._get(path, self._local)

    def _get_global(self, path):
        return self._get(path, self._global)
        
    def _get(self, _path, _dict):
        path = _path.split('.')
        v = _dict
        for k in path:
            v = v[k]
        return v

    def set(self, _path, _value):
        try:
            self._get_global(_path)
        except KeyError:
            raise ConfigError("'%s' not in default config" % (_path,))
        path = _path.split('.')
        v = self._local
        for k in path[:-1]:
            try:
                v = v[k]
            except KeyError:
                v[k] = {}
                v = v[k]
        v[path[-1]] = _value

    def reset(self):
        self._local = {}

    def save(self, _path=None):
        fd = open(_path if _path else self._local_file, 'w')
        fd.write(encode(self._local, indent="    "))
