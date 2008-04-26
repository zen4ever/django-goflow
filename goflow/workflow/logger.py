import logging
from django.conf import settings

import logging
logger = logging.getLogger('workflow.log')

try:
    _file_log = settings.LOGGING_FILE
    _LOG_FILE_NOTSET = False
except Exception:
    _LOG_FILE_NOTSET = True
    _file_log = 'workflow.log'
    
_hdlr = logging.FileHandler(_file_log)
_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
_hdlr.setFormatter(_formatter)
logger.addHandler(_hdlr)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

if _LOG_FILE_NOTSET:
     logger.warning('settings.LOGGING_FILE not set; default is workflow.log')
