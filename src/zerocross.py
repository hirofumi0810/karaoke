#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import scipy.io.wavfile
import matplotlib.pyplot as plt
import pitch  # 音高を抽出するモジュール(関数is_peakを使用)


def zerocross(waveform, sampling_rate, filename):
    """
    ゼロ交差数を推定
    """

    # 短時間フレームごとに基本周波数を推定(非発音区間・無声部の基本周波数は0)
    frame = 30  # 分割フレーム数
    N = len(waveform) / frame  # フレーム幅
    start = 0  # 開始位置
    result = []  # 有声部の基本周波数(他は0)の配列

    while start < len(waveform):
        # ■自己相関の計算による基本周波数の推定■
        # 波形を短時間フレームに分ける
        short_wave = waveform[start:start + N]
        # 自己相関が格納された，長さがlen(short_wave)*2-1の対称な配列を得る
        autocorr = np.correlate(short_wave, short_wave, 'full')
        # 不要な前半を捨てる
        autocorr = autocorr[len(autocorr) / 2:]
        # ピークのインデックスを抽出する
        peakindices = [i for i in range(
            len(autocorr)) if pitch.is_peak(autocorr, i)]
        # インデックス0がピークに含まれていれば捨てる
        peakindices = [i for i in peakindices if i != 0]
        # 自己相関が最大となるインデックスを得る
        max_peak_index = max(peakindices, key=lambda index: autocorr[index])
        # インデックスに対応する周波数を得る
        f0 = 1.0 / max_peak_index * sampling_rate

        # ■次にゼロ交差数を計算し、有声・無声を判定■
        zc = 0
        for i in range(len(short_wave) - 1):
            if ((short_wave[i] > 0.0 and short_wave[i + 1] < 0.0) or
                    (short_wave[i] < 0.0 and short_wave[i + 1] > 0.0)):
                zc += 1
        # print "zc {} / f0 {}".format(zc, f0)
        # 以下でも計算できる
        # sum([1 if x < 0.0 else 0 in x for short_wave[1:] * short_wave[:-1]])

        # 基本周波数がゼロ交差数の2倍を越えないものを有声音とする
        count = 0
        if 2 * zc < f0:
            while count < N:
                result.append(0)  # 無声音または非発音区間(基本周波数は0)
                count += 1
        else:
            while count < N:
                result.append(f0)  # 有声音
                count += 1
        start += N

    # 有声部のみの基本周波数を表示
    plt.subplot(211)
    sampling_interval = 1.0 / sampling_rate
    times = np.arange(len(result)) * sampling_interval
    plt.title("Pitch (" + filename + ")")
    plt.plot(times, result)
    # plt.xlabel("Time[sec]")
    plt.ylabel("F0[Hz]")
    plt.xlim([0, len(result) * sampling_interval])

    # スペクトログラムを表示
    plt.subplot(212)
    window_duration = 40.0 * 1.0e-3  # 窓関数の長さ、単位は秒
    window_shift = 5.0 * 1.0e-3  # 窓関数をスライドさせる長さ、単位は秒
    window_size = int(window_duration * sampling_rate)  # 窓関数のサンプル数
    # 隣接する窓関数の重なり
    window_overlap = int((window_duration - window_shift) * sampling_rate)
    # 窓関数(ハニング窓を使用)
    window = scipy.hanning(window_size)

    sp, freqs, times, ax = plt.specgram(
        waveform,
        NFFT=window_size,
        Fs=sampling_rate,
        window=window,
        noverlap=window_overlap
    )

    plt.title("Spectrogram")
    plt.xlabel("Time[sec]")
    plt.ylabel("Frequency[Hz]")
    plt.xlim([0, times[-1]])
    plt.ylim([0, 1000])
    plt.savefig("graph/zerocross/" + filename.split("/")[1].split(".")[0] + ".png")
    # plt.show()


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 2:
        print "Invalid arguments."
        print "Usage: python zerocross.py <input_filename>"
        exit()

    filename = argv[1]
    sampling_rate, waveform = scipy.io.wavfile.read(filename)
    waveform = waveform / 32768.0
    zerocross(waveform, sampling_rate, filename)
