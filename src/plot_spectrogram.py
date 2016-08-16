#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy
import scipy
import scipy.io.wavfile
import matplotlib.pyplot as plt


def plot_spectrogram(waveform, sampling_rate, window_name, filename):
    """
    スペクトログラムを表示
    """

    window_duration = 40.0 * 1.0e-3  # 窓関数の長さ、単位は秒
    window_shift = 5.0 * 1.0e-3  # 窓関数をスライドさせる長さ、単位は秒
    window_size = int(window_duration * sampling_rate)  # 窓関数のサンプル数
    window_overlap = int((window_duration - window_shift) * sampling_rate)  # 隣接する窓関数の重なり

    # 窓関数本体
    if window_name == "hanning":
        window = scipy.hanning(window_size)  # ハニング窓
    elif window_name == "hamming":
        window = scipy.hamming(window_size)  # ハミング窓
    elif window_name == "gaussian":
        window = scipy.gaussian(window_size)  # ガウス窓??
    elif window_name == "blackman":
        window = scipy.blackman(window_size)  # ブラックマン窓
    elif window_name == "trianglar":
        window = scipy.triang(window_size)  # 三角窓??
    elif window_name == "rectanglar":
        window = scipy.rectang(window_size)  # 矩形窓??
    else:
        print "The window function name is wrong."
        exit()

    sp, freqs, times, ax = plt.specgram(
        waveform,
        NFFT=window_size,
        Fs=sampling_rate,
        window=window,
        noverlap=window_overlap
    )

    plt.title("Spectrogram [" + window_name + "] (" + filename + ")")
    plt.xlabel("Time[sec]")
    plt.ylabel("Frequency[Hz]")
    plt.xlim([0, times[-1]])
    plt.ylim([0, 5000])
    plt.savefig("graph/spectrogram/" + filename.split("/")
                [1].split(".")[0] + "_" + window_name + ".png")
    # plt.show()


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 3:
        print "Invalid arguments."
        print "Usage: python plot_spectrogram.py <input_filename> <window_functionname>"
        exit()

    filename = argv[1]
    window = argv[2]
    sampling_rate, waveform = scipy.io.wavfile.read(filename)
    waveform = waveform / 32768.0
    plot_spectrogram(waveform, sampling_rate, window, filename)
