# noinspection PyUnresolvedReferences
"""This is a space for environment variables shared across multiple modules validated using pydantic.

>>> Models

"""

import os
import platform
from datetime import datetime
from typing import Union

from pydantic import (BaseSettings, DirectoryPath, Field, FilePath, HttpUrl,
                      PositiveInt)


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    home: DirectoryPath = Field(default=os.path.expanduser("~"), env="HOME")

    request_url: HttpUrl = Field(default=None, env="REQUEST_URL")
    token: str = Field(default=None, env="TOKEN")

    request_timeout: Union[float, PositiveInt] = Field(default=5, env="REQUEST_TIMEOUT")
    speech_timeout: Union[float, PositiveInt] = Field(default=5, env="SPEECH_TIMEOUT")
    sensitivity: Union[float, PositiveInt] = Field(default=0.5, le=1, ge=0, env="SENSITIVITY")
    voice_timeout: Union[float, PositiveInt] = Field(default=3, env="VOICE_TIMEOUT")
    voice_phrase_limit: Union[float, PositiveInt] = Field(default=3, env="VOICE_PHRASE_LIMIT")
    legacy_wake_words: list = Field(default=["jarvis"], env="LEGACY_WAKE_WORDS")

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = ".env"

    if platform.system() == "Windows":
        macos = 0
    else:
        macos = 1


class FileIO(BaseSettings):
    """Loads all the mp3 files' path and log file path required by Jarvis.

    >>> FileIO

    """

    acknowledgement: FilePath = os.path.join('indicators', 'acknowledgement.wav')
    base_log_file: str = datetime.now().strftime(os.path.join('logs', 'jarvis_%d-%m-%Y.log'))
    speech_wav_file: str = os.path.join('indicators', 'speech-synthesis.wav')


env = EnvConfig()
fileio = FileIO()

if not env.request_url or not env.token:
    raise PermissionError(
        "'REQUEST_URL' or 'TOKEN' not found in environment variables."
    )
if not env.request_url.endswith("/"):
    env.request_url += "/"
