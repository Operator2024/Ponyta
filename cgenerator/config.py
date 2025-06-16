import os

logging_config: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "datefmt": "[%d/%b/%Y %H:%M:%S %z]",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "verbose": {
            "datefmt":
            "[%d/%b/%Y %H:%M:%S %z]",
            "format":
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "verbose",
            "when": "D",
            "backupCount": 0,
            "filename": "cgenerator.log",
        },
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    },
}

WEB_CONFIG_FILE = os.environ.get("WEB_CONFIG_FILE", "web.yml")
ENV_FILE = os.environ.get("ENV_FILE", ".env")
