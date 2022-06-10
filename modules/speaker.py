# noinspection PyUnresolvedReferences
"""Module for speaker and voice options.

>>> Speaker

"""

import os
from typing import NoReturn

import pyttsx3
import requests
from playsound import playsound
from modules.logger import logger

from modules.models import env

audio_driver = pyttsx3.init()
voices = audio_driver.getProperty("voices")  # gets the list of voices available
voice_model = "Daniel" if env.macos else "David"
for ind_d, voice_id in enumerate(voices):  # noqa
    if voice_id.name == voice_model or voice_model in voice_id.name:
        audio_driver.setProperty("voice", voices[ind_d].id)  # noqa
        break
else:
    logger.info("Using default voice model.")


def speech_synthesizer(text: str, timeout: int = env.speech_synthesis_timeout) -> bool:
    """Makes a post call to docker container running on localhost for speech synthesis.

    Args:
        text: Takes the text that has to be spoken as an argument.
        timeout: Time to wait for the docker image to process text-to-speech request.

    Returns:
        bool:
        A boolean flag to indicate whether speech synthesis has worked.
    """
    try:
        response = requests.post(url=f"http://localhost:{env.speech_synthesis_port}/api/tts",
                                 headers={"Content-Type": "text/plain"},
                                 params={"voice": "en-us_northern_english_male-glow_tts", "quality": "medium"},
                                 data=text, verify=False, timeout=timeout)
        if not response.ok:
            return False
        with open(file="speech_synthesis.wav", mode="wb") as file:
            file.write(response.content)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
        logger.error(error)


def speak(text: str = None, run: bool = False) -> NoReturn:
    """Calls ``audio_driver.say`` to speak a statement from the received text.

    Args:
        text: Takes the text that has to be spoken as an argument.
        run: Takes a boolean flag to choose whether to run the ``audio_driver.say`` loop.
    """
    if text:
        text = text.replace('\n', '\t').strip()
        if speech_synthesizer(text=text) and os.path.isfile("speech_synthesis.wav"):
            playsound(sound="speech_synthesis.wav", block=True)
            os.remove("speech_synthesis.wav")
        else:
            audio_driver.say(text=text)
    if run:
        audio_driver.runAndWait()
