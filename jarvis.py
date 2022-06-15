import pathlib
import platform
import struct
import sys
from typing import NoReturn

import packaging.version
import pvporcupine
from pyaudio import PyAudio, paInt16

from modules import listener, speaker
from modules.api_handler import make_request
from modules.config import config
from modules.logger import logger
from modules.models import env, fileio
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
            speaker.speak(text="Shutting down now!")
            return True
        if not any(word in phrase.lower() for word in config.keywords + config.conversation):
            logger.warning(f"'{phrase}' is not a part of recognized keywords or conversation.")
            return False
        if not any(word in phrase.lower() for word in config.api_compatible['compatible']):
            logger.warning(f"'{phrase}' is not a part of API compatible request.")
            speaker.speak(text="I am unable to process this request via API calls!")
            return False
        if any(word in phrase.lower() for word in config.delay_keywords):
            logger.info(f"Increasing timeout for: {phrase}")
            timeout = 30
            if any(word in phrase.lower() for word in config.delay_with_ack):
                speaker.speak(text="Processing now.", block=False)
        else:
            timeout = env.request_timeout
        if response := make_request(path='offline-communicator', data={'command': phrase}, timeout=timeout):
            response = response.get('detail', '').replace("\N{DEGREE SIGN}F", " degrees fahrenheit").replace("\n", ". ")
            logger.info(f"Response: {response}")
            sys.stdout.write(f"\rResponse: {response}")
            speaker.speak(text=response)
        else:
            speaker.speak(text="I wasn't able to process your request.")


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
        keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in [pathlib.PurePath(__file__).stem]]
        self.input_device_index = input_device_index
        self.recorded_frames = []

        self.py_audio = PyAudio()
        self.detector = pvporcupine.create(
            library_path=pvporcupine.LIBRARY_PATH,
            model_path=pvporcupine.MODEL_PATH,
            keyword_paths=keyword_paths,
            sensitivities=[env.sensitivity]
        )
        self.audio_stream = None

    def open_stream(self):
        """Initializes an audio stream."""
        self.audio_stream = self.py_audio.open(
            rate=self.detector.sample_rate,
            channels=1,
            format=paInt16,
            input=True,
            frames_per_buffer=self.detector.frame_length,
            input_device_index=self.input_device_index
        )

    def close_stream(self):
        """Closes audio stream so that other listeners can use microphone."""
        self.py_audio.close(stream=self.audio_stream)
        self.audio_stream = None

    def start(self) -> NoReturn:
        """Runs ``audio_stream`` in a forever loop and calls ``initiator`` when the phrase ``Jarvis`` is heard."""
        logger.info(f"Starting wake word detector with sensitivity: {env.sensitivity}")
        while True:
            if not self.audio_stream:
                self.open_stream()
            sys.stdout.write("\rSentry Mode")
            pcm = struct.unpack_from("h" * self.detector.frame_length,
                                     self.audio_stream.read(num_frames=self.detector.frame_length,
                                                            exception_on_overflow=False))
            self.recorded_frames.append(pcm)
            if self.detector.process(pcm=pcm) >= 0:
                playsound(sound=fileio.acknowledgement, block=False)
                self.close_stream()
                if processor():
                    raise KeyboardInterrupt

    def stop(self) -> NoReturn:
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


def sentry_mode() -> NoReturn:
    """Listens forever and invokes ``initiator()`` when recognized. Stops when ``restart`` table has an entry.

    See Also:
        - Gets invoked only when run from Mac-OS older than 10.14.
        - A regular listener is used to convert audio to text.
        - The text is then condition matched for wake-up words.
        - Additional wake words can be passed in a list as an env var ``LEGACY_KEYWORDS``.
    """
    while True:
        sys.stdout.write("\rSentry Mode")
        if wake_word := listener.listen(timeout=10, phrase_limit=2.5, stdout=False):
            if any(word in wake_word.lower() for word in env.legacy_wake_words):
                playsound(sound=fileio.acknowledgement, block=False)
                if processor():
                    raise KeyboardInterrupt


def begin():
    """Starts main process to activate Jarvis and process requests via API calls."""
    try:
        if env.macos and packaging.version.parse(platform.mac_ver()[0]) < packaging.version.parse('10.14'):
            sentry_mode()
        else:
            Activator().start()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    begin()
