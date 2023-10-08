import pathlib

import pyttsx3

from jarvis_ui.modules.exceptions import InvalidEnvVars
from jarvis_ui.modules.logger import logger
from jarvis_ui.modules.models import env, fileio, settings


def reload_static_files() -> None:
    """Iterates through ``FileIO`` objects and converts all preloaded audio files to speech-synthesis audio files."""
    extn = fileio.extn_[settings.operating_system]
    if extn == "ss":
        return
    for key, value in fileio.__dict__.items():
        value = str(value)
        if value.endswith(f"{extn}.wav"):
            value = value.replace(f"{extn}.wav", "ss.wav")
            # because playaudio in Windows uses string concatenation assuming input sound is going to be a string
            if settings.operating_system != "Windows":
                value = pathlib.PosixPath(value)
            setattr(fileio, key, value)


def instantiate_audio_driver() -> pyttsx3.Engine:
    """Instantiates the audio driver and sets voice.

    Returns:
        pyttsx3.Engine:
        Returns instance of audio engine.
    """
    driver = pyttsx3.init()
    voices = driver.getProperty("voices")  # gets the list of voices available
    voice_names = [__voice.name for __voice in voices]
    if not env.voice_name:
        if settings.operating_system == "Darwin":
            env.voice_name = "Daniel"
        elif settings.operating_system == "Windows":
            env.voice_name = "David"
        elif settings.operating_system == "Linux":
            env.voice_name = "english-us"
    elif env.voice_name not in voice_names:
        raise InvalidEnvVars(
            f"\n\nVoice name {env.voice_name!r} is not available.\nAvailable voices:\n\t{', '.join(voice_names)}"
        )
    for ind_d, voice in enumerate(voices):
        if voice.name == env.voice_name:
            logger.debug(voice.__dict__)
            driver.setProperty("voice", voices[ind_d].id)
            if env.voice_rate:
                driver.setProperty("rate", env.voice_rate)
            if env.voice_pitch:
                driver.setProperty("pitch", env.voice_pitch)
            break
    else:
        logger.info("Using default voice model.")
    return driver
