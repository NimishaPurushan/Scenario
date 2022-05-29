import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter
from logging.handlers import DatagramHandler
from datetime import datetime
from sys import stderr

'''LOGGING VARIABLES'''
# The below hard-coded values shall be used
# when running module(s) as main. Else, when
# run from __main__ , the below values shall
# be overridden by the values present in 'LoggingConfig.ini'
logging_file_name = 'interpreter.log'
CONSOLE_LOG_TO_DISPLAY = True
MAX_LOG_ROTATOR_FILES = 5
MAX_LOG_FILE_SIZE_kB = 100000
DATAGRAM_HOST_IP = '127.0.0.15'
DATAGRAM_PORT_NUMBER = 7777
CONSOLE_FILE = open('report.log', 'w+', encoding='utf-8')


class BaseLogger:
    """
    Provides basic logging functionalities:
    1. Log rotation
    """
    def __init__(self):
        """Setting up base attributes for logging"""
        self.base_log_filepath = 'tmp'
        self.base_log_format = '%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s'
        self.base_formatter = Formatter(fmt=self.base_log_format)
        self.base_rotating_handler = RotatingFileHandler(self.base_log_filepath+"\\"+logging_file_name,
                                                         maxBytes=MAX_LOG_FILE_SIZE_kB,
                                                         backupCount=MAX_LOG_ROTATOR_FILES,
                                                         encoding='utf-8')


class FrameworkLogger(BaseLogger):
    def __init__(self, logger_name):
        BaseLogger.__init__(self)
        if logger_name != '__main__':
            logger_name = logger_name.split('.')[-1]
        else:
            logger_name = 'main'
        self.logger = logging.getLogger(logger_name)
        self.formatter = self.base_formatter
        self.permanent_handler = self.base_rotating_handler
        self.datagram_handler = DatagramHandler(DATAGRAM_HOST_IP, DATAGRAM_PORT_NUMBER)
        self.permanent_handler.setFormatter(self.formatter)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(self.permanent_handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        '''
        if not self.__class__.__name__ == 'ApplicationLogger':
            self.logger.debug(f"Initialized framework logger for : {logger_name}")
        '''

    # Basic logging methods
    def info(self, msg, **kwargs):
        self.logger.info(msg, **kwargs)

    def debug(self, msg, **kwargs):
        self.logger.debug(msg, **kwargs)

    def warning(self, msg, **kwargs):
        self.logger.warning(msg, **kwargs)

    def critical(self, msg, **kwargs):
        self.logger.critical(msg, **kwargs)

    def error(self, msg, **kwargs):
        self.logger.error(msg, **kwargs)


class ScenarioLogger(FrameworkLogger):
    def __init__(self, logger_name):
        FrameworkLogger.__init__(self, logger_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

    def console(self, msg):
        try:
            msg = str(msg)
        except Exception as err:
            msg = str(msg.encode('utf-8', errors='ignore'))
        self.logger.info(f"Console message -> {msg}")
        try:
            if CONSOLE_LOG_TO_DISPLAY is True:
                print(str(datetime.now()) + '\t:\t' + msg, flush=True)
            print(str(datetime.now()) + '\t:\t' + msg, file=CONSOLE_FILE, flush=True)
        except UnicodeEncodeError as err:
            # Need to understand this better than just to bypass !!
            self.logger.warning(f"Unable to print {msg} on stdout. Hence not printing it.")

    def console_error(self, msg):
        try:
            msg = str(msg)
        except Exception as err:
            msg = str(msg.encode('utf-8', errors='ignore'))
        self.logger.info(f"Console message -> {msg}")
        try:
            if CONSOLE_LOG_TO_DISPLAY is True:
                print(str(datetime.now()) + '\t:\t' + msg, flush=True)
            print(str(datetime.now()) + '\t:\t' + msg, file=stderr, flush=True)
        except UnicodeEncodeError as err:
            # Need to understand this better than just to bypass !!
            self.logger.warning(f"Unable to print {msg} on stdout. Hence not printing it.")



