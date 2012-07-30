import logging

FORMAT = "%(asctime)s] %(levelname)s %(module)s %(funcName)s: %(message)s"
LOG_LEVEL = logging.INFO
LOGFILE = "cloudly.log"


def init(name, log_level=LOG_LEVEL):
    # Create logger and formatter
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    formatter = logging.Formatter(FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(LOGFILE)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
