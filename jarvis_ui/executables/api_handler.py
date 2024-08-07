# noinspection PyUnresolvedReferences
"""Makes a post call to Jarvis API running in the backend to process a request and return the response.

>>> APIHandler

"""
import json
from typing import Union

import requests
from pydantic import ValidationError
from requests.auth import AuthBase
from requests.models import PreparedRequest

from jarvis_ui.logger import logger
from jarvis_ui.modules.models import env, fileio, get_server_url


class BearerAuth(AuthBase):
    """Instantiates ``BearerAuth`` object.

    >>> BearerAuth

    References:
        `New Forms of Authentication <https://requests.readthedocs.io/en/latest/user/authentication/#new
        -forms-of-authentication>`__
    """

    def __init__(self, token: str):
        """Initializes the class and assign object members.

        Args:
            token: Token for bearer auth.
        """
        self.token = token

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        """Override built-in.

        Args:
            request: Takes prepared request as an argument.

        Returns:
            PreparedRequest:
            Returns the request after adding the auth header.
        """
        request.headers["authorization"] = "Bearer " + self.token
        return request


session = requests.Session()
session.auth = BearerAuth(token=env.token)
session.headers["Accept"] = "application/json"


def make_request(
    path: str, data: dict = None, method: str = "POST"
) -> Union[dict, bool]:
    """Makes a requests call to the API running on the backend to execute a said task.

    Args:
        data: Takes the command to be executed as an argument.
        path: Path to make the api call.
        method: HTTP methods, GET/POST.

    Returns:
        dict:
        Returns the JSON response if request was successful.
    """
    try:
        endpoint = get_server_url()
    except ValidationError as error:
        logger.critical(error)
        return False
    try:
        response = session.request(
            method=method,
            url=endpoint + path,
            json=data,
            timeout=(3, 30),
            verify=endpoint.startswith("https"),
        )
        assert response.ok, f"{response.status_code} - {response.reason}"
    except (requests.RequestException, AssertionError) as error:
        logger.error(error)
        return False
    if response.headers.get("Content-Type", "NO MATCH") == "application/octet-stream":
        with open(file=fileio.speech_wav_file, mode="wb") as file:
            file.write(response.content)
            file.flush()
        return True
    try:
        return response.json()
    except json.JSONDecodeError as error:
        logger.error(error)
