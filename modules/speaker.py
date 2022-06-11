# noinspection PyUnresolvedReferences
"""Module for speaker and voice options.

>>> Speaker

"""

import os
from typing import NoReturn

import pyttsx3
from playsound import playsound

from modules.api_handler import make_request
from modules.logger import logger
from modules.models import env, fileio

audio_driver = pyttsx3.init()
voices = audio_driver.getProperty("voices")  # gets the list of voices available
voice_model = "Daniel" if env.macos else "David"
for ind_d, voice_id in enumerate(voices):  # noqa
    if voice_id.name == voice_model or voice_model in voice_id.name:
        audio_driver.setProperty("voice", voices[ind_d].id)  # noqa
        break
else:
    logger.info("Using default voice model.")


def speak(text: str = None, run: bool = False) -> NoReturn:
    """Calls ``audio_driver.say`` to speak a statement from the received text.

    Args:
        text: Takes the text that has to be spoken as an argument.
        run: Takes a boolean flag to choose whether to run the ``audio_driver.say`` loop.
    """
    if text:
        text = text.replace('\n', '\t').strip()
        if make_request(path=f"speech-synthesis?text={text}", timeout=env.request_timeout + 3):
            playsound(sound=fileio.speech_wav_file, block=True)
            os.remove(fileio.speech_wav_file)
        else:
            audio_driver.say(text=text)
    if run:
        audio_driver.runAndWait()
