"""This is a space for configuration required by the API module.

>>> Config

"""

from pydantic import BaseConfig

from modules.api_handler import make_request
from modules.models import env


class Config(BaseConfig):
    """Gets keywords, conversation and api-compatibles during start up. Mandates ``speech-synthesis`` for WindowsOS.

    >>> Config

    """

    if env.request_url[-1] != "/":
        env.request_url += "/"
    EXCEPTION = ConnectionError(f"Unable to connect to the API via {env.request_url}")
    if not (keywords := make_request(path='keywords', timeout=env.request_timeout)):
        raise EXCEPTION
    if not (conversation := make_request(path='conversation', timeout=env.request_timeout)):
        raise EXCEPTION
    if not (api_compatible := make_request(path='api-compatible', timeout=env.request_timeout)):
        raise EXCEPTION
    if detail := keywords.get("detail", conversation.get("detail", api_compatible.get("detail"))):
        exit(detail)
    if not env.macos and (not env.speech_timeout or env.speech_timeout < env.request_timeout):
        env.speech_timeout = env.request_timeout

    # delay_keywords = list(filter(lambda v: v is not None, delay_keywords))  # If 0 is to be included
    delay_with_ack = list(filter(None, keywords.get('car', []) + keywords.get('speed_test', []) +
                                 keywords.get('google_home', [])))
    delay_without_ack = list(filter(None, keywords.get('television', [])))
    delay_keywords = delay_with_ack + delay_without_ack
    keywords = sum([v for _, v in keywords.items()], [])
    conversation = sum([v for _, v in conversation.items()], [])


config = Config()
