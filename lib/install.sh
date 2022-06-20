#!/bin/sh

ver=$(python -c"import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")
if [ "$ver" -ge 38 ] && [ "$ver" -le 311 ]; then
  filename="PyAudio-0.2.11-cp$ver-cp$ver-win_amd64.whl"
else
  echo "Python version $ver is unsupported for Jarvis. Please use any python version between 3.8 and 3.11"
  exit
fi

# Upgrades pip module
python -m pip install --upgrade pip

os_independent_packages() {
    # Get to the current directory and install the module specific packages from requirements.txt
    current_dir="$(dirname "$(realpath "$0")")"
    python -m pip install --no-cache-dir -r $current_dir/requirements.txt
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

    xcode-select --install
    # Looks for brew installation and installs only if brew is not found in /usr/local/bin
    brew_check=$(which brew)
    brew_condition="/usr/local/bin/brew"
    if [[ "$brew_check" != "$brew_condition" ]]; then
        echo "Installing Homebrew"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
        else echo "Found Homebrew, skipping installation"
    fi
    brew install portaudio
    python -m pip install PyAudio==0.2.11
elif [[ "$OSName" == MSYS* ]]; then
    conda install portaudio=19.6.0
    # PyAudio wheel files original source:
    # https://www.lfd.uci.edu/~gohlke/pythonlibs/#:~:text=PyAudio:%20bindings%20for%20the%20PortAudio%20library
    curl https://vigneshrao.com/Jarvis/$filename --output $filename --silent
    pip install $filename
else
    sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
    sudo apt-get install ffmpeg libav-tools
    sudo pip install pyaudio
fi

os_independent_packages
