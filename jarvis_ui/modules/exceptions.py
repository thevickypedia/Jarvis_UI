import ctypes
from contextlib import contextmanager
from typing import ByteString, Iterable, NoReturn

ALSA_ERROR_HANDLER = ctypes.CFUNCTYPE(None,
                                      ctypes.c_char_p,
                                      ctypes.c_int,
                                      ctypes.c_char_p,
                                      ctypes.c_int,
                                      ctypes.c_char_p)


# noinspection PyUnusedLocal
def py_error_handler(filename: ByteString, line: int, function: ByteString, err: int, fmt: ByteString) -> NoReturn:
    """Handles errors from pyaudio module especially for Linux based operating systems."""
    pass


c_error_handler = ALSA_ERROR_HANDLER(py_error_handler)


@contextmanager
def no_alsa_err() -> Iterable:
    """Wrapper to suppress ALSA error messages when ``PyAudio`` module is called.

    Notes:
        - This happens specifically for Linux based operating systems.
        - There are usually multiple sound APIs to choose from but not all of them might be configured correctly.
        - PyAudio goes through "ALSA", "PulseAudio" and "Jack" looking for audio hardware and that triggers warnings.
        - None of the options below seemed to work in all given conditions, so the approach taken was to hide them.

    Options:
        - Comment off the ALSA devices where the error is triggered.
        - Set energy threshold to the output from ``python -m speech_recognition``
        - Setting dynamic energy threshold to ``True``

    References:
        - https://github.com/Uberi/speech_recognition/issues/100
        - https://github.com/Uberi/speech_recognition/issues/182
        - https://github.com/Uberi/speech_recognition/issues/191
        - https://forums.raspberrypi.com/viewtopic.php?t=136974
    """
    sound = ctypes.cdll.LoadLibrary('libasound.so')
    sound.snd_lib_error_set_handler(c_error_handler)
    yield
    sound.snd_lib_error_set_handler(None)


class UnsupportedOS(OSError):
    """Custom ``OSError`` raised when initiated in an unsupported operating system.

    >>> UnsupportedOS

    """


class InvalidEnvVars(ValueError):
    """Custom ``InvalidEnvVars`` raised when invalid env vars are passed.

    >>> InvalidEnvVars

    """


class APIError(ConnectionError):
    """Custom ``APIError`` raised when the UI is unable to connect to the API.

    >>> APIError

    """
