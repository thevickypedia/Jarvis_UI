Release Notes
=============

0.6.0 (05/09/2023)
------------------
- Fix ``PermissionError`` on Windows for playsound
- Convert ``FileIO`` object's attributes to strings
- Windows doesn't ``PathLike`` attributes

0.5.9 (05/09/2023)
------------------
- Improve audio quality on predefined responses
- Install playsound to deal with audio

0.5.8 (05/06/2023)
------------------
- Update doc strings and remove dead code

0.5.7 (05/06/2023)
------------------
- Set UI to trigger even when failed to reach server
- Add connection restart wav files for indicators
- Remove timeout and timeout extensions
- Reduce latency in response
- Cleanup unwanted objects

0.5.6 (04/19/2023)
------------------
- Resolve edge case scenario with `ObjectiveC`
- Check pyttsx3 instantiation in a thread
- Use custom module instead of pyttsx3
- Install coreutils on macOS using brew

0.5.5 (04/10/2023)
------------------
- Update initialization and installation script
- Unhook version dependencies with changelog-generator

0.5.4 (03/22/2023)
------------------
- Fix interactive mode on Windows OS
- Update requirements.txt

0.5.3 (03/22/2023)
------------------
- Fix static IDE identifier on child processes
- Bump max allowed retry limit to 1000

0.5.2 (03/21/2023)
------------------
- Flush screen to support terminals
- Update release_notes.rst and README.md

0.5.1 (01/30/2023)
------------------
- Update README.md

0.5.0 (01/30/2023)
------------------
- Make `Jarvis_UI` pip installable
- Onboard to pypi with pyproject.toml
- Fix path for indicators
- Switch python-publish.yml to support pyproject.toml

0.4.9 (01/11/2023)
------------------
- Set the application to restart in case of startup errors
- Avoid application falling on its face during a restart
- Restructure modules and executables

0.4.8 (01/07/2023)
------------------
- Move validations from `speaker.py` to `config.py`
- Fix docstrings

0.4.7 (01/07/2023)
------------------
- Create `Enum` flags to communicate
- Add an option to restart upon user request
- Add restart.wav and restart_ss.wav

0.4.6 (01/07/2023)
------------------
- Use `multiprocessing.Manager` to block restart in between a task
- Add support to Linux OS
- Block of ALSA errors on Linux
- Add an option to set voice name and voice rate for built-in speaker
- Add custom exception handlers
- Update .gitignore and README.md

0.4.5 (01/07/2023)
------------------
- Setup automatic restart based on env var
- Update README.md

0.4.4 (01/02/2023)
------------------
- Change HTTP requests method to match a change in Jarvis' API

0.4.3 (12/30/2022)
------------------
- Upgrade `PyAudio` and `pydantic` modules
- Add a helper function in playsound.py
- CHANGELOG -> release_notes.rst
- Update setup.py

0.4.2 (12/06/2022)
------------------
- Set pypi build upon release instead of commit
- Simplify pypi build action

0.4.1 (10/29/2022)
------------------
- Remove preflight check and timed restart
- Have an env var to determine URL swapping
- Add connection failed wav file
- Update README.md

0.4.0 (10/22/2022)
------------------
- Set voice phrase limit to 7 seconds when recognizer settings are used
- This will avoid any potential background sounds for a very long time

0.3.9 (10/22/2022)
------------------
- Add custom recognizer settings
- Add a static file to indicate a connection failure
- Update README.md

0.3.8 (09/27/2022)
------------------
- Switch `Authorization` from headers to custom `BearerAuth`
- Increase timeout for MyQ controls

0.3.7 (09/21/2022)
------------------
- Enable `speech-synthesis` via `offline-communicator`
- Add missing call option for swapper function

0.3.6 (09/14/2022)
------------------
- Swap request URL with public endpoint from Jarvis
- Write wake words on screen
- Update type hinting and docstrings

0.3.5 (09/03/2022)
------------------
- Improve wait time after wake word detection
- Initialize microphone object before startup
- Update README.md

0.3.4 (08/31/2022)
------------------
- Add individual sensitivity values for wake words
- Fig bug on manual interruption
- Bump sphinx version

