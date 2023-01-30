# noinspection PyUnresolvedReferences
"""Module for listener and speech recognition.

>>> Listener

"""

import sys
from typing import Union

import requests
from speech_recognition import (Microphone, Recognizer, RequestError,
                                UnknownValueError, WaitTimeoutError)

from jarvis_ui.modules.logger import logger
from jarvis_ui.modules.models import env

recognizer = Recognizer()  # initiates recognizer object
microphone = Microphone()  # initiates microphone object

if env.recognizer_settings:
    recognizer.energy_threshold = env.recognizer_settings.energy_threshold
    recognizer.pause_threshold = env.recognizer_settings.pause_threshold
    recognizer.phrase_threshold = env.recognizer_settings.phrase_threshold
    recognizer.dynamic_energy_threshold = env.recognizer_settings.dynamic_energy_threshold
    recognizer.non_speaking_duration = env.recognizer_settings.non_speaking_duration
    env.voice_phrase_limit = 7  # Override voice phrase limit when recognizer settings are available


def listen() -> Union[str, None]:
    """Function to activate listener, this function will be called by most upcoming functions to listen to user input.

    Returns:
        str:
         - Returns recognized statement from the microphone.
    """
    with microphone as source:
        sys.stdout.write("\rListener activated..")
        try:
            listened = recognizer.listen(source=source, timeout=env.voice_timeout,
                                         phrase_time_limit=env.voice_phrase_limit)
            sys.stdout.write("\r")
            return recognizer.recognize_google(audio_data=listened)
        except (UnknownValueError, WaitTimeoutError, RequestError):
            return
        except requests.exceptions.RequestException as error:
            logger.error(error)
