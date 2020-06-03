# Python modules
import logging
import sys

# NOC modules
from core.config.base import BaseConfig, ConfigSection
from core.config.params import (
    StringParameter,
    IntParameter,
    MapParameter
)


class Config(BaseConfig):
    class log(ConfigSection):
        loglevel = MapParameter(
            default="info",
            mappings={
                # pylint: disable=used-before-assignment
                "critical": logging.CRITICAL,
                # pylint: disable=used-before-assignment
                "error": logging.ERROR,
                # pylint: disable=used-before-assignment
                "warning": logging.WARNING,
                # pylint: disable=used-before-assignment
                "info": logging.INFO,
                # pylint: disable=used-before-assignment
                "debug": logging.DEBUG,
            },
        )
        log_format = StringParameter(default="%(asctime)s [%(levelname)s] [%(name)s] [%(funcName)s] %(lineno)d: %(message)s")

    class httpserver(ConfigSection):
        host = StringParameter(default="127.0.0.1")
        port = IntParameter(default=80)
        hostname = StringParameter(default="localhost")
        max_threads = IntParameter(default=1)
        root = StringParameter(default="/opt/httpd/web/")


config = Config()
config.load()

