# Python modules
import itertools
import logging

# NOC modules
from core.comp import smart_text

logger = logging.getLogger(__name__)


class BaseParameter(object):
    PARAM_NUMBER = itertools.count()

    def __init__(self, default=None, help=None):
        self.param_number = next(self.PARAM_NUMBER)
        if default is None:
            self.default = None
            self.orig_value = None
        else:
            self.orig_value = default
            self.default = self.clean(default)
        self.help = help
        self.name = None  # Set by metaclass
        self.value = self.default  # Set by __set__ method

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.set_value(value)

    def set_value(self, value):
        self.orig_value = value
        self.value = self.clean(value)

    def clean(self, v):
        return v

    def dump_value(self):
        return self.value


class StringParameter(BaseParameter):
    def __init__(self, default=None, help=None, choices=None):
        self.choices = choices
        super().__init__(default=default, help=help)

    def clean(self, v):
        v = smart_text(v)
        if self.choices:
            if v not in self.choices:
                raise ValueError("Invalid value: %s" % v)
        return v

class IntParameter(BaseParameter):
    def __init__(self, default=None, help=None, min=None, max=None):
        self.min = min
        self.max = max
        super().__init__(default=default, help=None)

    def clean(self, v):
        v = int(v)
        if self.min is not None:
            if v < self.min:
                raise ValueError("Value is less than %d" % self.min)
        if self.max is not None:
            if v > self.max:
                raise ValueError("Value is greater than %d" % self.max)
        return v

class MapParameter(BaseParameter):
    def __init__(self, default=None, help=None, mappings=None):
        self.mappings = mappings or {}
        super().__init__(default=default, help=help)

    def clean(self, v):
        try:
            return self.mappings[smart_text(v)]
        except KeyError:
            raise ValueError("Invalid value %s" % v)

    def dump_value(self):
        if not self.mappings:
            return super().dump_value()
        for mv in self.mappings:
            if self.mappings[mv] == self.value:
                return mv
        return self.value

class BooleanParameter(BaseParameter):
    def clean(self, v):
        if isinstance(v, str):
            v = v.lower() in ["y", "t", "true", "yes"]
        return bool(v)