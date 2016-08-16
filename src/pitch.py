#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt


def is_peak(a, index):
    """
    配列aのindex順目の要素がピーク(両隣よりも大きい)であればTrueを返す
    """

    if index == 0:
        return False
    elif index == len(a) - 1:
        return False
    else:
        if (a[index - 1] < a[index]) and (a[index] > a[index + 1]):
            return True
        else:
            return False


def pitch(waveform, sampling_rate, filename):
    """
    音高を推定
    """

    # 短時間フレームごとに基本周波数を推定
    frame = 100  # 分割フレーム数
    N = len(waveform) / frame  # フレーム幅
    start = 0  # 開始位置
    result = []  # 基本周波数を格納する配列

    while start < len(waveform):
        # 波形を短時間フレームに分ける
        short_wave = waveform[start:start + N]
        # 自己相関が格納された，長さがlen(short_wave)*2-1の対称な配列を得る
        autocorr = np.correlate(short_wave, short_wave, 'full')
        # 不要な前半を捨てる
        autocorr = autocorr[len(autocorr) / 2:]
        # ピークのインデックスを抽出する
        peakindices = [i for i in range(len(autocorr)) if is_peak(autocorr, i)]
        # インデックス0がピークに含まれていれば捨てる
        peakindices = [i for i in peakindices if i != 0]
        # 自己相関が最大となるインデックスを得る
        max_peak_index = max(peakindices, key=lambda index: autocorr[index])
        # インデックスに対応する周波数を得る
        f0 = 1.0 / max_peak_index * sampling_rate
        # 基本周波数をN個をプロット
        count = 0
        while count < N:
            result.append(f0)
            count += 1
        start += N

    sampling_interval = 1.0 / sampling_rate
    times = np.arange(len(result)) * sampling_interval
    plt.title("Pitch (" + filename + ")")
    plt.plot(times, result)
    plt.xlabel("Time[sec]")
    plt.ylabel("F0[Hz]")
    plt.xlim([0, len(result) * sampling_interval])
    plt.savefig("graph/pitch/" + filename.split("/")[1].split(".")[0] + ".png")
    # plt.show()


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 2:
        print "Invalid arguments."
        print "Usage: python pitch.py <input_filename>"
        exit()

    filename = argv[1]
    sampling_rate, waveform = scipy.io.wavfile.read(filename)
    waveform = waveform / 32768.0

    pitch(waveform, sampling_rate, filename)
