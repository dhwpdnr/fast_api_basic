import logging
from logging.config import dictConfig
import os

LOG_FILE_PATH = "logs/app.log"
os.makedirs("logs", exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # 기존 로거 유지
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] - %(name)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": LOG_FILE_PATH,
            "mode": "a",
        },
    },
    "root": {
        "level": "INFO",  # 전체 로그 레벨
        "handlers": ["console", "file"],
    },
}
