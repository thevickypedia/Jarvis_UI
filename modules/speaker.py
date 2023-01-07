# noinspection PyUnresolvedReferences
"""Module for speaker and voice options.

>>> Speaker

Raises:
    InvalidEnvVars:
    If the voice name is not present for the OperatingSystem.
"""

from typing import NoReturn, Union

from modules.exceptions import InvalidEnvVars
from modules.logger import logger
from modules.models import audio_driver, env, settings

voices: Union[list, object] = audio_driver.getProperty("voices")  # gets the list of voices available
voice_names = [__voice.name for __voice in voices]
if not env.voice_name:
    if settings.os == "Darwin":
        env.voice_name = "Daniel"
    elif settings.os == "Windows":
        env.voice_name = "David"
    elif settings.os == "Linux":
        env.voice_name = "english-us"
elif env.voice_name not in voice_names:
    raise InvalidEnvVars(
        f"{env.voice_name!r} is not available.\nAvailable voices are: {', '.join(voice_names)}"
    )
for ind_d, voice in enumerate(voices):  # noqa
    if voice.name == env.voice_name:
        logger.debug(voice.__dict__)
        audio_driver.setProperty("voice", voices[ind_d].id)
        audio_driver.setProperty("rate", env.voice_rate)
        break
else:
    logger.info("Using default voice model.")


def speak(text: str) -> NoReturn:
    """Calls ``audio_driver.say`` to speak a statement from the received text.

    Args:
        text: Takes the text that has to be spoken as an argument.
    """
    text = text.replace('\n', '\t').strip()
    if not text.endswith('.') or not text.endswith('!'):
        text = text + '!'
    audio_driver.say(text=text)
    audio_driver.runAndWait()
