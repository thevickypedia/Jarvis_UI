Release Notes
=============

v2.3 (09/10/2023)
-----------------
- Includes a new feature to use custom ``.env`` files
- Minor configuration updates

v2.2 (09/09/2023)
-----------------
- Includes stability and performance improvements
- Improved static audio responses specific to the operating system
- Includes a feature to adjust voice pitch for Linux users

v2.1 (08/30/2023)
-----------------
- Improves overall stability
- Awaits restart when response is spoken
- Includes some minor modifications in type hinting
- Includes a feature to respond even after a restart

v2.0 (05/10/2023)
-----------------
- Fix startup errors on Linux OS
- Provide better user experience with runbook
- Implement background health check process
- Release v2.0

v1.1 (05/10/2023)
-----------------
- Improvements in audio quality for static responses
- Implemented heart beat for server's health check
- Release v1.1

v1.0 (05/06/2023)
-----------------
- Set UI to trigger even when failed to reach server
- Add connection restart wav files for indicators
- Remove timeout and timeout extensions
- Reduce latency in response
- Cleanup unwanted objects

0.8 (04/19/2023)
----------------
- Resolve edge case scenario with `ObjectiveC`
- Check pyttsx3 instantiation in a thread
- Use custom module instead of pyttsx3
- Install coreutils on macOS using brew

0.7 (04/10/2023)
----------------
- Update initialization and installation script
- Unhook version dependencies with changelog-generator

0.5.4 (03/22/2023)
------------------
- Fix interactive mode on Windows OS
- Update requirements.txt
