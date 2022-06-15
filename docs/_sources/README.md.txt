# Jarvis UI

Connects to `Jarvis` running in the backend to process request and response via API calls.

#### Mandatory Env Vars:
- `REQUEST_URL`: URL to which the API call has to be made.
- `TOKEN`: Authentication token.

#### Optional Env Vars:
Click [here](https://github.com/thevickypedia/Jarvis#env-variables), for more information.
- `REQUEST_TIMEOUT`: Defaults to `5`
- `SPEECH_TIMEOUT`: Defaults to `5`
- `SENSITIVITY`: Defaults to `0.5`
- `VOICE_TIMEOUT`: Defaults to `3`
- `VOICE_PHRASE_LIMIT`: Defaults to `3`
- `LEGACY_WAKE_WORDS`: Defaults to `jarvis`