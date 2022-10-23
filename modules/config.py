"""This is a space for configuration required by the API module.

>>> Config

"""
import os
import platform
import warnings
from typing import Callable, NoReturn

import pvporcupine
from pydantic import BaseConfig, PositiveInt

from modules.api_handler import make_request
from modules.logger import logger
from modules.models import env, fileio, settings

add_ss_extn: Callable = lambda filepath: os.path.splitext(filepath)[0] + "_ss" + os.path.splitext(filepath)[1]


def swapper() -> NoReturn:
    """Swaps any request URL with the public URL if returned by Jarvis.

    Notes:
        Avoid making calls via load balancers or reverse proxy (if one is in place) such as CloudFront or Nginx.
    """
    if (public_url := make_request(path='offline-communicator', timeout=env.request_timeout,
                                   data={'command': 'ngrok public url'})) and public_url.get('detail'):
        if public_url['detail'][-1] != "/":
            public_url['detail'] += "/"
        if public_url['detail'] == env.request_url:
            return
        logger.info(f"Switching {env.request_url} to {public_url['detail']}")
        env.request_url = public_url['detail']


class Config(BaseConfig):
    """Gets keywords, conversation and api-compatibles during start up. Mandates ``speech-synthesis`` for WindowsOS.

    >>> Config

    """
    if not env.recognizer_settings and not env.voice_phrase_limit:
        env.recognizer_settings = env.recognizer_settings_default  # Default override when phrase limit is not available

    if env.request_url[-1] != "/":
        env.request_url += "/"
    swapper()
    if isinstance(env.sensitivity, float) or isinstance(env.sensitivity, PositiveInt):
        env.sensitivity = [env.sensitivity] * len(env.wake_words)
    EXCEPTION = ConnectionError(f"Unable to connect to the API via {env.request_url}")
    if not (keywords := make_request(path='keywords', timeout=env.request_timeout)):
        logger.error(EXCEPTION)
        keywords = {}
    if not (conversation := make_request(path='conversation', timeout=env.request_timeout)):
        logger.error(EXCEPTION)
        conversation = {}
    if not (api_compatible := make_request(path='api-compatible', timeout=env.request_timeout)):
        logger.error(EXCEPTION)
        api_compatible = {}
    if detail := keywords.get("detail", conversation.get("detail", api_compatible.get("detail"))):
        logger.error(detail)

    # delay_keywords = list(filter(lambda v: v is not None, delay_keywords))  # If 0 is to be included
    delay_with_ack = list(filter(None, keywords.get('car', []) + keywords.get('speed_test', []) +
                                 keywords.get('google_home', []) + keywords.get('garage', [])))
    delay_without_ack = list(filter(None, keywords.get('television', [])))  # Since delay is only on initial turn on
    keywords = sum([v for _, v in keywords.items()], [])
    conversation = sum([v for _, v in conversation.items()], [])

    if env.speech_timeout and env.native_audio:
        warnings.warn(
            "Both `speech-synthesis` and `native-audio` cannot be enabled simultaneously.\n"
            "Speech synthesis uses third-party tts service where as `native_audio` preserves the audio from server.\n"
            "Disabling speech synthesis!!"
        )
        env.speech_timeout = 0

    if not settings.macos and not env.native_audio and env.speech_timeout < env.request_timeout:
        env.speech_timeout = env.request_timeout

    if env.speech_timeout and not env.native_audio:
        fileio.failed = add_ss_extn(fileio.failed)
        fileio.shutdown = add_ss_extn(fileio.shutdown)
        fileio.processing = add_ss_extn(fileio.processing)
        fileio.unprocessable = add_ss_extn(fileio.unprocessable)

    if settings.legacy:
        pvporcupine.KEYWORD_PATHS = {}
        pvporcupine.MODEL_PATH = os.path.join(os.path.dirname(pvporcupine.__file__),
                                              'lib/common/porcupine_params.pv')
        pvporcupine.LIBRARY_PATH = os.path.join(os.path.dirname(pvporcupine.__file__),
                                                f'lib/mac/{platform.machine()}/libpv_porcupine.dylib')
        keyword_files = os.listdir(os.path.join(os.path.dirname(pvporcupine.__file__), "resources/keyword_files/mac/"))
        for x in keyword_files:
            pvporcupine.KEYWORD_PATHS[x.split('_')[0]] = os.path.join(os.path.dirname(pvporcupine.__file__),
                                                                      f"resources/keyword_files/mac/{x}")

    for keyword in env.wake_words:
        if keyword == 'sphinx-build':
            break
        if not pvporcupine.KEYWORD_PATHS.get(keyword) or not os.path.isfile(pvporcupine.KEYWORD_PATHS[keyword]):
            raise ValueError(
                f"Detecting '{keyword}' is unsupported!\n"
                f"Available keywords are: {', '.join(list(pvporcupine.KEYWORD_PATHS.keys()))}"
            )


config = Config()
