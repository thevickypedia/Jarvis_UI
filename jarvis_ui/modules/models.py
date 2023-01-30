"""This is a space for environment variables shared across multiple modules validated using pydantic."""

import base64
import binascii
import os
import platform
import string
from collections import ChainMap
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

import pyttsx3
from packaging.version import parse as parser
from pydantic import (BaseSettings, Field, FilePath, HttpUrl, PositiveFloat,
                      PositiveInt, validator)

from jarvis_ui import indicators
from jarvis_ui.modules.exceptions import UnsupportedOS
from jarvis_ui.modules.peripherals import channel_type, get_audio_devices

audio_driver = pyttsx3.init()
if os.getcwd().endswith("doc_generator"):
    os.chdir(os.path.dirname(os.getcwd()))

UNICODE_PREFIX = base64.b64decode(b'XA==').decode(encoding="ascii") + string.ascii_letters[20] + string.digits[:1] * 2


class Flag(str, Enum):
    """Enum flags for restart and stop.

    >>> Flag

    """

    stop: str = "STOP"
    restart: str = "RESTART"


flag = Flag


class Settings(BaseSettings):
    """Loads most common system values.

    >>> Settings

    Raises:
        UnsupportedOS:
        If the host operating system is other than Linux, macOS or Windows.
    """

    os: str = platform.system()
    if os not in ["Windows", "Darwin", "Linux"]:
        raise UnsupportedOS(
            f"\n{''.join('*' for _ in range(80))}\n\n"
            "Unsupported Operating System. Currently Jarvis can run only on Mac and Windows OS.\n\n"
            "To raise an issue: https://github.com/thevickypedia/Jarvis/issues/new\n"
            "To reach out: https://vigneshrao.com/contact\n"
            f"\n{''.join('*' for _ in range(80))}\n"
        )
    legacy: bool = True if os == "Darwin" and parser(platform.mac_ver()[0]) < parser('10.14') else False
    bot: str = "jarvis"
    wake_words: Optional[List[str]]


settings = Settings()


class Sensitivity(float or PositiveInt, Enum):
    """Allowed values for sensitivity.

    >>> Sensitivity

    """

    sensitivity: Union[float, PositiveInt]


class RestartTimer(float or PositiveInt, Enum):
    """Allowed values for restart_timer.

    >>> RestartTimer

    """

    restart_timer: Union[float, PositiveInt]


class RecognizerSettings(BaseSettings):
    """Settings for speech recognition.

    >>> RecognizerSettings

    """

    energy_threshold: PositiveInt = 1100
    pause_threshold: Union[PositiveInt, float] = 1
    phrase_threshold: Union[PositiveInt, float] = 0.1
    dynamic_energy_threshold: bool = False
    non_speaking_duration: Union[PositiveInt, float] = 1


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    # Required env vars
    request_url: HttpUrl = Field(default=..., env="REQUEST_URL")
    token: str = Field(default=..., env="TOKEN")

    # Speech recognition settings
    recognizer_settings: RecognizerSettings = Field(default=None, env="RECOGNIZER_SETTINGS")
    recognizer_settings_default: RecognizerSettings = RecognizerSettings()

    restart_timer: RestartTimer = Field(default=86_400, le=172_800, ge=1_800, env="RESTART_TIMER")
    restart_attempts: int = Field(default=5, gt=1, le=10, env="RESTART_ATTEMPTS")
    debug: bool = Field(default=False, env="DEBUG")
    microphone_index: Union[int, PositiveInt] = Field(default=None, ge=0, env='MICROPHONE_INDEX')

    request_timeout: Union[float, PositiveInt] = Field(default=5, env="REQUEST_TIMEOUT")
    speech_timeout: Union[float, PositiveInt] = Field(default=0, env="SPEECH_TIMEOUT")
    sensitivity: Union[Sensitivity, List[Sensitivity]] = Field(default=0.5, le=1, ge=0, env="SENSITIVITY")

    # Built-in speaker config (Unused if speech synthesis is used)
    voice_name: str = Field(default=None, env='VOICE_NAME')
    voice_rate: Union[PositiveInt, PositiveFloat] = Field(default=audio_driver.getProperty("rate"), env='VOICE_RATE')

    voice_timeout: Union[float, PositiveInt] = Field(default=3, env="VOICE_TIMEOUT")
    voice_phrase_limit: Union[float, PositiveInt] = Field(default=None, env="VOICE_PHRASE_LIMIT")
    if settings.legacy:
        wake_words: list = Field(default=['alexa'], env="WAKE_WORDS")
    else:
        wake_words: list = Field(default=[settings.bot], env="WAKE_WORDS")
    native_audio: bool = Field(default=False, env="NATIVE_AUDIO")

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = ".env"

    # noinspection PyMethodParameters
    @validator("microphone_index", pre=True, allow_reuse=True)
    def parse_microphone_index(cls, value: Union[int, PositiveInt]) -> Union[int, PositiveInt, None]:
        """Validates microphone index."""
        if not value:
            return
        if int(value) in list(map(lambda tag: tag['index'], get_audio_devices(channels=channel_type.input_channels))):
            return value
        else:
            complicated = dict(ChainMap(*list(map(lambda tag: {tag['index']: tag['name']},
                                                  get_audio_devices(channels=channel_type.input_channels)))))
            raise ValueError(f"value should be one of {complicated}")


class FileIO(BaseSettings):
    """Loads all the mp3 files' path and log file path required by Jarvis.

    >>> FileIO

    """

    failed: FilePath = os.path.join(indicators.__path__[0], 'failed.wav')
    restart: FilePath = os.path.join(indicators.__path__[0], 'restart.wav')
    shutdown: FilePath = os.path.join(indicators.__path__[0], 'shutdown.wav')
    processing: FilePath = os.path.join(indicators.__path__[0], 'processing.wav')
    unprocessable: FilePath = os.path.join(indicators.__path__[0], 'unprocessable.wav')
    acknowledgement: FilePath = os.path.join(indicators.__path__[0], 'acknowledgement.wav')

    speech_wav_file: Union[FilePath, str] = os.path.join(indicators.__path__[0], 'speech-synthesis.wav')
    base_log_file: Union[FilePath, str] = datetime.now().strftime(os.path.join('logs', 'jarvis_%d-%m-%Y.log'))


env = EnvConfig()
fileio = FileIO()
raw_token = env.token
env.token = UNICODE_PREFIX + UNICODE_PREFIX.join(binascii.hexlify(data=env.token.encode(encoding="utf-8"),
                                                                  sep="-").decode(encoding="utf-8").split(sep="-"))
assert raw_token == bytes(env.token, "utf-8").decode(encoding="unicode_escape")  # Check decoded value before startup
