import os
import pathlib
import string
import struct
import sys
import time
from datetime import datetime
from multiprocessing import Manager, Process
from typing import Dict, NoReturn, Union

import pvporcupine
from pyaudio import PyAudio, Stream, paInt16

from modules import listener, speaker
from modules.api_handler import make_request
from modules.config import config, time_converter
from modules.logger import logger
from modules.models import env, fileio, flag, settings
from modules.playsound import playsound


def processor() -> Union[str, None]:
    """Processes the request after wake word is detected.

    Returns:
        bool:
        Returns a ``True`` flag if a manual stop is requested.
    """
    if phrase := listener.listen():
        logger.info(f"Request: {phrase}")
        sys.stdout.write(f"\rRequest: {phrase}")
        if "restart" in phrase.lower():
            logger.info("User requested to restart.")
            playsound(sound=fileio.restart)
            return flag.restart
        if "stop running" in phrase.lower():
            logger.info("User requested to stop.")
            playsound(sound=fileio.shutdown)
            return flag.stop
        if not any(word in phrase.lower() for word in config.keywords + config.conversation):
            logger.warning(f"'{phrase}' is not a part of recognized keywords or conversation.")
            return
        if not any(word in phrase.lower() for word in config.api_compatible['compatible']):
            logger.warning(f"'{phrase}' is not a part of API compatible request.")
            playsound(sound=fileio.unprocessable)
            return
        if any(word in phrase.lower() for word in config.delay_with_ack + config.delay_without_ack):
            logger.info(f"Increasing timeout for: {phrase}")
            timeout = 30
            if any(word in phrase.lower() for word in config.delay_with_ack):
                playsound(sound=fileio.processing, block=False)
        else:
            timeout = env.request_timeout
        if response := make_request(path='offline-communicator', timeout=timeout,
                                    data={'command': phrase, 'native_audio': env.native_audio,
                                          'speech_timeout': env.speech_timeout}):
            if response is True:
                logger.info("Response received as audio.")
                sys.stdout.write("\rResponse received as audio.")
                playsound(sound=fileio.speech_wav_file)
                os.remove(fileio.speech_wav_file)
                return
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
            input_device_index=env.microphone_index
        )

    def executor(self, status):
        """Closes the audio stream and calls the processor."""
        logger.debug(f"Detected {settings.bot} at {datetime.now()}")
        status["LOCKED"] = True
        logger.debug("Restart locked")
        playsound(sound=fileio.acknowledgement, block=False)
        self.py_audio.close(stream=self.audio_stream)
        processed = processor()
        if processed == flag.stop:
            self.audio_stream = None
            raise KeyboardInterrupt
        if processed == flag.restart:
            status["LOCKED"] = None
        else:
            status["LOCKED"] = False
        logger.debug("Restart released")
        self.audio_stream = self.open_stream()

    def start(self, status: Dict) -> NoReturn:
        """Runs ``audio_stream`` in a forever loop and calls ``initiator`` when the phrase ``Jarvis`` is heard."""
        logger.info(f"Starting wake word detector with sensitivity: {env.sensitivity}")
        while True:
            sys.stdout.write(f"\r{self.label}")
            pcm = struct.unpack_from("h" * self.detector.frame_length,
                                     self.audio_stream.read(num_frames=self.detector.frame_length,
                                                            exception_on_overflow=False))
            result = self.detector.process(pcm=pcm)
            if settings.legacy:
                if len(env.wake_words) == 1 and result:
                    settings.bot = env.wake_words[0]
                    self.executor(status=status)
                elif len(env.wake_words) > 1 and result >= 0:
                    settings.bot = env.wake_words[result]
                    self.executor(status=status)
            else:
                if result >= 0:
                    settings.bot = env.wake_words[result]
                    self.executor(status=status)


def starter(status: Dict) -> None:
    """Starts main process to activate Jarvis and process requests via API calls."""
    try:
        Activator().start(status=status)
    except KeyboardInterrupt:
        return


def terminate(process: Process):
    """Terminates the process.

    Args:
        process: Takes the process object as an argument.
    """
    logger.info(f"Terminating {process.name}[{process.pid}]")
    process.terminate()
    if process.is_alive():
        logger.warning(f"Process {process.name}[{process.pid}] is still alive. Killing it.")
        process.kill()
        process.join(timeout=1e-01)
        try:
            logger.info(f"Closing process: {process.name}[{process.pid}]")
            process.close()  # Close immediately instead of waiting to be garbage collected
        except ValueError as error:
            # Expected when join timeout is insufficient. The resources will be released eventually but not immediately.
            logger.error(error)


def begin():
    """Initiates Jarvis as a child process and restarts as per the timer set.

    See Also:
        - Swaps the public URL every time it restarts.
        - Reloads env variables upon restart.
        - Avoids memory overload.
    """
    sys.stdout.write(f"\rRestart set to {time_converter(second=env.restart_timer)}")
    logger.info(f"Restart set to {time_converter(second=env.restart_timer)}")
    status_dict = Manager().dict()
    status_dict["LOCKED"] = False
    process = Process(target=starter, args=(status_dict,))
    process.name = pathlib.Path(__file__).stem
    process.start()
    logger.info(f"Initiating as {process.name}[{process.pid}]")
    start_time = time.time()
    while True:
        if start_time + env.restart_timer <= time.time():
            if status_dict["LOCKED"]:
                continue  # Wait for the existing task to complete
            logger.info(f"Time to restart {process.name}[{process.pid}]")
            terminate(process=process)
            break
        if not process.is_alive():
            logger.info(f"Process {process.name}[{process.pid}] died. Ending loop.")
            return
        if status_dict["LOCKED"] is None:
            logger.info("Lock status was set to None")
            terminate(process=process)
            break
        time.sleep(0.5)
    begin()


if __name__ == '__main__':
    begin()
