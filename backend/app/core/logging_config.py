import logging
import logging.config


class SafeFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "job_id"):
            record.job_id = "-"
        if not hasattr(record, "step_name"):
            record.step_name = "-"
        return super().format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": SafeFormatter,
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | job=%(job_id)s | step=%(step_name)s | %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        # FastAPI/Uvicorn internal logs
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        # application logs
        "app": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
