# noinspection PyUnresolvedReferences
"""Makes a post call to Jarvis API running in the backend to process a request and return the response.

>>> APIHandler

"""

from typing import Union

import requests

from modules.logger import logger
from modules.models import env


def make_request(task: str) -> Union[str, None]:
    """Makes a ``POST`` call to offline-communicator running on ``localhost`` to execute a said task.

    Args:
        task: Takes the command to be executed as an argument.

    Returns:
        str:
        Returns the response if request was successful.
    """
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {env.offline_pass}',
    }
    try:
        response = requests.post(url=env.request_url, headers=headers, json={'command': task},
                                 timeout=env.request_timeout)
    except requests.RequestException as error:
        logger.error(error)
        return
    return response.json()['detail'].split('\n')[-1]
