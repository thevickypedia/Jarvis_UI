# noinspection PyUnresolvedReferences
"""Makes a post call to Jarvis API running in the backend to process a request and return the response.

>>> APIHandler

"""
import json
from typing import Union

import requests

from modules.logger import logger
from modules.models import env, fileio


def make_request(path: str, timeout: Union[int, float], data: dict = None) -> Union[dict, bool]:
    """Makes a ``POST`` call to offline-communicator running on ``localhost`` to execute a said task.

    Args:
        data: Takes the command to be executed as an argument.
        path: Path to make the api call.
        timeout: Timeout for a specific call.

    Returns:
        dict:
        Returns the JSON response if request was successful.
    """
    try:
        response = requests.post(url=env.request_url + path,
                                 headers={'accept': 'application/json',
                                          'Authorization': f'Bearer {env.token}'},
                                 json=data, timeout=timeout)
    except requests.RequestException as error:
        logger.error(error)
        return False
    if not response.ok:
        logger.error(f"{response.status_code} - {response.reason}")
        return False
    if path == "speech-synthesis":
        with open(file=fileio.speech_wav_file, mode="wb") as file:
            file.write(response.content)
        return True
    try:
        return response.json()
    except json.JSONDecodeError as error:
        logger.error(error)
