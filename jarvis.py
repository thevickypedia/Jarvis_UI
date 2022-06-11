import pathlib
import platform
import struct
import sys
from multiprocessing import Process
from typing import NoReturn, Union

import packaging.version
import pvporcupine
import requests
from playsound import playsound
from pyaudio import PyAudio, paInt16
from speech_recognition import Microphone, Recognizer, UnknownValueError

from modules import speaker
from modules.api_handler import make_request
from modules.logger import logger
from modules.models import env, fileio
from modules.speech_synthesis import SpeechSynthesizer

recognizer = Recognizer()  # initiates recognizer that uses google's translation
if not (keywords := make_request(path='keywords', timeout=env.request_timeout)):
    raise ConnectionError(
        "Unable to connect to the API."
    )
if detail := keywords.get("detail"):
    exit(detail)


def listen(timeout: Union[int, float], phrase_limit: Union[int, float]) -> Union[str, None]:
    """Function to activate listener, this function will be called by most upcoming functions to listen to user input.

    Args:
        timeout: Time in seconds for the overall listener to be active.
        phrase_limit: Time in seconds for the listener to actively listen to a sound.

    Returns:
        str:
         - Returns recognized statement from the microphone.
    """
    (sys.stdout.flush(), sys.stdout.write("\rListener activated.."))
    listened = recognizer.listen(source=source, timeout=timeout, phrase_time_limit=phrase_limit)
    (sys.stdout.flush(), sys.stdout.write("\r"))
    try:
        return recognizer.recognize_google(audio_data=listened)
    except UnknownValueError:
        return
    except requests.exceptions.RequestException as error:
        logger.error(error)


def process_request() -> bool:
    """Processes the request after wake word is detected.

    Returns:
        bool:
        Returns a ``True`` flag if a manual stop is requested.
    """
    playsound(sound=fileio.acknowledgement, block=False)
    if phrase := listen(timeout=env.voice_timeout, phrase_limit=env.voice_phrase_limit):
        logger.info(f"Request: {phrase}")
        sys.stdout.write(f"\rRequest: {phrase}")
        if "stop running" in phrase.lower():
            logger.info("User requested to stop.")
            speaker.speak(text="Shutting down now!.", run=True)
            return True
        if any(word in phrase.lower() for word in keywords.get('car')):
            timeout = 15
        else:
            timeout = env.request_timeout
        if response := make_request(task=phrase, timeout=timeout, path='offline-communicator'):
            response = response.get('detail', '').split('\n')[-1]
            response = response.replace("\N{DEGREE SIGN}F", " degrees fahrenheit")
            logger.info(f"Response: {response}")
            sys.stdout.write(f"\rResponse: {response}")
            speaker.speak(text=response, run=True)
        else:
            speaker.speak(text="I wasn't able to process your request.", run=True)


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
        self.audio_stream = self.py_audio.open(
            rate=self.detector.sample_rate,
            channels=1,
            format=paInt16,
            input=True,
            frames_per_buffer=self.detector.frame_length,
            input_device_index=self.input_device_index
        )

    def start(self) -> NoReturn:
        """Runs ``audio_stream`` in a forever loop and calls ``initiator`` when the phrase ``Jarvis`` is heard."""
        logger.info(f"Starting wake word detector with sensitivity: {env.sensitivity}")
        while True:
            sys.stdout.write("\rSentry Mode")
            pcm = struct.unpack_from("h" * self.detector.frame_length,
                                     self.audio_stream.read(num_frames=self.detector.frame_length,
                                                            exception_on_overflow=False))
            self.recorded_frames.append(pcm)
            if self.detector.process(pcm=pcm) >= 0:
                if process_request():
                    return

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
        if wake_word := listen(timeout=10, phrase_limit=2.5):
            if any(word in wake_word.lower() for word in env.legacy_keywords):
                if process_request():
                    return


def begin():
    """Starts main process to activate Jarvis and process requests via API calls."""
    try:
        if env.macos and packaging.version.parse(platform.mac_ver()[0]) < packaging.version.parse('10.14'):
            sentry_mode()
        else:
            Activator().start()
    except KeyboardInterrupt as error:
        logger.warning(error)
    speech_process.join(timeout=3)
    if speech_process.is_alive():
        speech_process.kill()
        speech_process.join(timeout=1)


if __name__ == '__main__':
    speech_process = Process(target=SpeechSynthesizer().synthesizer)
    speech_process.start()
    with Microphone() as source:
        begin()
