from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

BASE_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
BASE_LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {module} {process:d} {thread:d} {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_LOG_DIR / "app.log",
            "maxBytes": 1024 * 1024,
            "backupCount": 3,
            "formatter": "verbose",
        },
        "daily_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": BASE_LOG_DIR / "daily.log",
            "when": "D",
            "backupCount": 7,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "users": {"handlers": ["console", "rotating_file", "daily_file"], "level": "INFO", "propagate": False},
        "schedule": {"handlers": ["console", "rotating_file"], "level": "INFO", "propagate": False},
    },
}
