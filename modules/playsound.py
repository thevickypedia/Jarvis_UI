import os
import wave
from threading import Thread
from typing import NoReturn, Union

import pyaudio
from pydantic import FilePath


class PlayAudio:
    """Instantiates ``PlayAudio`` object to play an audio wav file.

    >>> PlayAudio

    """

    def __init__(self, filename: Union[FilePath, str]):
        """Initializes the necessary args.

        Args:
            filename: Takes the audio filename as an argument.
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(
                f"{filename} not found."
            )
        if not filename.endswith("wav"):
            raise FileExistsError(
                "PlayAudio module can only be used for .wav files."
            )
        # length of data to read.
        self.chunk = 1024

        # open the file for reading.
        self.wave_file = wave.open(f=filename, mode='rb')

        # create an audio object
        self.py_audio = pyaudio.PyAudio()

        # open stream based on the wave object which has been input.
        self.stream = self.py_audio.open(
            format=self.py_audio.get_format_from_width(width=self.wave_file.getsampwidth()),
            channels=self.wave_file.getnchannels(), rate=self.wave_file.getframerate(), output=True
        )

    def play(self) -> NoReturn:
        """Reads the data based on chunk size and plays the stream while writing to the stream."""
        # read data (based on the chunk size)
        data = self.wave_file.readframes(nframes=self.chunk)

        # play stream (looping from beginning of file to the end)
        while data:
            # writing to the stream is what *actually* plays the sound.
            self.stream.write(frames=data)
            data = self.wave_file.readframes(nframes=self.chunk)
        self.close()

    def close(self) -> NoReturn:
        """Closes the wav file and resources blocked by pyaudio."""
        self.wave_file.close()
        self.py_audio.close(stream=self.stream)
        self.stream.close()
        self.py_audio.terminate()


def playsound(sound: Union[FilePath, str], block: bool = True) -> NoReturn:
    """Triggers the ``PlayAudio`` object.

    Args:
        sound: Takes the filename as the argument.
        block: Takes an argument whether to run as a thread to block the current process or not.

    Warnings:
        - Beware of specifying ``block=False`` when combining with other processes that use pyaudio resources.
    """
    player = PlayAudio(filename=str(sound))
    if block:
        player.play()
    else:
        Thread(target=player.play, daemon=True).start()
