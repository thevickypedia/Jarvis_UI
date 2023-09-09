# noinspection PyUnresolvedReferences
"""Module for speaker and voice options.

>>> Speaker

"""

from jarvis_ui.executables import audio_driver

driver = audio_driver.instantiate_audio_driver()


def speak(text: str) -> None:
    """Speak the received text using audio driver.

    Args:
        text: Takes the text that has to be spoken as an argument.
    """
    text = text.replace('\n', '\t').strip()
    if not text.endswith('.') or not text.endswith('!'):
        text = text + '!'
    driver.say(text=text)
    driver.runAndWait()
