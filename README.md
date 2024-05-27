![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)

**Deployments**

[![pages-build-deployment](https://github.com/thevickypedia/Jarvis_UI/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/thevickypedia/Jarvis_UI/actions/workflows/pages/pages-build-deployment)

[![pypi](https://github.com/thevickypedia/Jarvis_UI/actions/workflows/python-publish.yml/badge.svg)](https://github.com/thevickypedia/Jarvis_UI/actions/workflows/python-publish.yml)

# Jarvis UI

Connects to [`Jarvis`](https://github.com/thevickypedia/Jarvis/blob/master/jarvis/api/fast.py) running in the backend to process request and response via API calls.

### Kick off
**Install**
```shell
python -m pip install jarvis-ui
```

**Initiate**
```python
import jarvis_ui


if __name__ == '__main__':
    jarvis_ui.start()
```

### Environment Variables
Env vars are loaded from a `.env` file and validated using `pydantic`
<details>
<summary><strong><i>To use custom .env files</i></strong></summary>

To use a custom `.env` file, set the filename to the env var `env_file` before importing `jarvis_ui` module.

```python
import os
os.environ['env_file'] = "jarvis_ui.env"

import jarvis_ui

if __name__ == '__main__':
    jarvis_ui.start()
```

</details>

#### Mandatory
- **SERVER_URL**: Endpoint URL to which the API call has to be made. Can be `localhost` or a `tunneled` URL behind a reverse proxy/CDN.
- **TOKEN**: Authentication token.

#### Optional
- **HEART_BEAT**: Defaults to `None` - _Interval in seconds to trigger background healthcheck on the server with automatic restart_
- **DEBUG**: Defaults to `False` - _Enable debug level logging_
<br><br>
- **SPEECH_TIMEOUT**: Defaults to `0` for macOS, `10` for Windows - _Timeout for speech synthesis_
<br><br>
- **NATIVE_AUDIO**: Defaults to `False` - _If set to `True`, the response is generated in the server's default voice_
- **WAKE_WORDS**: Defaults to `jarvis` (Defaults to `alexa` in macOS older than `10.14`) - _Wake words to initiate Jarvis_
- **SENSITIVITY**: Defaults to `0.5` - _Sensitivity of wake word detection_
<br><br>
- **MICROPHONE_INDEX**: Defaults to `None` - _Use [peripherals.py](https://github.com/thevickypedia/Jarvis_UI/blob/main/modules/peripherals.py) to get the index values_
- **VOICE_NAME**: Defaults to the author's favorite per the OS. _Name of the voice supported by the OperatingSystem_
- **VOICE_RATE**: Defaults to the value in `py3-tts` module - _Speed/rate at which the text should be spoken_
- **VOICE_PITCH**: Defaults to the value in `py3-tts` module - _Currently available only for Linux OS_
<br><br>
- **LISTENER_TIMEOUT**: Defaults to `2` - _Timeout for listener once wake word is detected - Awaits for a speech to begin until this limit_
- **LISTENER_PHRASE_LIMIT**: Defaults to `5` - _Timeout for phrase once listener is activated - Listener will be deactivated after this limit_
- **RECOGNIZER_SETTINGS**: JSON object of customized speech recognition settings.

<details>
<summary><strong>Custom settings for speech recognition</strong></summary>

The default values for **RECOGNIZER_SETTINGS** are customized according to the author's voice pitch.
Please use [test_listener.py](https://github.com/thevickypedia/Jarvis_UI/blob/main/test_listener.py) to figure out the suitable values in a trial and error method.

Sample settings (formatted as JSON object)<br>

**RECOGNIZER_SETTINGS**: `'{"energy_threshold": 1100, "dynamic_energy_threshold": false, "pause_threshold": 1, "phrase_threshold": 0.1}'`

**Description**
- **energy_threshold**: Minimum audio energy to consider for recording. Greater the value, louder the voice should be.
- **dynamic_energy_threshold**: Change considerable audio **energy_threshold** dynamically.
- **pause_threshold**: Seconds of non-speaking audio before a phrase is considered complete.
- **phrase_threshold**: Minimum seconds of speaking audio before it can be considered a phrase - values below this are ignored. This helps to filter out clicks and pops.
- **non_speaking_duration**: Seconds of non-speaking audio to keep on both sides of the recording.

</details>

---

:bulb: &nbsp; **Refer Jarvis' [README](https://github.com/thevickypedia/Jarvis/blob/master/README.md) for more information on setting up the backend server.**

### Coding Standards
Docstring format: [`Google`](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) <br>
Styling conventions: [`PEP 8`](https://www.python.org/dev/peps/pep-0008/) <br>
Clean code with pre-commit hooks: [`flake8`](https://flake8.pycqa.org/en/latest/) and
[`isort`](https://pycqa.github.io/isort/)

### [Release Notes](https://github.com/thevickypedia/Jarvis_UI/blob/main/release_notes.rst)
**Requirement**
```shell
python -m pip install gitverse
```

**Usage**
```shell
gitverse-release reverse -f release_notes.rst -t 'Release Notes'
```

### Linting
`PreCommit` will ensure linting, and the doc creation are run on every commit.

**Requirement**
<br>
```bash
python -m pip install sphinx==5.1.1 pre-commit recommonmark
```

**Usage**
<br>
```bash
pre-commit run --all-files
```

### Pypi Package
[![pypi-module](https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg)](https://packaging.python.org/tutorials/packaging-projects/)

[https://pypi.org/project/jarvis-ui/](https://pypi.org/project/jarvis-ui/)

### Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html)

[https://thevickypedia.github.io/Jarvis_UI/](https://thevickypedia.github.io/Jarvis_UI/)

### License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License](https://github.com/thevickypedia/Jarvis_UI/blob/main/LICENSE)
