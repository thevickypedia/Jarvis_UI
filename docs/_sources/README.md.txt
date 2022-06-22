![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)

**Deployments**

[![pages-build-deployment](https://github.com/thevickypedia/Jarvis_UI/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/thevickypedia/Jarvis_UI/actions/workflows/pages/pages-build-deployment)
[![pypi](https://github.com/thevickypedia/Jarvis_UI/actions/workflows/python-publish.yml/badge.svg)](https://github.com/thevickypedia/Jarvis_UI/actions/workflows/python-publish.yml)

# Jarvis UI

Connects to [`Jarvis`](https://github.com/thevickypedia/Jarvis/blob/master/api/fast.py) running in the backend to process request and response via API calls.

### Mandatory Env Vars
- `REQUEST_URL`: URL to which the API call has to be made. Can be `localhost` or a `tunneled` URL.
- `TOKEN`: Authentication token.

### Optional Env Vars
Click [here](https://github.com/thevickypedia/Jarvis#env-variables), for more information.
- `REQUEST_TIMEOUT`: Defaults to `5` - _Timeout for API calls_
- `SPEECH_TIMEOUT`: Defaults to `0` for MacOS, `5` for Windows - _Timeout for speech synthesis_
- `SENSITIVITY`: Defaults to `0.5` - _Sensitivity of wake word detection_
- `VOICE_TIMEOUT`: Defaults to `3` - _Timeout for listener once wake word is detected_
- `VOICE_PHRASE_LIMIT`: Defaults to `3` - _Timeout for phrase once listener is activated_
- `LEGACY_WAKE_WORDS`: Defaults to `jarvis` - _Wake words for `MacOS` older than 10.14_
- `NATIVE_AUDIO`: Defaults to `False` - If set to `True`, the response is generated as audio in the source machine.

> ONLY for `MacOS`: `SPEECH_TIMEOUT` is set to `0` by default which deactivates API calls to `/speech-synthesis`

Refer Jarvis' [README](https://github.com/thevickypedia/Jarvis/blob/master/README.md) for more information on setting up the backend server.

#### Coding Standards
Docstring format: [`Google`](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) <br>
Styling conventions: [`PEP 8`](https://www.python.org/dev/peps/pep-0008/) <br>
Clean code with pre-commit hooks: [`flake8`](https://flake8.pycqa.org/en/latest/) and 
[`isort`](https://pycqa.github.io/isort/)

#### Linting
`PreCommit` will ensure linting, and the doc creation are run on every commit.

**Requirement**
<br>
`pip install --no-cache --upgrade sphinx pre-commit recommonmark`

**Usage**
<br>
`pre-commit run --all-files`

#### Pypi Package
[![pypi-module](https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg)](https://packaging.python.org/tutorials/packaging-projects/)

[https://pypi.org/project/jarvis-ui/](https://pypi.org/project/jarvis-ui/)

#### Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html)

[https://thevickypedia.github.io/Jarvis_UI/](https://thevickypedia.github.io/Jarvis_UI/)

### License & copyright

&copy; Vignesh Sivanandha Rao

Licensed under the [MIT License](https://github.com/thevickypedia/Jarvis_UI/blob/main/LICENSE)
