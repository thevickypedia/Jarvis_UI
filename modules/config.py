"""This is a space for configuration required by the API module.

>>> Config

"""

from urllib.parse import urlparse

from pydantic import BaseConfig

from modules.api_handler import make_request
from modules.models import env


class Config(BaseConfig):
    """Make calls to get keywords, conversation and api-compatibles during start up.

    >>> Config

    """

    EXCEPTION = {"connection": ConnectionError("Unable to connect to the API."),
                 "permission": PermissionError("'REQUEST_URL' or 'TOKEN' not found in environment variables.")}
    if not env.request_url or not env.token:
        raise EXCEPTION['permission']
    parsed = urlparse(url=env.request_url)
    env.request_url = parsed.geturl()
    if env.request_url[-1] != parsed.path:
        env.request_url += parsed.path
    if not (keywords := make_request(path='keywords', timeout=env.request_timeout)):
        raise EXCEPTION['connection']
    if not (conversation := make_request(path='conversation', timeout=env.request_timeout)):
        raise EXCEPTION['connection']
    if not (api_compatible := make_request(path='api-compatible', timeout=env.request_timeout)):
        raise EXCEPTION['connection']
    if detail := keywords.get("detail", conversation.get("detail", api_compatible.get("detail"))):
        exit(detail)

    # delay_keywords = list(filter(lambda v: v is not None, delay_keywords))  # If 0 is to be included
    delay_with_ack = list(filter(None, keywords.get('car', []) + keywords.get('speed_test', []) +
                                 keywords.get('google_home', [])))
    delay_without_ack = list(filter(None, keywords.get('television', [])))
    delay_keywords = delay_with_ack + delay_without_ack
    keywords = sum([v for _, v in keywords.items()], [])
    conversation = sum([v for _, v in conversation.items()], [])


config = Config()
