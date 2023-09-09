import importlib
import pathlib
import subprocess
from multiprocessing import current_process
from threading import Thread
from typing import Dict

import pyttsx3

from jarvis_ui.modules.exceptions import InvalidEnvVars, SegmentationError
from jarvis_ui.modules.logger import logger
from jarvis_ui.modules.models import env, fileio, settings

module: Dict[str, pyttsx3.Engine] = {}


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


def import_module() -> None:
    """Instantiates pyttsx3 after importing ``nsss`` drivers beforehand."""
    if settings.operating_system == "Darwin":
        importlib.import_module("pyttsx3.drivers.nsss")
    module['pyttsx3'] = pyttsx3.init()


def get_driver() -> pyttsx3.Engine:
    """Get audio driver by instantiating pyttsx3.

    Returns:
        pyttsx3.Engine:
        Audio driver.
    """
    try:
        subprocess.run(["python3", "-c", "import pyttsx3; pyttsx3.init()"], check=True)
    except subprocess.CalledProcessError as error:
        if error.returncode == -11:  # Segmentation fault error code
            if current_process().name == "MainProcess":
                print(f"\033[91mERROR:{'':<6}Segmentation fault when loading audio driver "
                      "(interrupted by signal 11: SIGSEGV)\033[0m")
                print(f"\033[93mWARNING:{'':<4}Trying alternate solution...\033[0m")
            thread = Thread(target=import_module)
            thread.start()
            thread.join(timeout=10)
            if module.get('pyttsx3'):
                if current_process().name == "MainProcess":
                    print(f"\033[92mINFO:{'':<7}Instantiated audio driver successfully\033[0m")
                return module['pyttsx3']
            else:
                raise SegmentationError(
                    "Segmentation fault when loading audio driver (interrupted by signal 11: SIGSEGV)"
                )
        else:
            return pyttsx3.init()
    else:
        return pyttsx3.init()


def instantiate_audio_driver() -> pyttsx3.Engine:
    """Instantiates the audio driver and sets voice.

    Returns:
        pyttsx3.Engine:
        Returns instance of audio engine.
    """
    try:
        if settings.operating_system == "Windows":
            driver = pyttsx3.init()
        else:
            driver = get_driver()
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
    except (SegmentationError, Exception):  # resolve to speech-synthesis
        env.speech_timeout = 10
        reload_static_files()
        logger.warning("Failed to load the audio driver. Resolving to use SpeechSynthesis")
