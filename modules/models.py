"""This is a space for environment variables shared across multiple modules validated using pydantic.

>>> EnvConfig
>>> FileIO
>>> Settings

"""

import base64
import binascii
import os
import pathlib
import platform
import string
import sys
import warnings
from datetime import datetime
from enum import Enum
from typing import List, Union

from packaging.version import parse as parser
from pydantic import BaseSettings, Field, FilePath, HttpUrl, PositiveInt

if os.getcwd().endswith("doc_generator"):
    os.chdir(os.path.dirname(os.getcwd()))

UNICODE_PREFIX = base64.b64decode(b'XA==').decode(encoding="ascii") + string.ascii_letters[20] + string.digits[:1] * 2


class Settings(BaseSettings):
    """Loads most common system values.

    >>> Settings

    """

    if platform.system() == "Darwin":
        macos = 1
    else:
        macos = 0
        if platform.system() != "Windows":
            warnings.warn(
                f"Running on un-tested operating system: {platform.system()}.\n"
                "Please raise an issue at https://github.com/thevickypedia/Jarvis_UI/issues/new/choose if found."
            )
    legacy: bool = True if macos and parser(platform.mac_ver()[0]) < parser('10.14') else False
    bot: str = pathlib.PurePath(sys.argv[0]).stem


settings = Settings()


class Sensitivity(float, Enum):
    """Allowed values for sensitivity.

    >>> Sensitivity

    """

    sensitivity: Union[float, PositiveInt]


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    request_url: HttpUrl = Field(default=..., env="REQUEST_URL")
    token: str = Field(default=..., env="TOKEN")

    request_timeout: Union[float, PositiveInt] = Field(default=5, env="REQUEST_TIMEOUT")
    speech_timeout: Union[float, PositiveInt] = Field(default=0, env="SPEECH_TIMEOUT")
    sensitivity: Union[Sensitivity, List[Sensitivity]] = Field(default=0.5, le=1, ge=0, env="SENSITIVITY")
    voice_timeout: Union[float, PositiveInt] = Field(default=3, env="VOICE_TIMEOUT")
    voice_phrase_limit: Union[float, PositiveInt] = Field(default=3, env="VOICE_PHRASE_LIMIT")
    wake_words: list = Field(default=[settings.bot], env="WAKE_WORDS")
    native_audio: bool = Field(default=False, env="NATIVE_AUDIO")

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = ".env"


class FileIO(BaseSettings):
    """Loads all the mp3 files' path and log file path required by Jarvis.

    >>> FileIO

    """

    failed: FilePath = os.path.join('indicators', 'failed.wav')
    shutdown: FilePath = os.path.join('indicators', 'shutdown.wav')
    processing: FilePath = os.path.join('indicators', 'processing.wav')
    unprocessable: FilePath = os.path.join('indicators', 'unprocessable.wav')
    acknowledgement: FilePath = os.path.join('indicators', 'acknowledgement.wav')

    speech_wav_file: Union[FilePath, str] = os.path.join('indicators', 'speech-synthesis.wav')
    base_log_file: Union[FilePath, str] = datetime.now().strftime(os.path.join('logs', 'jarvis_%d-%m-%Y.log'))


env = EnvConfig()
fileio = FileIO()
raw_token = env.token
env.token = UNICODE_PREFIX + UNICODE_PREFIX.join(binascii.hexlify(data=env.token.encode(encoding="utf-8"),
                                                                  sep="-").decode(encoding="utf-8").split(sep="-"))
assert raw_token == bytes(env.token, "utf-8").decode(encoding="unicode_escape")  # Check decoded value before startup
