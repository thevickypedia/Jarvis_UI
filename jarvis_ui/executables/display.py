# noinspection PyUnresolvedReferences
"""OnScreen display functions for the UI.

>>> Display

"""

import os
import sys
from typing import Any

from jarvis_ui.modules import models


def write_screen(text: Any) -> None:
    """Write text to a screen that can be cleared later.

    Args:
        text: Text to be written on screen..
    """
    flush_screen()
    sys.stdout.write(f"\r{text}")


def flush_screen() -> None:
    """Flushes the screen output.

    See Also:
        - Writes white spaces to the window size in a terminal.
        - Writes recursive empty text in IDE to flush screen.
    """
    if models.settings.interactive:
        sys.stdout.write(f"\r{' '.join(['' for _ in range(os.get_terminal_size().columns)])}")
    else:
        sys.stdout.write("\r")
