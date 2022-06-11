# noinspection PyUnresolvedReferences
"""This is a space for environment variables shared across multiple modules validated using pydantic.

>>> Models

"""

import os
import platform
from datetime import datetime
from typing import Union

from pydantic import (BaseModel, BaseSettings, DirectoryPath, Field, FilePath,
                      HttpUrl, PositiveInt)


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    home: DirectoryPath = Field(default=os.path.expanduser("~"), env="HOME")
    request_url: HttpUrl = Field(default=None, env="REQUEST_URL")
    request_timeout: int = Field(default=5, env="REQUEST_TIMEOUT")
    offline_pass: str = Field(default="OfflineComm", env="OFFLINE_PASS")
    sensitivity: Union[float, PositiveInt] = Field(default=0.5, le=1, ge=0, env="SENSITIVITY")
    voice_timeout: Union[float, PositiveInt] = Field(default=3, env="VOICE_TIMEOUT")
    voice_phrase_limit: Union[float, PositiveInt] = Field(default=3, env="VOICE_PHRASE_LIMIT")
    legacy_keywords: list = Field(default=["jarvis"], env="LEGACY_KEYWORDS")
    speech_synthesis_port: int = Field(default=5002, env="SPEECH_SYNTHESIS_PORT")
    speech_synthesis_timeout: int = Field(default=3, env="SPEECH_SYNTHESIS_TIMEOUT")

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = ".env"

    if platform.system() == "Windows":
        macos = 0
    else:
        macos = 1


class FileIO(BaseModel):
    """Loads all the mp3 files' path and log file path required by Jarvis.

    >>> FileIO

    """

    acknowledgement: FilePath = os.path.join('indicators', 'acknowledgement.mp3')
    end: FilePath = os.path.join('indicators', 'end.mp3')
    start: FilePath = os.path.join('indicators', 'start.mp3')
    base_log_file: FilePath = datetime.now().strftime(os.path.join('logs', 'jarvis_%d-%m-%Y.log'))
    speech_log_file: FilePath = datetime.now().strftime(os.path.join('logs', 'speech_synthesis_%d-%m-%Y.log'))


env = EnvConfig()
fileio = FileIO()
