import logging

FORMAT = "%(asctime)s] %(levelname)s %(module)s %(funcName)s: %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOGFILE = "cloudly.log"


def init(name, log_level=DEFAULT_LOG_LEVEL):
    # Create logger and formatter
    logger = logging.getLogger(name)
    configure_logger(logger, log_level)
    return logger


def configure_logger(logger, log_level):
    logger.setLevel(log_level)
    formatter = logging.Formatter(FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(DEFAULT_LOGFILE)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
