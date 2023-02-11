import logging
import logging.config
from typing import Any

config: dict[str, Any] = {
    "version": 1,
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
        "app": {
            "level": "DEBUG",
            "handlers": ["console"],
        }
    },
}

logging.config.dictConfig(config)
