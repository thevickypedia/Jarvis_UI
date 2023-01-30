# noinspection PyUnresolvedReferences
"""Module for speaker and voice options.

>>> Speaker

"""

from typing import NoReturn

from jarvis_ui.modules.models import audio_driver


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