0.3.3 (08/30/2022)
------------------
- Update install.sh, README.md and requirements.txt

0.3.2 (08/29/2022)
------------------
- Support wake words detection for legacy macOS
- Add more start up checks for wake words
- Log wake word used

0.3.1 (07/09/2022)
------------------
- Convert stop method to destructor
- Break loop instead of raising exception
- Fix pydantic validation

0.3.0 (07/08/2022)
------------------
- Add preconfigured wav files to process tts in background
- Reconfigure config.py to accommodate fileio changes
- Add warnings for untested OS in models.py
- Ignore lambda instead of def in pre-commit config

0.2.9 (07/06/2022)
------------------
- Let pydantic validate env vars
- Remove unused recorded frames

0.2.8 (06/28/2022)
------------------
- Hexlify token to secure it over internet
- Assert secured token during startup
- Remove parsing URL during startup

0.2.7 (06/21/2022)
------------------
- Have an option to process audio at source machine

0.2.6 (06/20/2022)
------------------
- Do not delete wav file if run from windows in a thread
- Raise connection error using parsed URL

0.2.5 (06/20/2022)
------------------
- Avoid mandating speech synthesis on MacOS
- Add detailed notes in install.sh
- Close audio streams when requested to stop

0.2.4 (06/20/2022)
------------------
- Download `PyAudio` wheel file based on python version
- Mandatory speech synthesis for Windows
- Update README.md

0.2.3 (06/19/2022)
------------------
- Disable API calls to speech synthesis by default
- Parse request url

0.2.2 (06/15/2022)
------------------
- Add `CSS` for docstrings
- Bump version

0.2.1 (06/15/2022)
------------------
- Use `Session` to reuse headers
- Set a fixed connect timeout for 3 seconds to the API
- Update docs

0.2.0 (06/15/2022)
------------------
- Update CHANGELOG

0.1.9 (06/15/2022)
------------------
- Bump version to trigger deployment

0.1.8 (06/15/2022)
------------------
- Bump version to trigger deployment

0.1.7 (06/15/2022)
------------------
- Change path when doc generation is run
- Update README.md
- Add LICENSE and update setup.py

0.1.6 (06/15/2022)
------------------
- Add template for feature request

0.1.5 (06/15/2022)
------------------
- Add template for bug report

0.1.4 (06/15/2022)
------------------
- Store exceptions in a dictionary
- Remove env var for docs_generation

0.1.3 (06/15/2022)
------------------
- Fix classifier in setup.py

0.1.2 (06/15/2022)
------------------
- Fix branch name in python-publish.yml
- Update setup.py, README.md, version.py
- Have an env var DOCS_GENERATION to filter default actions

0.1.1 (06/15/2022)
------------------
- Make Jarvis_UI as a pypi package
- Add CHANGELOG
- Update shpinx docs
- Update docstrings and type hints

0.1.0 (06/14/2022)
------------------
- Filter non-compatible words before making API calls
- Store all requirements in a config class during startup
- Remove unnecessary args in speaker.py

0.0.9 (06/13/2022)
------------------
- Send payload as json instead of query string
- Have optional acknowledgement played for delay keywords

0.0.8 (06/12/2022)
------------------
- Remove unused fileio resources
- Change base log file type hint from FilePath to str

0.0.7 (06/12/2022)
------------------
- Onboard custom `PlayAudio` module
- Close `audio_stream` before opening `Microphone`
- Fix install.sh
- Convert mp3 to wav files

0.0.6 (06/11/2022)
------------------
- Increase delay timeout to 30 seconds
- Log it and have an acknowledgement
- Have a new variable for speech timeout

0.0.5 (06/11/2022)
------------------
- Use speech synthesis running on server
- Avoid spinning up a docker in client
- Validate mandatory args during startup
- Update README.md

0.0.4 (06/11/2022)
------------------
- Get keywords before proceeding
- Load log file paths into a models.py
- Add .pre-commit-config.yaml

0.0.3 (06/10/2022)
------------------
- Move api_handler.py to its own module for future iterations

0.0.2 (06/10/2022)
------------------
- Jarvis to run via api calls

0.0.1 (06/09/2022)
------------------
- Replicate necessary parts from Jarvis repo
