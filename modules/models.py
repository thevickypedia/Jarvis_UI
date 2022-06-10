# noinspection PyUnresolvedReferences
"""This is a space for environment variables shared across multiple modules validated using pydantic.

>>> Models

"""

import os
import platform
from typing import Union

from pydantic import (BaseModel, BaseSettings, Field,
                      FilePath, PositiveInt, DirectoryPath, HttpUrl)


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    home: DirectoryPath = Field(default=os.path.expanduser("~"), env="HOME")
    request_url: HttpUrl = Field(default=None, env="REQUEST_URL")
    request_timeout: int = Field(default=5, env="REQUEST_TIMEOUT")
    offline_pass: str = Field(default="OfflineComm", env="OFFLINE_PASS")
    sensitivity: Union[float, PositiveInt] = Field(default=0.5, le=1, ge=0, env="SENSITIVITY")
    timeout: Union[float, PositiveInt] = Field(default=3, env="TIMEOUT")
    phrase_limit: Union[float, PositiveInt] = Field(default=3, env="PHRASE_LIMIT")
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


class Indicators(BaseModel):
    """Loads all the mp3 files' path required by Jarvis.

    >>> Indicators

    """

    acknowledgement: FilePath = os.path.join('indicators', 'acknowledgement.mp3')
    end: FilePath = os.path.join('indicators', 'end.mp3')
    start: FilePath = os.path.join('indicators', 'start.mp3')


env = EnvConfig()
indicators = Indicators()
