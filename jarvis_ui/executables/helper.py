import os
import re
import sys
from multiprocessing.managers import DictProxy  # noqa
from typing import NoReturn, Union

import requests

from jarvis_ui.logger import logger
from jarvis_ui.modules.models import env, settings

FAILED_HEALTH_CHECK = {"count": 0}


def linux_restart() -> NoReturn:
    """Restarts the base script on Linux OS.

    See Also:
        - In Linux, it is not possible to trigger port audio on multiple processes.
        - To overcome this problem, JarvisUI on Linux is set to restart from self.
        - Since restarting executable triggers the base script, explicit reload of env vars are not required.

    Raises:
        - KeyboardInterrupt: To stop the current process to avoid recursion.
    """
    os.execv(sys.executable, ["python"] + sys.argv)
    raise KeyboardInterrupt


def heart_beat(status_manager: DictProxy = None) -> None:
    """Initiate health check with the server.

    Args:
        status_manager: Shared multiprocessing dict to update in case of failed health check.

    See Also:
        - Heart beat should be set no lesser than 5 seconds to avoid throttling and no longer than an hour.
        - Maintains a consecutive failure threshold of 5, as a single failed health check doesn't warrant a restart.
    """
    try:
        response = requests.get(url=env.server_url + "health", timeout=(3, 3))
    except requests.RequestException as error:
        logger.error(error)
    else:
        if response.ok:
            if FAILED_HEALTH_CHECK["count"]:
                logger.info("Resetting failure count")
                FAILED_HEALTH_CHECK["count"] = 0
            return
    FAILED_HEALTH_CHECK["count"] += 1
    if FAILED_HEALTH_CHECK["count"] >= 5:
        while True:
            # Awaits any ongoing request/response to go through before restarting
            if not status_manager["LOCKED"]:
                break
        logger.critical("Heart beat failed for 5 times in row, restarting...")
        if settings.operating_system == "Linux":
            linux_restart()
        status_manager["LOCKED"] = None


def extract_nos(input_: str, method: type = float) -> Union[int, float]:
    """Extracts number part from a string.

    Args:
        input_: Takes string as an argument.
        method: Takes a type to return a float or int value.

    Returns:
        Union[int, float]:
        Integer/float values from the phrase.
    """
    if value := re.findall(r"\d+", input_):
        if method == float:
            try:
                return method(".".join(value))
            except ValueError:
                method = int
        if method == int:
            return method("".join(value))
