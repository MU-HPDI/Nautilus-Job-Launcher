import logging
import logging.config


def setup_logger(name, verbose=False):
    level = logging.INFO if verbose else logging.ERROR

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                name: {"format": "[%(asctime)s] (%(levelname)s):: %(message)s"}
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "formatter": name,
                    "level": level,
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": name,
                    "level": logging.DEBUG,
                    "filename": "nautiluslauncher.log",
                },
            },
            "loggers": {
                name: {
                    "level": logging.DEBUG,
                    "handlers": ["stdout", "file"],
                    "propagate": False,
                }
            },
        }
    )

    return logging.getLogger(name)


LOGGER = setup_logger("nautiluslauncher", verbose=True)
