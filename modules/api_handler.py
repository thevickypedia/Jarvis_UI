# noinspection PyUnresolvedReferences
"""Makes a post call to Jarvis API running in the backend to process a request and return the response.

>>> APIHandler

"""
import json
from typing import Union

import requests

from modules.logger import logger
from modules.models import env


def make_request(path: str, timeout: Union[int, float], task: str = None) -> Union[dict, None]:
    """Makes a ``POST`` call to offline-communicator running on ``localhost`` to execute a said task.

    Args:
        task: Takes the command to be executed as an argument.
        path: Path to make the api call.
        timeout: Timeout for a specific call.

    Returns:
        dict:
        Returns the JSON response if request was successful.
    """
    try:
        if task:
            response = requests.post(url=env.request_url + path,
                                     headers={'accept': 'application/json',
                                              'Authorization': f'Bearer {env.offline_pass}'},
                                     json={'command': task},
                                     timeout=timeout)
        else:
            response = requests.post(url=env.request_url + path, timeout=timeout)
    except requests.RequestException as error:
        logger.error(error)
        return
    try:
        return response.json()
    except json.JSONDecodeError as error:
        logger.error(error)
