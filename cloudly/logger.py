import os
import logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL  # noqa

FORMAT = "%(asctime)s] %(levelname)s %(module)s %(funcName)s: %(message)s"
DEFAULT_LOGFILE = "cloudly.log"

log_level_string = os.environ.get("CLOUDLY_LOG_LEVEL", "info")
log_level_map = {
    'debug': DEBUG,
    'info': INFO,
    'warning': WARNING,
    'error': ERROR,
    'critical': CRITICAL
}
try:
    default_log_level = log_level_map[log_level_string]
except KeyError, exception:
    print ("WARNING: Log level {!r} not supported. "
           "Using 'info' instead.".format(
               log_level_string))
    default_log_level = INFO


def init(name, log_level=default_log_level):
    # Create logger and formatter
    logger = logging.getLogger(name)
    configure_logger(logger, log_level)
    return logger


def configure_logger(logger, log_level, log_to_file=False):
    logger.setLevel(log_level)
    formatter = logging.Formatter(FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_to_file:
        # File handler
        file_handler = logging.FileHandler(DEFAULT_LOGFILE)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
