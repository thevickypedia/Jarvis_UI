# noinspection PyUnresolvedReferences
"""Makes a post call to Jarvis API running in the backend to process a request and return the response.

>>> APIHandler

"""
import json
from typing import Union

import requests

from modules.logger import logger
from modules.models import env, fileio

session = requests.Session()
session.headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {env.token}'
}


def make_request(path: str, timeout: Union[int, float], data: dict = None) -> Union[dict, bool]:
    """Makes a ``POST`` call to the API running on the backend to execute a said task.

    Args:
        data: Takes the command to be executed as an argument.
        path: Path to make the api call.
        timeout: Timeout for a specific call.

    See Also:
        - Makes session calls using a fixed connect timeout for ``3 seconds`` and variable read timeout.

    Returns:
        dict:
        Returns the JSON response if request was successful.
    """
    try:
        response = session.post(url=env.request_url + path, json=data, timeout=(3, timeout))
    except requests.RequestException as error:
        logger.error(error)
        return False
    if not response.ok:
        logger.error(f"{response.status_code} - {response.reason}")
        return False
    if path == "speech-synthesis" or (data and data.get('native_audio')):
        with open(file=fileio.speech_wav_file, mode="wb") as file:
            file.write(response.content)
        return True
    try:
        return response.json()
    except json.JSONDecodeError as error:
        logger.error(error)
