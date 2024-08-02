import os
from multiprocessing import Process
from multiprocessing.managers import DictProxy  # noqa
from threading import Timer
from typing import Union

import pyvolume
from playsound import playsound

from jarvis_ui.executables import api_handler, display, helper, listener, speaker
from jarvis_ui.logger import logger
from jarvis_ui.modules.config import config
from jarvis_ui.modules.models import env, fileio, settings


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
    phrase_lower = phrase.lower()
    if "restart" in phrase_lower:
        logger.info("User requested to restart.")
        playsound(sound=fileio.restart)
        display.write_screen("Restarting...")
        return "RESTART"
    if "stop running" in phrase_lower:
        logger.info("User requested to stop.")
        playsound(sound=fileio.shutdown)
        display.write_screen("Shutting down")
        return "STOP"
    if (
        "volume" in phrase_lower or "mute" in phrase_lower
    ) and "server" not in phrase_lower:
        if "unmute" in phrase_lower:
            level = env.volume
        elif "mute" in phrase_lower:
            level = 0
        elif "max" in phrase_lower or "full" in phrase_lower:
            level = 100
        else:
            level = helper.extract_nos(input_=phrase, method=int)
        pyvolume.custom(level, logger)
    if not config.keywords:
        logger.warning("keywords are not loaded yet, restarting")
        if os.path.isfile("failed_command"):
            logger.critical("Consecutive failure")
            os.remove("failed_command")
        else:
            with open("failed_command", "w") as file:
                file.write(phrase)
                file.flush()
            playsound(sound=fileio.connection_restart)
        display.write_screen("Trying to re-establish connection with Server...")
        return "RESTART"
    if os.path.isfile("failed_command"):
        logger.info("Recovered after a recent failure, deleting placeholder file.")
        os.remove("failed_command")
    if response := api_handler.make_request(
        path="offline-communicator",
        data={
            "command": phrase,
            "native_audio": env.native_audio,
            "speech_timeout": env.speech_timeout,
        },
    ):
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
            player = Process(target=playsound, kwargs={"sound": fileio.speech_wav_file})
            player.start()
            player.join()
            if player.is_alive():
                player.terminate()
                player.kill()
            Timer(
                interval=3, function=os.remove, args=(fileio.speech_wav_file,)
            ).start()
        else:
            playsound(sound=fileio.speech_wav_file)
            os.remove(fileio.speech_wav_file)
        return
    response = response.get("detail", "")
    logger.info("Response: %s", response)
    display.write_screen(f"Response: {response}")
    speaker.speak(text=response)


def process(phrase: str = None, status_manager: DictProxy = None) -> None:
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
                helper.linux_restart()
            status_manager["LOCKED"] = None
            while True:
                pass  # To ensure the listener doesn't end so that, the main process can kill and restart
