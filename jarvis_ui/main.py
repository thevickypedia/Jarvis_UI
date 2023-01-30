import pathlib
import time
import warnings
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy  # noqa

from jarvis_ui.executables.helper import time_converter, word_engine
from jarvis_ui.modules.exceptions import APIError
from jarvis_ui.modules.logger import logger


def initiator(status_manager: DictProxy) -> None:
    """Starts main process to activate Jarvis and process requests via API calls."""
    try:
        # Import within a function to catch startup errors
        from jarvis_ui.executables.starter import Activator
    except APIError as error:
        logger.error(error)
        status_manager["LOCKED"] = "RESTART"
    else:
        try:
            status_manager["LOCKED"] = False
            Activator().start(status_manager=status_manager)
        except KeyboardInterrupt:
            return


def terminator(process: Process):
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


def start():
    """Initiates Jarvis as a child process and restarts as per the timer set.

    See Also:
        - Swaps the public URL every time it restarts.
        - Reloads env variables upon restart.
        - Avoids memory overload.
    """
    # Import within a function to be called repeatedly
    from jarvis_ui.modules.models import env
    logger.info(f"Restart set to {time_converter(second=env.restart_timer)}")
    status_manager = Manager().dict()
    status_manager["LOCKED"] = False  # Instantiate DictProxy
    process = Process(target=initiator, args=(status_manager,))
    process.name = pathlib.Path(__file__).stem
    process.start()
    logger.info(f"Initiating as {process.name}[{process.pid}]")
    start_time = time.time()
    while True:
        if start_time + env.restart_timer <= time.time():
            if status_manager["LOCKED"] is True:
                continue  # Wait for the existing task to complete
            logger.info(f"Time to restart {process.name}[{process.pid}]")
            terminator(process=process)
            break
        if not process.is_alive():
            if start.count > env.restart_attempts:
                warnings.warn(
                    "Retry limit exceeded after consecutive start up errors."
                )
                logger.critical("Retry limit exceeded.")
                return
            if status_manager["LOCKED"] == "RESTART":  # Called only when restart fails during initial connect
                start.count += 1
                logger.warning(f"{word_engine.ordinal(start.count)} restart because of a problem.")
                break
            logger.info(f"Process {process.name}[{process.pid}] died. Ending loop.")
            return
        if status_manager["LOCKED"] is None:
            logger.info("Lock status was set to None")
            terminator(process=process)
            break
        time.sleep(0.5)
    start()
