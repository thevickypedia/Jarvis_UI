#!/bin/sh

download_from_ext_sources() {
    # Downloads PyAudio's wheel file to install it on Windows
    curl https://vigneshrao.com/Jarvis/PyAudio-0.2.11-cp310-cp310-win_amd64.whl --output PyAudio-0.2.11-cp310-cp310-win_amd64.whl --silent
    pip install PyAudio-0.2.11-cp310-cp310-win_amd64.whl
}

OSName=$(UNAME)

if [[ "$OSName" == "Darwin" ]]; then
    # Checks current version and throws a warning if older han 10.14
    base_ver="10.14"
    ver=$(sw_vers | grep ProductVersion | cut -d':' -f2 | tr -d ' ')
    if awk "BEGIN {exit !($base_ver > $ver)}"; then
        echo -e '\n***************************************************************************************************'
        echo " ** You're running MacOS ${ver#"${ver%%[![:space:]]*}"}. Wake word library is not supported in MacOS older than ${base_ver}. **"
        echo "** This means the audio listened, is converted into text and then condition checked to initiate. **"
        echo -e '***************************************************************************************************\n'
        sleep 3
    fi

    # Looks for brew installation and installs only if brew is not found in /usr/local/bin
    brew_check=$(which brew)
    brew_condition="/usr/local/bin/brew"
    if [[ "$brew_check" != "$brew_condition" ]]; then
        echo "Installing Homebrew"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
        else echo "Found Homebrew, skipping installation"
    fi
    brew install portaudio
    python -m pip install PyAudio==0.2.11 playsound==1.3.0 pyobjc==8.5
elif [[ "$OSName" == MSYS* ]]; then
    conda install portaudio=19.6.0
    python -m pip install playsound==1.2.2
    download_from_ext_sources
else
  sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
  sudo apt-get install ffmpeg libav-tools
  sudo pip install pyaudio
  python -m pip install playsound==1.3.0
fi
