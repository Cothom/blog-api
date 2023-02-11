"""Configuration of logging module for the whole app"""

import logging.config
from typing import Any

# Configuration dict
config: dict[str, Any] = {
    "version": 1,  # 1 is the only accepted value
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        # Any module in 'app' package will inherit from this configuration
        # if getting a logger with its own __name__ (e.g.: app.routes)
        "app": {
            "level": "DEBUG",
            "handlers": ["console"],
        }
    },
}

# Application of the configuration
logging.config.dictConfig(config)
