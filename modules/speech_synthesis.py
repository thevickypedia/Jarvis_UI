"""Checks if speech synthesis is running a docker container already. If not tries to trigger it.

>>> SpeechSynthesizer

"""

import os
import pathlib
import socket
import subprocess
from typing import NoReturn

import requests

from modules.logger import logger
from modules.models import env


def is_port_in_use(port: int) -> bool:
    """Connect to a remote socket at address, to identify if the port is currently being used.

    Args:
        port: Takes the port number as an argument.

    Returns:
        bool:
        A boolean flag to indicate whether a port is open.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0


def check_existing() -> bool:
    """Checks for existing connection.

    Returns:
        bool:
        A boolean flag whether a valid connection is present.
    """
    if is_port_in_use(port=env.speech_synthesis_port):
        try:
            res = requests.get(url=f"http://localhost:{env.speech_synthesis_port}", timeout=1)
            if res.ok:
                logger.info(f"Speech synthesizer is running on {env.speech_synthesis_port}")
                return True
            logger.warning(f"{res.url}::{res.status_code}::{res.reason}")
            return False
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            logger.error(error)
            return False


class SpeechSynthesizer:
    """Initiates the docker container to process text-to-speech requests.

    >>> SpeechSynthesizer

    """

    def __init__(self):
        """Creates log file and initiates port number and docker command to run."""
        self.docker = f"""docker run \n
            -p {env.speech_synthesis_port}:{env.speech_synthesis_port} \n
            -e "HOME={env.home}" \n
            -v "$HOME:{env.home}" \n
            -v /usr/share/ca-certificates:/usr/share/ca-certificates \n
            -v /etc/ssl/certs:/etc/ssl/certs \n
            -w "{os.getcwd()}" \n
            --user "$(id -u):$(id -g)" \n
            rhasspy/larynx"""
        if env.speech_synthesis_port != 5002:
            self.docker += f" --port {env.speech_synthesis_port}"

    def synthesizer(self) -> NoReturn:
        """Initiates speech synthesizer using docker."""
        if check_existing():
            return
        if not os.path.isfile(os.path.join("logs", "speech_synthesis.log")):
            pathlib.Path(os.path.join("logs", "speech_synthesis.log")).touch()
        with open(os.path.join("logs", "speech_synthesis.log"), "a") as output:
            try:
                subprocess.call(self.docker, shell=True, stdout=output, stderr=output)
            except (subprocess.CalledProcessError, subprocess.SubprocessError, Exception):
                env.speech_synthesis_timeout = 0
                return


if __name__ == '__main__':
    SpeechSynthesizer().synthesizer()
