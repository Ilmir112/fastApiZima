import logging
from pythonjsonlogger.json import JsonFormatter

logger = logging.getLogger()

logHandler = logging.StreamHandler()

formatter = JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)