.. Jarvis UI documentation master file, created by
   sphinx-quickstart on Wed Jun 15 11:46:55 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Jarvis UI's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Read Me:

   README

Jarvis
====================

.. automodule:: jarvis
   :members:
   :undoc-members:

API Handler
===========

.. automodule:: modules.api_handler
   :members:
   :undoc-members:

Config
======

.. autoclass:: modules.config.Config(BaseConfig)
   :members:
   :exclude-members:

Listener
========

.. automodule:: modules.listener
   :members:
   :undoc-members:

Logger
======

.. automodule:: modules.logger
   :members:
   :undoc-members:

Models
======

.. autoclass:: modules.models.EnvConfig(BaseSettings)
   :members:
   :undoc-members:

.. autoclass:: modules.models.FileIO(BaseSettings)
   :members:
   :undoc-members:

.. autoclass:: modules.models.Settings(BaseSettings)
   :members:
   :undoc-members:

.. autoclass:: modules.models.Sensitivity(float or PositiveInt, Enum)
   :members:
   :undoc-members:

.. autoclass:: modules.models.RestartTimer(float or PositiveInt, Enum)
   :members:
   :undoc-members:

.. autoclass:: modules.models.Flag(str, Enum)
   :members:
   :undoc-members:

PlaySound
=========

.. automodule:: modules.playsound
   :members:
   :undoc-members:

Speaker
=======

.. automodule:: modules.speaker
   :members:
   :undoc-members:

Peripherals
===========

.. automodule:: modules.peripherals
   :members:
   :undoc-members:

Exceptions
==========

.. automodule:: modules.exceptions
   :members:
   :undoc-members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
