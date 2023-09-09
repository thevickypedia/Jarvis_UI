# noinspection PyUnresolvedReferences
"""Module to kick off wake word detection.

>>> Starter

"""

import os
import string
import struct
from multiprocessing import Process
from multiprocessing.managers import DictProxy  # noqa
from threading import Timer
from typing import Union

import pvporcupine
from playsound import playsound
from pyaudio import PyAudio, Stream, paInt16

from jarvis_ui.executables import display, listener, speaker
from jarvis_ui.executables.api_handler import make_request
from jarvis_ui.executables.helper import linux_restart
from jarvis_ui.modules.config import config
from jarvis_ui.modules.logger import logger
from jarvis_ui.modules.models import env, fileio, settings

assert speaker.driver or env.speech_timeout, "Cannot proceed without both audio drivers and speech timeout."


def process_request(phrase: str) -> Union[str, None]:
    """Process request from the user.

    Args:
        phrase: Takes the phrase spoken as an argument.

    Returns:
        str:
        Returns the appropriate action to be taken.
    """
    logger.info("Request: %s", phrase)
    display.write_screen(f"Request: {phrase}")
    if "restart" in phrase.lower():
        logger.info("User requested to restart.")
        playsound(sound=fileio.restart)
        display.write_screen("Restarting...")
        return "RESTART"
    if "stop running" in phrase.lower():
        logger.info("User requested to stop.")
        playsound(sound=fileio.shutdown)
        display.write_screen("Shutting down")
        return "STOP"
    if not config.keywords:
        logger.warning("keywords are not loaded yet, restarting")
        if os.path.isfile("failed_command"):
            logger.critical("Consecutive failure")
            os.remove("failed_command")
        else:
            with open("failed_command", "w") as file:
                file.write(phrase)
            playsound(sound=fileio.connection_restart)
        display.write_screen("Trying to re-establish connection with Server...")
        return "RESTART"
    if os.path.isfile("failed_command"):
        logger.info("Recovered after a recent failure, deleting placeholder file.")
        os.remove("failed_command")
    if response := make_request(path='offline-communicator',
                                data={'command': phrase, 'native_audio': env.native_audio,
                                      'speech_timeout': env.speech_timeout}):
        process_response(response)
    else:
        playsound(sound=fileio.failed)
        return "RESTART"


def process_response(response: Union[dict, bool]) -> None:
    """Processes response from the server.

    Args:
        response: Takes either a boolean flag or a dictionary from the server as an argument.
    """
    if response is True:
        logger.info("Response received as audio.")
        display.write_screen("Response received as audio.")
        # Because Windows runs into PermissionError if audio file is open when file is removed
        if settings.operating_system == "Windows":
            player = Process(target=playsound, kwargs={'sound': fileio.speech_wav_file})
            player.start()
            player.join()
            if player.is_alive():
                player.terminate()
                player.kill()
            Timer(interval=3, function=os.remove, args=(fileio.speech_wav_file,)).start()
        else:
            playsound(sound=fileio.speech_wav_file)
            os.remove(fileio.speech_wav_file)
        return
    response = response.get('detail', '')
    logger.info("Response: %s", response)
    display.write_screen(f"Response: {response}")
    speaker.speak(text=response)


def processor(phrase: str = None, status_manager: DictProxy = None) -> None:
    """Handles request and response.

    Args:
        phrase: Takes existing phrase as an argument in case a previous failure is pending tobe addressed.
        status_manager: Multiprocessing dictionary to set restarts.
    """
    if phrase := (phrase or listener.listen()):
        processed = process_request(phrase)
        if processed == "STOP":
            raise KeyboardInterrupt
        if processed == "RESTART":
            if settings.operating_system == "Linux":
                linux_restart()
            status_manager["LOCKED"] = None
            while True:
                pass  # To ensure the listener doesn't end so that, the main process can kill and restart


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
        keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in env.wake_words]
        self.py_audio = PyAudio()
        arguments = {
            "library_path": pvporcupine.LIBRARY_PATH,
            "sensitivities": env.sensitivity
        }
        if settings.legacy:
            arguments["keywords"] = env.wake_words
            arguments["model_file_path"] = pvporcupine.MODEL_PATH
            arguments["keyword_file_paths"] = keyword_paths
        else:
            arguments["model_path"] = pvporcupine.MODEL_PATH
            arguments["keyword_paths"] = keyword_paths

        self.detector = pvporcupine.create(**arguments)
        self.audio_stream = self.open_stream()
        label = ', '.join([f'{string.capwords(wake)!r}: {sens}' for wake, sens in
                           zip(env.wake_words, env.sensitivity)])
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
            input_device_index=env.microphone_index
        )

    def executor(self, status_manager: DictProxy = None):
        """Closes the audio stream and calls the processor."""
        if status_manager:
            status_manager["LOCKED"] = True
            logger.debug("Restart locked")
        playsound(sound=fileio.acknowledgement, block=False)
        self.py_audio.close(stream=self.audio_stream)
        try:
            processor(status_manager=status_manager)
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
        logger.info("Starting wake word detector with sensitivity: %s", env.sensitivity)
        if os.path.isfile("failed_command"):
            with open("failed_command") as file:
                existing = file.read().strip()
            processor(phrase=existing, status_manager=status_manager)
        display.write_screen(self.label)
        while True:
            result = self.detector.process(
                pcm=struct.unpack_from("h" * self.detector.frame_length,
                                       self.audio_stream.read(num_frames=self.detector.frame_length,
                                                              exception_on_overflow=False))
            )
            if result is False or result < 0:
                continue
            self.executor(status_manager=status_manager)
