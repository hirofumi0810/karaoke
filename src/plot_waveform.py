#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import scipy.io.wavfile
import numpy
import pylab


def plot_waveform(waveform, sampling_rate, filename):
    """
    波形を表示
    """

    sampling_interval = 1.0 / sampling_rate  # add
    times = numpy.arange(len(waveform)) * sampling_interval  # 各サンプルの時刻
    pylab.plot(times, waveform)  # pair of x- and y-coordinate lists/arrays
    pylab.title("Waveform (" + filename + ")")
    pylab.xlabel("Time[sec]")
    pylab.ylabel("Amplitude")
    pylab.xlim(0, len(waveform) / sampling_rate)
    pylab.ylim([-1, 1])
    pylab.savefig("graph/waveform/" + filename.split("/")[1].split(".")[0] + ".png")
    # pylab.show()


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 2:
        print "Invalid arguments."
        print "Usage: python plot_waveform.py <input_filename>"

    filename = argv[1]
    sampling_rate, waveform = scipy.io.wavfile.read(filename)
    # WAVファイルのフォーマットが符号あり16bit整数であることを仮定し，
    # 波形が-1.0から1.0の範囲に収まるように正規化する
    waveform = waveform / 32768.0
    plot_waveform(waveform, sampling_rate, filename)
