# Python modules
import inspect
import os

# HTTP modules
from .params import BaseParameter
from core.config.proto.yaml import YAMLProtocol

DEFAULT_CONFIG = "yaml:///opt/http/etc/settings.yml"


class ConfigSectionBase(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        cls._params = {}
        for k in attrs:
            if isinstance(attrs[k], BaseParameter):
                cls._params[k] = attrs[k]
                cls._params[k].name = k
        return cls


class ConfigSection(object, metaclass=ConfigSectionBase):
    pass


class ConfigBase(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        cls._params = {}
        for k in attrs:
            if isinstance(attrs[k], BaseParameter):
                cls._params[k] = attrs[k]
                cls._params[k].name = k
            elif inspect.isclass(attrs[k]) and issubclass(attrs[k], ConfigSection):
                for kk in attrs[k]._params:
                    sn = "%s.%s" % (k, kk)
                    cls._params[sn] = attrs[k]._params[kk]
        cls._params_order = sorted(cls._params, key=lambda x: cls._params[x].param_number)
        return cls


class BaseConfig(object, metaclass=ConfigBase):

    def load(self):
        paths = os.environ.get("SERVER_CONFIG", DEFAULT_CONFIG)
        for p in paths.split(","):
            p = p.strip()
            proto = YAMLProtocol(self, p)
            proto.load()
