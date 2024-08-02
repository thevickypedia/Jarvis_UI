"""This is a space for configuration required by the API module.

>>> Config

"""
import os
import platform
import warnings
from multiprocessing import current_process
from typing import Callable

import pvporcupine
from pydantic import PositiveInt

from jarvis_ui.executables.api_handler import make_request
from jarvis_ui.logger import logger
from jarvis_ui.modules.models import env, settings

add_ss_extn: Callable = (
    lambda filepath: os.path.splitext(filepath)[0]
    + "_ss"
    + os.path.splitext(filepath)[1]
)


class Config:
    """Gets keywords during start up. Runs custom validations on env-vars.

    >>> Config

    Raises:
        InvalidEnvVars:
        If the voice name is not present for the OperatingSystem.
    """

    if env.voice_pitch and settings.operating_system in ("Windows", "Darwin"):
        warnings.warn(
            "Voice pitch adjustment is currently supported only in Linux operating system."
        )
        env.voice_pitch = None
    env.server_url = str(env.server_url)

    if isinstance(env.sensitivity, float) or isinstance(env.sensitivity, PositiveInt):
        env.sensitivity = [env.sensitivity] * len(env.wake_words)
    if keywords := make_request(path="keywords", method="GET"):
        logger.info("keywords have been loaded")

    if keywords:
        keywords = sum([v for _, v in keywords.items()], [])

    if env.speech_timeout and env.native_audio:
        warnings.warn(
            "Both `speech-synthesis` and `native-audio` cannot be enabled simultaneously.\n"
            "Speech synthesis uses third-party tts service where as `native_audio` preserves the audio from server.\n"
            "Disabling speech synthesis!!"
        )
        env.speech_timeout = 0

    if settings.legacy:
        pvporcupine.KEYWORD_PATHS = {}
        pvporcupine.MODEL_PATH = os.path.join(
            os.path.dirname(pvporcupine.__file__), "lib/common/porcupine_params.pv"
        )
        pvporcupine.LIBRARY_PATH = os.path.join(
            os.path.dirname(pvporcupine.__file__),
            f"lib/mac/{platform.machine()}/libpv_porcupine.dylib",
        )
        keyword_files = os.listdir(
            os.path.join(
                os.path.dirname(pvporcupine.__file__), "resources/keyword_files/mac/"
            )
        )
        for x in keyword_files:
            pvporcupine.KEYWORD_PATHS[x.split("_")[0]] = os.path.join(
                os.path.dirname(pvporcupine.__file__),
                f"resources/keyword_files/mac/{x}",
            )

    for keyword in env.wake_words:
        if keyword == "sphinx-build":
            break
        if not pvporcupine.KEYWORD_PATHS.get(keyword) or not os.path.isfile(
            pvporcupine.KEYWORD_PATHS[keyword]
        ):
            raise ValueError(
                f"Detecting '{keyword}' is unsupported!\n"
                f"Available keywords are: {', '.join(list(pvporcupine.KEYWORD_PATHS.keys()))}"
            )


logger.info("Current Process: %s", current_process().name)
if current_process().name != "MainProcess" or settings.operating_system == "Linux":
    config = Config()  # Run validations only on SyncManager and child process
else:
    config = None
