import logging, os

def get_logger():
    level = logging.getLevelName(os.getenv("log_level", "INFO"))
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger