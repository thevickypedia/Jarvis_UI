# noinspection PyUnresolvedReferences
"""Initiates a custom logger to be accessed across modules.

>>> Logger

Disables loggers from imported modules, while using the root logger without having to load an external file.

"""

import importlib
import logging
import os
from logging.config import dictConfig

from jarvis_ui.modules.models import env, fileio

if not os.path.isdir('logs'):
    os.makedirs('logs')

importlib.reload(module=logging)
dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})
logging.getLogger("_code_cache").propagate = False
log_level = logging.DEBUG if env.debug else logging.INFO


def file_logger() -> logging.Logger:
    """Create custom file logger.

    Returns:
        Logger:
        Returns the logger object.
    """
    logging.basicConfig(
        filename=fileio.base_log_file, filemode='a', level=log_level,
        format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s',
        datefmt='%b-%d-%Y %I:%M:%S %p'
    )
    return logging.getLogger(__name__)


def console_logger() -> logging.Logger:
    """Create custom stream logger.

    Returns:
        Logger:
        Returns the logger object.
    """
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s',
        datefmt='%b-%d-%Y %I:%M:%S %p', level=log_level
    )
    return logging.getLogger(__name__)


logger = file_logger()
