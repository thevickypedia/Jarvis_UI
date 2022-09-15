import os
import struct
import sys
from datetime import datetime
from typing import NoReturn

import pvporcupine
from pyaudio import PyAudio, Stream, paInt16

from modules import listener, speaker
from modules.api_handler import make_request
from modules.config import config
from modules.logger import logger
from modules.models import env, fileio, settings
from modules.playsound import playsound


def processor() -> bool:
    """Processes the request after wake word is detected.

    Returns:
        bool:
        Returns a ``True`` flag if a manual stop is requested.
    """
    if phrase := listener.listen(timeout=env.voice_timeout, phrase_limit=env.voice_phrase_limit):
        logger.info(f"Request: {phrase}")
        sys.stdout.write(f"\rRequest: {phrase}")
        if "stop running" in phrase.lower():
            logger.info("User requested to stop.")
            playsound(sound=fileio.shutdown)
            return True
        if not any(word in phrase.lower() for word in config.keywords + config.conversation):
            logger.warning(f"'{phrase}' is not a part of recognized keywords or conversation.")
            return False
        if not any(word in phrase.lower() for word in config.api_compatible['compatible']):
            logger.warning(f"'{phrase}' is not a part of API compatible request.")
            playsound(sound=fileio.unprocessable)
            return False
        if any(word in phrase.lower() for word in config.delay_with_ack + config.delay_without_ack):
            logger.info(f"Increasing timeout for: {phrase}")
            timeout = 30
            if any(word in phrase.lower() for word in config.delay_with_ack):
                playsound(sound=fileio.processing, block=False)
        else:
            timeout = env.request_timeout
        if response := make_request(path='offline-communicator', timeout=timeout,
                                    data={'command': phrase, 'native_audio': env.native_audio}):
            if env.native_audio:
                logger.info("Response received as audio.")
                sys.stdout.write("\rResponse received as audio.")
                playsound(sound=fileio.speech_wav_file)
                os.remove(fileio.speech_wav_file)
                return False
            response = response.get('detail', '').replace("\N{DEGREE SIGN}F", " degrees fahrenheit").replace("\n", ". ")
            logger.info(f"Response: {response}")
            sys.stdout.write(f"\rResponse: {response}")
            speaker.speak(text=response)
        else:
            playsound(sound=fileio.failed)


class Activator:
    """Awaits for the keyword ``Jarvis`` and triggers ``initiator`` when heard.

    >>> Activator

    See Also:
        - Creates an input audio stream from a microphone, monitors it, and detects the specified wake word.
        - Once detected, Jarvis triggers the ``listener.listen()`` function with an ``acknowledgement`` sound played.
        - After processing the phrase, the converted text is sent as response to the API.
    """

    def __init__(self, input_device_index: int = None):
        """Initiates Porcupine object for hot word detection.

        Args:
            input_device_index: Index of Input Device to use.

        See Also:
            - Instantiates an instance of Porcupine object and monitors audio stream for occurrences of keywords.
            - A higher sensitivity results in fewer misses at the cost of increasing the false alarm rate.
            - sensitivity: Tolerance/Sensitivity level. Takes argument or env var ``sensitivity`` or defaults to ``0.5``

        References:
            - `Audio Overflow <https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream.read>`__ handling.
        """
        keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in env.wake_words]
        self.input_device_index = input_device_index

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

    def __del__(self) -> NoReturn:
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
            input_device_index=self.input_device_index
        )

    def executor(self):
        """Closes the audio stream and calls the processor."""
        logger.debug(f"Detected {settings.bot} at {datetime.now()}")
        playsound(sound=fileio.acknowledgement, block=False)
        self.py_audio.close(stream=self.audio_stream)
        if processor():
            self.audio_stream = None
            raise KeyboardInterrupt
        self.audio_stream = self.open_stream()

    def start(self) -> NoReturn:
        """Runs ``audio_stream`` in a forever loop and calls ``initiator`` when the phrase ``Jarvis`` is heard."""
        logger.info(f"Starting wake word detector with sensitivity: {env.sensitivity}")
        while True:
            sys.stdout.write(f"\rAwaiting: [{', '.join(env.wake_words).upper()}]")
            pcm = struct.unpack_from("h" * self.detector.frame_length,
                                     self.audio_stream.read(num_frames=self.detector.frame_length,
                                                            exception_on_overflow=False))
            result = self.detector.process(pcm=pcm)
            if settings.legacy:
                if len(env.wake_words) == 1 and result:
                    settings.bot = env.wake_words[0]
                    self.executor()
                elif len(env.wake_words) > 1 and result >= 0:
                    settings.bot = env.wake_words[result]
                    self.executor()
            else:
                if result >= 0:
                    settings.bot = env.wake_words[result]
                    self.executor()


def begin() -> None:
    """Starts main process to activate Jarvis and process requests via API calls."""
    try:
        Activator().start()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    begin()
