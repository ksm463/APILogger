import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_path, logger_name=__name__) -> logging.Logger:

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    rotating_handler = RotatingFileHandler(
        log_path, maxBytes=30 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    rotating_handler.setFormatter(formatter)
    logger.addHandler(rotating_handler)
    
    return logger
