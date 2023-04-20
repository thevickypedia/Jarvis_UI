#!/bin/bash

OSName=$(UNAME)
ver=$(python -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")
echo_ver=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")

echo -e '\n***************************************************************************************************'
echo "                               $OSName running python $echo_ver"
echo -e '***************************************************************************************************\n'

if [ "$ver" -ge 38 ] && [ "$ver" -le 311 ]; then
  pyaudio="PyAudio-0.2.11-cp$ver-cp$ver-win_amd64.whl"
else
  echo "Python version $echo_ver is unsupported for Jarvis. Please use any python version between 3.8.* and 3.11.*"
  exit
fi

# Upgrades pip module
python -m pip install --upgrade pip

os_independent_packages() {
    # Get to the current directory and install the module specific packages from requirements.txt
    current_dir="$(dirname "$(realpath "$0")")"
    python -m pip install --no-cache-dir -r "$current_dir"/requirements.txt
}

if [[ "$OSName" == "Darwin" ]]; then
    # Looks for xcode installation and installs only if xcode is not found already
    which xcodebuild > tmp_xcode && xcode_check=$(cat tmp_xcode) && rm tmp_xcode
    if  [[ "$xcode_check" == "/usr/bin/xcodebuild" ]] || [[ $HOST == "/*" ]] ; then
        xcode_version=$(pkgutil --pkg-info=com.apple.pkg.CLTools_Executables | grep version)
        echo "xcode $xcode_version"
    else
        echo "Installing xcode"
        xcode-select --install
    fi

    # Looks for brew installation and installs only if brew is not found
    brew_check=$(which brew)
    if [[ "$brew_check" == "/usr/local/bin/brew" ]] || [[ "$brew_check" == "/usr/bin/brew" ]]; then
        brew -v > tmp_brew && brew_version=$(head -n 1 tmp_brew) && rm tmp_brew
        echo "$brew_version"
    else
        echo "Installing Homebrew"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
    fi
    brew install portaudio coreutils
    python -m pip install PyAudio==0.2.13

    # Checks current version and installs legacy pvporcupine version if macOS is older han 10.14
    base_ver="10.14"
    os_ver=$(sw_vers | grep ProductVersion | cut -d':' -f2 | tr -d ' ')
    if awk "BEGIN {exit !($base_ver > $os_ver)}"; then
      pip install 'pvporcupine==1.6.0'
    else
      pip install 'pvporcupine==1.9.5'
    fi
    os_independent_packages
elif [[ "$OSName" == MSYS* ]]; then
    conda install portaudio=19.6.0
    # PyAudio wheel files original source:
    # https://www.lfd.uci.edu/~gohlke/pythonlibs/#:~:text=PyAudio:%20bindings%20for%20the%20PortAudio%20library
    curl https://vigneshrao.com/Jarvis/"$pyaudio" --output "$pyaudio" --silent
    pip install "$pyaudio"
    rm "$pyaudio"
    pip install 'pvporcupine==1.9.5'
    os_independent_packages
elif [[ "$OSName" == "Linux" ]]; then
    dev_ver=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    sudo apt install -y "python$dev_ver-distutils"  # Install distutils for the current python version
    sudo apt-get install -y git libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
    sudo apt install -y build-essential ffmpeg espeak python3-pyaudio "python$dev_ver-dev"
    python -m pip install PyAudio==0.2.12 pvporcupine==1.9.5
    os_independent_packages
else
    clear
    echo "*****************************************************************************************************************"
    echo "*****************************************************************************************************************"
    echo ""
    echo "Current Operating System: $OSName"
    echo "Jarvis is currently supported only on Linux, MacOS and Windows"
    echo ""
    echo "*****************************************************************************************************************"
    echo "*****************************************************************************************************************"
fi
