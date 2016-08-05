#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import matplotlib.pyplot as plt
import wave


def loudness(filename):
    wavfile = wave.open(filename, "r")
    fs = wavfile.getframerate()  # サンプリング周波数
    nsamples = wavfile.getnframes()  # サンプル数
    x = wavfile.readframes(nsamples)
    x = np.frombuffer(x, dtype="int16") / 32768.0  # [-1, +1]に正規化
    wavfile.close()

    # RMSを抽出
    frame = 1000  # 分割フレーム数
    N = nsamples / frame  # フレーム幅
    start = 0  # 開始位置
    rmsdb = 0
    result = []  # RMS[dB]

    while start < nsamples:
        dt = np.fft.fft(x[start:start + N])
        amp = abs(dt)  # 振幅
        rms = np.sqrt(np.dot(amp, amp) / N)  # RMS
        if rms == 0:
            rmsdb = -1000  # デフォルト(-∞)
        else:
            rmsdb = 20 * np.log10(rms)  # dBに変換
        result.append(rmsdb)
        start += N

    length = float(len(x) / fs)  # 音声の長さ
    times = np.arange(len(result)) * length / frame
    plt.title("Loudness")
    plt.plot(times, result)
    plt.xlabel("Time[sec]")
    plt.ylabel("Loudness[dB]")
    plt.xlim([0, length])
    plt.ylim([-100, max(result) + 10])
    plt.show()


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 2:
        print "Invalid arguments."
        print "Usage: python loudness.py <input_filename>"
        exit()

    filename = argv[1]
    loudness(filename)
