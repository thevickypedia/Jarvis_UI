# noinspection PyUnresolvedReferences
"""OnScreen display functions for the UI.

>>> Display

"""

import os
import sys
from typing import Any, NoReturn

from jarvis_ui.modules import models


def write_screen(text: Any) -> NoReturn:
    """Write text to a screen that can be cleared later.

    Args:
        text: Text to be written.
    """
    flush_screen()
    sys.stdout.write(f"\r{text}")


def flush_screen() -> NoReturn:
    """Flushes the screen output."""
    if models.settings.interactive:
        sys.stdout.write(f"\r{' '.join(['' for _ in range(os.get_terminal_size().columns)])}")
    else:
        sys.stdout.write("\r")
