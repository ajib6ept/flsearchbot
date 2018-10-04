import os
import logging

from logging.handlers import RotatingFileHandler


class Logger():
    def __init__(self, log_file, logger_name):
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        fh = RotatingFileHandler(log_file, mode='a', maxBytes=10 * 1024 * 1024,
                                 backupCount=5, encoding=None, delay=0)
        fh.setLevel(logging.DEBUG)
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def get(self):
        return self.logger
