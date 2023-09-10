"""This is a space for environment variables shared across multiple modules validated using pydantic."""

import base64
import binascii
import os
import platform
import string
import sys
from collections import ChainMap
from datetime import datetime
from enum import Enum
from typing import List, Union

from packaging.version import parse as parser
from pydantic import (BaseSettings, Field, FilePath, HttpUrl, PositiveFloat,
                      PositiveInt, validator)

from jarvis_ui import indicators
from jarvis_ui.modules.exceptions import UnsupportedOS
from jarvis_ui.modules.peripherals import channel_type, get_audio_devices

if os.getcwd().endswith("doc_generator"):
    os.chdir(os.path.dirname(os.getcwd()))

UNICODE_PREFIX = base64.b64decode(b'XA==').decode(encoding="ascii") + string.ascii_letters[20] + string.digits[:1] * 2


class Settings(BaseSettings):
    """Loads most common system values.

    >>> Settings

    Raises:
        UnsupportedOS:
        If the host operating system is other than Linux, macOS or Windows.
    """

    operating_system: str = platform.system()
    if operating_system not in ["Windows", "Darwin", "Linux"]:
        raise UnsupportedOS(
            f"\n{''.join('*' for _ in range(80))}\n\n"
            "Unsupported Operating System. Currently Jarvis can run only on Mac and Windows OS.\n\n"
            "To raise an issue: https://github.com/thevickypedia/Jarvis/issues/new\n"
            "To reach out: https://vigneshrao.com/contact\n"
            f"\n{''.join('*' for _ in range(80))}\n"
        )
    legacy: bool = True if os == "Darwin" and parser(platform.mac_ver()[0]) < parser('10.14') else False
    if sys.stdin.isatty():
        interactive = True
    else:
        interactive = False


settings = Settings()
# Intermittently changes to Windows_NT because of pydantic
if settings.operating_system.startswith('Windows'):
    settings.operating_system = "Windows"


class Sensitivity(float or PositiveInt, Enum):
    """Allowed values for sensitivity.

    >>> Sensitivity

    """

    sensitivity: Union[float, PositiveInt]


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
    request_url: HttpUrl = Field(default=...)
    token: str = Field(default=...)

    # Heart beat
    heart_beat: int = Field(default=None, le=3_600, ge=5)

    # Speech recognition settings
    recognizer_settings: RecognizerSettings = Field(default=RecognizerSettings())

    debug: bool = Field(default=False)
    microphone_index: Union[int, PositiveInt] = Field(default=None, ge=0)

    speech_timeout: Union[float, PositiveInt] = Field(default=0)
    sensitivity: Union[Sensitivity, List[Sensitivity]] = Field(default=0.5, le=1, ge=0)

    # Built-in speaker config (Unused if speech synthesis is used)
    voice_name: str = Field(default=None)
    voice_rate: Union[PositiveInt, PositiveFloat] = Field(default=None)
    voice_pitch: Union[PositiveInt, PositiveFloat] = Field(default=None)

    listener_timeout: Union[float, PositiveInt] = Field(default=2)
    listener_phrase_limit: Union[float, PositiveInt] = Field(default=5)
    if settings.legacy:
        wake_words: list = Field(default=['alexa'])
    else:
        wake_words: list = Field(default=['jarvis'])
    native_audio: bool = Field(default=False)

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".env"))

    # noinspection PyMethodParameters
    @validator("microphone_index", pre=True, allow_reuse=True)
    def parse_microphone_index(cls, v: Union[int, PositiveInt]) -> Union[int, PositiveInt, None]:
        """Validates microphone index."""
        if not v:
            return
        if int(v) in list(map(lambda tag: tag['index'], get_audio_devices(channels=channel_type.input_channels))):
            return v
        else:
            complicated = dict(ChainMap(*list(map(lambda tag: {tag['index']: tag['name']},
                                                  get_audio_devices(channels=channel_type.input_channels)))))
            raise ValueError(f"value should be one of {complicated}")


env = EnvConfig()


class FileIO(BaseSettings):
    """Loads all the mp3 files' path and log file path required by Jarvis.

    >>> FileIO

    """

    path = indicators.__path__[0]
    extn_ = {"Darwin": "mac", "Windows": "win", "Linux": "ss"}  # Mapping for OS specific pre-recorded audio files

    acknowledgement: FilePath = os.path.join(path, 'acknowledgement.wav')

    if env.speech_timeout and not env.native_audio:
        extn_[settings.operating_system] = "ss"  # Set mapping to use speech synthesis' audio file

    failed: FilePath = os.path.join(path, f'failed_{extn_[settings.operating_system]}.wav')
    restart: FilePath = os.path.join(path, f'restart_{extn_[settings.operating_system]}.wav')
    shutdown: FilePath = os.path.join(path, f'shutdown_{extn_[settings.operating_system]}.wav')
    connection_restart: FilePath = os.path.join(path, f'connection_restart_{extn_[settings.operating_system]}.wav')

    speech_wav_file: Union[FilePath, str] = os.path.join(path, 'speech-synthesis.wav')
    base_log_file: Union[FilePath, str] = datetime.now().strftime(os.path.join('logs', 'jarvis_%d-%m-%Y.log'))


fileio = FileIO()
# because playaudio in Windows uses string concatenation assuming input sound is going to be a string
if settings.operating_system == "Windows":
    for key, value in fileio.__dict__.items():
        if not key.endswith('_'):
            setattr(fileio, key, value.__str__())
raw_token = env.token
env.token = UNICODE_PREFIX + UNICODE_PREFIX.join(binascii.hexlify(data=env.token.encode(encoding="utf-8"),
                                                                  sep="-").decode(encoding="utf-8").split(sep="-"))
assert raw_token == bytes(env.token, "utf-8").decode(encoding="unicode_escape")  # Check decoded value before startup
