# logger script taken from following source
# https://www.toptal.com/python/in-depth-python-logging#:~:text=There%20are%20six%20log%20levels%20in%20Python;%20each,particularity%20will%20be%20addressed%20next.%20Python%20Logging%20Formatting

import logging
import sys
from logging.handlers import TimedRotatingFileHandler


#########################
# Constants
#########################

FORMATTER = logging.Formatter("%(process)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = "v4_simulation.log"
META_DATA_FILE = "v4_metadata.log"
LOG_LEVEL = logging.NOTSET
METADATA_LOGGER = "meta_data_logger"
TEST_LOGGER = "rovpp_v4_test_logger"
SIM_LOGGER = "rovpp_v4_sim_logger"
CONDUCTING_SYSTEM_TEST = False

LOG_FILE_MAP = {
   METADATA_LOGGER: META_DATA_FILE,
   SIM_LOGGER: LOG_FILE,
   TEST_LOGGER: LOG_FILE
}


def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler

def get_file_handler(log_file):
   file_handler = TimedRotatingFileHandler(log_file, when='midnight')
   file_handler.setFormatter(FORMATTER)
   return file_handler

def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(LOG_LEVEL)  # better to have too much log than not enough
   # logger.addHandler(get_console_handler())  # Also prints to console
   logger.addHandler(get_file_handler(LOG_FILE_MAP[logger_name]))
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger

sim_logger = get_logger(SIM_LOGGER)
test_logger = get_logger(TEST_LOGGER)
metadata_logger = get_logger(METADATA_LOGGER)
