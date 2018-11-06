# =============================================================================
#   Logging setup
# =============================================================================
import settings
import logging, logging.handlers
import sys
import os
from datetime import datetime


start_time = datetime.now()
logFile = os.path.join(settings.PROJECT_DIR, r'logs\XF_Docs.log')
logFormat = '%(asctime)s -- %(levelname)s -- %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#fileHandler = logging.handlers.RotatingFileHandler(filename=rotating_log_file, maxBytes=log_file_size, backupCount=20)
fileHandler = logging.handlers.RotatingFileHandler(filename=logFile, maxBytes=10*1048576, backupCount=10)  # Adding File Handler
fileHandler.setLevel(logging.DEBUG)  # Setting level of Handler
fileHandler.setFormatter(logging.Formatter(logFormat))  # Setting Format of handler
logger.addHandler(fileHandler)  # Adding the Handler to logger.

consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(logging.Formatter(logFormat))  # Setting Format of handler
logger.addHandler(consoleHandler)

logger.info('Program Start')