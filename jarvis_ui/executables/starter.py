# noinspection PyUnresolvedReferences
"""Module to kick off wake word detection.

>>> Starter

"""

import os
import string
import struct
from importlib import metadata
from multiprocessing.managers import DictProxy  # noqa
from typing import Dict, List, Union

import pvporcupine
from packaging.version import Version
from playsound import playsound
from pyaudio import PyAudio, Stream, paInt16

from jarvis_ui.executables import display, processor, speaker
from jarvis_ui.logger import logger
from jarvis_ui.modules import exceptions, models

assert (
    speaker.driver or models.env.speech_timeout
), "Cannot proceed without both audio drivers and speech timeout."

WAKE_WORD_DETECTOR = metadata.version(pvporcupine.__name__)


def constructor() -> Dict[str, Union[str, List[float], List[str]]]:
    """Construct arguments for wake word detector.

    Returns:
        Dict[str, Union[str, List[float], List[str]]]:
        Arguments for wake word detector constructed as a dictionary based on the system and dependency version.
    """
    arguments = {
        "sensitivities": models.env.sensitivity,
        "keywords": models.env.wake_words,
    }
    if WAKE_WORD_DETECTOR in ("1.9.5", "1.6.0"):
        arguments["library_path"] = pvporcupine.LIBRARY_PATH
        keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in models.env.wake_words]
        if models.settings.legacy:
            arguments["model_file_path"] = pvporcupine.MODEL_PATH
            arguments["keyword_file_paths"] = keyword_paths
        else:
            arguments["model_path"] = pvporcupine.MODEL_PATH
            arguments["keyword_paths"] = keyword_paths
    elif Version(WAKE_WORD_DETECTOR) >= Version("3.0.2"):
        arguments["access_key"] = models.env.porcupine_key
    else:
        # this shouldn't happen by itself
        raise exceptions.DependencyError(
            f"{pvporcupine.__name__} {WAKE_WORD_DETECTOR}\n\tInvalid version\n"
            f"{models.settings.os} is only supported with porcupine versions 1.9.5 or 3.0.2 and above (requires key)"
        )
    return arguments


class Activator:
    """Awaits for the keyword ``Jarvis`` and triggers ``initiator`` when heard.

    >>> Activator

    See Also:
        - Creates an input audio stream from a microphone, monitors it, and detects the specified wake word.
        - After processing the phrase, the converted text is sent as response to the API.
    """

    def __init__(self):
        """Initiates Porcupine object for hot word detection.

        See Also:
            - Instantiates an instance of Porcupine object and monitors audio stream for occurrences of keywords.
            - A higher sensitivity results in fewer misses at the cost of increasing the false alarm rate.
            - sensitivity: Tolerance/Sensitivity level. Takes argument or env var ``sensitivity`` or defaults to ``0.5``

        References:
            - `Audio Overflow <https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream.read>`__ handling.
        """
        self.py_audio = PyAudio()
        self.detector = pvporcupine.create(**constructor())
        self.audio_stream = self.open_stream()
        label = ", ".join(
            [
                f"{string.capwords(wake)!r}: {sens}"
                for wake, sens in zip(models.env.wake_words, models.env.sensitivity)
            ]
        )
        self.label = f"Awaiting: [{label}]"

    def at_exit(self) -> None:
        """Invoked when the run loop is exited or manual interrupt.

        See Also:
            - Releases resources held by porcupine.
            - Closes audio stream.
            - Releases port audio resources.
        """
        self.detector.delete()
        if self.audio_stream and self.audio_stream.is_active():
            self.py_audio.close(stream=self.audio_stream)
            self.audio_stream.close()
        self.py_audio.terminate()

    def open_stream(self) -> Stream:
        """Initializes an audio stream.

        Returns:
            Stream:
            PyAudio stream.
        """
        return self.py_audio.open(
            rate=self.detector.sample_rate,
            channels=1,
            format=paInt16,
            input=True,
            frames_per_buffer=self.detector.frame_length,
            input_device_index=models.env.microphone_index,
        )

    def executor(self, status_manager: DictProxy = None):
        """Closes the audio stream and calls the processor."""
        if status_manager:
            status_manager["LOCKED"] = True
            logger.debug("Restart locked")
        playsound(sound=models.fileio.acknowledgement, block=False)
        self.py_audio.close(stream=self.audio_stream)
        try:
            processor.process(status_manager=status_manager)
        except KeyboardInterrupt:
            self.audio_stream = None
            raise KeyboardInterrupt
        if status_manager:
            status_manager["LOCKED"] = False
            logger.debug("Restart released")
        self.audio_stream = self.open_stream()
        display.write_screen(self.label)

    def start(self, status_manager: DictProxy = None) -> None:
        """Runs ``audio_stream`` in a forever loop and calls ``initiator`` when the phrase ``Jarvis`` is heard."""
        logger.info(
            "Starting wake word detector with sensitivity: %s", models.env.sensitivity
        )
        if os.path.isfile("failed_command"):
            with open("failed_command") as file:
                existing = file.read().strip()
            processor.process(phrase=existing, status_manager=status_manager)
        display.write_screen(self.label)
        while True:
            result = self.detector.process(
                pcm=struct.unpack_from(
                    "h" * self.detector.frame_length,
                    self.audio_stream.read(
                        num_frames=self.detector.frame_length,
                        exception_on_overflow=False,
                    ),
                )
            )
            if result is False or result < 0:
                continue
            self.executor(status_manager=status_manager)
