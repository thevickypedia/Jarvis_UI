# noinspection PyUnresolvedReferences
"""Module for speaker and voice options.

>>> Speaker

"""

from jarvis_ui.modules.models import audio_driver


def speak(text: str) -> None:
    """Speak the received text using audio driver.

    Args:
        text: Takes the text that has to be spoken as an argument.
    """
    text = text.replace('\n', '\t').strip()
    if not text.endswith('.') or not text.endswith('!'):
        text = text + '!'
    audio_driver.say(text=text)
    audio_driver.runAndWait()
