import pathlib
import time
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy  # noqa

from jarvis_ui.modules.logger import logger


def initiator(status_manager: DictProxy = None) -> None:
    """Starts main process to activate Jarvis and process requests via API calls."""
    from jarvis_ui.executables.helper import heart_beat
    from jarvis_ui.executables.starter import Activator
    from jarvis_ui.modules.models import env
    from jarvis_ui.modules.timer import RepeatedTimer
    if env.heart_beat:
        logger.info("Initiating heart beat with an interval of %d seconds", env.heart_beat)
        timer = RepeatedTimer(function=heart_beat, interval=env.heart_beat, args=(status_manager,))
        timer.start()
    else:
        timer = None
    activator = Activator()
    try:
        if status_manager:
            status_manager["LOCKED"] = False
        activator.start(status_manager=status_manager)
    except KeyboardInterrupt:
        if timer:
            timer.stop()
    finally:
        activator.at_exit()


def terminator(process: Process) -> None:
    """Terminates the process.

    Args:
        process: Takes the process object as an argument.
    """
    logger.info("Terminating %s [%d]", process.name, process.pid)
    process.terminate()
    if process.is_alive():
        logger.warning("Process %s [%d] is still alive. Killing it.", process.name, process.pid)
        process.kill()
        process.join(timeout=1e-01)
        try:
            logger.info("Closing process: %s [%d]", process.name, process.pid)
            process.close()  # Close immediately instead of waiting to be garbage collected
        except ValueError as error:
            # Expected when join timeout is insufficient. The resources will be released eventually but not immediately.
            logger.error(error)


def start() -> None:
    """Initiates Jarvis as a child process."""
    # Import within a function to be called repeatedly
    from jarvis_ui.modules.models import env, settings  # noqa: F401
    if settings.operating_system == "Linux":
        initiator()
        return
    status_manager = Manager().dict()
    status_manager["LOCKED"] = False  # Instantiate DictProxy
    process = Process(target=initiator, args=(status_manager,))
    process.name = pathlib.Path(__file__).stem
    process.start()
    logger.info("Initiating as %s [%d]", process.name, process.pid)
    while True:
        if not process.is_alive():  # Terminated
            logger.info("Process %s [%d] died. Ending loop.", process.name, process.pid)
            return
        if status_manager["LOCKED"] is None:  # Neither locked nor unlocked, so restart
            logger.info("Lock status was set to None")
            terminator(process=process)
            break
        time.sleep(1)
    start()
