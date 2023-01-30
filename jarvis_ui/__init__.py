import os

from pynotification import pynotifier

version = "0.5.1"

try:
    import pvporcupine  # noqa
    import pyaudio  # noqa
except ImportError as error:
    pynotifier(title="First time user?", dialog=True,
               message=f"Please run\n\n{os.path.join(os.path.dirname(__file__), 'lib', 'install.sh')}")
    raise UserWarning(f"{error.__str__()}\n\nPlease run\n\n"
                      f"{os.path.join(os.path.dirname(__file__), 'lib', 'install.sh')}")
else:
    from .main import start
    start.count = 0
