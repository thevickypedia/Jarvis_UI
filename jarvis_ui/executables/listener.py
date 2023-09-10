# noinspection PyUnresolvedReferences
"""Module for listener and speech recognition.

>>> Listener

"""

from typing import Union

import requests
from pydantic import PositiveFloat, PositiveInt
from speech_recognition import (Microphone, Recognizer, RequestError,
                                UnknownValueError, WaitTimeoutError)

from jarvis_ui.executables import display
from jarvis_ui.modules.logger import logger
from jarvis_ui.modules.models import env

recognizer = Recognizer()  # initiates recognizer object
microphone = Microphone()  # initiates microphone object

recognizer.energy_threshold = env.recognizer_settings.energy_threshold
recognizer.pause_threshold = env.recognizer_settings.pause_threshold
recognizer.phrase_threshold = env.recognizer_settings.phrase_threshold
recognizer.dynamic_energy_threshold = env.recognizer_settings.dynamic_energy_threshold
recognizer.non_speaking_duration = env.recognizer_settings.non_speaking_duration


def listen(timeout: Union[PositiveInt, PositiveFloat] = env.listener_timeout,
           phrase_time_limit: Union[PositiveInt, PositiveFloat] = env.listener_phrase_limit) -> Union[str, None]:
    """Function to activate listener and get the user input.

    Args:
        timeout: Time in seconds to wait for a phrase/sound to begin.
        phrase_time_limit: Time in seconds to await user input. Anything spoken beyond this limit will be excluded.

    Returns:
        str:
        Returns the recognized statement listened via microphone.
    """
    return_val = None
    with microphone as source:
        display.write_screen(f"Listener activated [{timeout}: {phrase_time_limit}]")
        try:
            listened = recognizer.listen(source=source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return_val = recognizer.recognize_google(audio_data=listened)
        except (UnknownValueError, WaitTimeoutError, RequestError) as error:
            logger.debug(error)
        except requests.exceptions.RequestException as error:
            logger.error(error)
        display.flush_screen()
        return return_val
