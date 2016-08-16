#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import wave
import numpy as np
import pylab


def fourier_transform(filename, start_time, end_time):
    """
    フーリエ変換
    """

    wavfile = wave.open(filename, "r")
    fs = wavfile.getframerate()  # サンプリング周波数
    nsamples = wavfile.getnframes()  # サンプル数
    x = wavfile.readframes(nsamples)
    x = np.frombuffer(x, dtype="int16") / 32768.0  # [-1, +1]に正規化
    wavfile.close()

    # 振幅軸の値を計算
    length = len(x) / fs  # 音声の長さ
    start = int(nsamples * start_time / length)  # 開始フレーム
    end = int(nsamples * end_time / length)  # 終了フレーム
    dt = np.fft.fft(x[start:end])
    amp = abs(dt)
    log = 20 * np.log10(amp)  # dBに変換

    # 周波数軸の値を計算
    frq = np.fft.fftfreq(len(log), d=1.0 / fs)

    # 振幅スペクトルを描画
    pylab.title("Amplitude Spectrum (" + filename + ")")
    pylab.plot(frq[:len(log) / 2], log[:len(log) / 2])
    pylab.xlabel("Frequency[Hz]")
    pylab.ylabel("log Amplitude Spectrum[dB]")
    pylab.xlim([0, fs / 2.0])  # ナイキスト周波数まで
    pylab.savefig("graph/fourier/" + filename.split("/")[1].split(".")[0] + ".png")
    # pylab.show()


if __name__ == "__main__":
    argv = sys.argv

    if not len(argv) in [2, 4]:
        print "Invalid arguments."
        print "Usage: python fourier.py <input_filename> (from <start> to <end>)"
        exit()

    filename = argv[1]

    if len(argv) == 2:
        start = 0
        wavfile = wave.open(filename, "r")
        fs = wavfile.getframerate()  # サンプリング周波数
        nsamples = wavfile.getnframes()  # サンプル数
        x = wavfile.readframes(nsamples)
        x = np.frombuffer(x, dtype="int16") / 32768.0  # [-1, +1]に正規化
        wavfile.close()
        length = len(x) / fs
        end = length

    elif len(argv) == 4:
        start = float(argv[2])
        end = float(argv[3])

    # 区間を指定してフーリエ変換
    fourier_transform(filename, start, end)
