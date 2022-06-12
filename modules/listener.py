import sys
from typing import Union

import requests
from speech_recognition import (Microphone, Recognizer, RequestError,
                                UnknownValueError, WaitTimeoutError)

from modules.logger import logger

recognizer = Recognizer()  # initiates recognizer that uses google's translation


def listen(timeout: Union[int, float], phrase_limit: Union[int, float], stdout: bool = True) -> Union[str, None]:
    """Function to activate listener, this function will be called by most upcoming functions to listen to user input.

    Args:
        timeout: Time in seconds for the overall listener to be active.
        phrase_limit: Time in seconds for the listener to actively listen to a sound.
        stdout: Flag whether to print the listener status on the screen.

    Returns:
        str:
         - Returns recognized statement from the microphone.
    """
    with Microphone() as source:
        sys.stdout.write("\rListener activated..") if stdout else sys.stdout.flush()
        try:
            listened = recognizer.listen(source=source, timeout=timeout, phrase_time_limit=phrase_limit)
            sys.stdout.write("\r") if stdout else sys.stdout.flush()
            return recognizer.recognize_google(audio_data=listened)
        except (UnknownValueError, WaitTimeoutError, RequestError):
            return
        except requests.exceptions.RequestException as error:
            logger.error(error)
