# noinspection PyUnresolvedReferences
"""Initiates a custom logger to be accessed across modules.

>>> Logger

Disables loggers from imported modules, while using the root logger without having to load an external file.

"""

import importlib
import logging
import os
from datetime import datetime
from logging.config import dictConfig

log_file = datetime.now().strftime(os.path.join('logs', 'jarvis_%d-%m-%Y.log'))

if not os.path.isdir('logs'):
    os.makedirs('logs')

importlib.reload(module=logging)
dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})
logging.getLogger("_code_cache").propagate = False
logging.basicConfig(
    filename=log_file, filemode='a', level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s',
    datefmt='%b-%d-%Y %I:%M:%S %p'
)
logger = logging.getLogger('jarvis')
