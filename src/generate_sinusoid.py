#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import math
import numpy
import scipy.io.wavfile


def generate_sinusoid(sampling_rate, frequency, duration):
    """
    自己相関を計算
    """

    sampling_interval = 1.0 / sampling_rate
    t = numpy.arange(sampling_rate * duration) * sampling_interval
    waveform = numpy.sin(2.0 * math.pi * frequency * t)

    return waveform


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 2:
        print "Invalid arguments."
        print "Usage: python plot_spectrogram.py <input_filename>"
        exit()

    sampling_rate = 48000.0  # Hz
    frequency = 440.0  # Hz
    duration = 2.0  # seconds
    waveform = generate_sinusoid(sampling_rate, frequency, duration)
    waveform = waveform * 0.9  # avoid clipping noises
    waveform = (waveform * 32768.0). astype('int16')
    filename = argv[1]
    scipy.io.wavfile.write("wav/sinusoid/" + filename.split("/")[1].split(".")
                           [0] + "_sinusoid.wav", int(sampling_rate), waveform)
