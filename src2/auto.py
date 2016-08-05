#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt

# 配列aのindex順目の要素がピーク(両隣よりも大きい)であればTrueを返す
def is_peak(a, index):
    if index == 0:
        return False
    elif index == len(a)-1:
        return False
    else:
        if (a[index-1] < a[index]) and (a[index] > a[index+1]):
            return True 
        else:
            return False


# 自己相関で基本周波数を推定する関数
def pitch(waveform , sampling_rate):
    # 短時間フレームごとに基本周波数を推定
    frame = 100 # 分割フレーム数
    N = len(waveform) / frame # フレーム幅
    start = 0 # 開始位置
    result = [] # 基本周波数を格納する配列
  
    while start < len(waveform):
        # 波形を短時間フレームに分ける
        short_wave = waveform[start:start+N]
        # 自己相関が格納された，長さがlen(short_wave)*2-1の対称な配列を得る
        autocorr = np.correlate(short_wave, short_wave, 'full')
        # 不要な前半を捨てる
        autocorr = autocorr[len(autocorr) / 2 : ]
        # ピークのインデックスを抽出する
        peakindices = [i for i in range(len(autocorr)) if is_peak(autocorr, i)]
        # インデックス0がピークに含まれていれば捨てる
        peakindices = [i for i in peakindices if i != 0]
        # 自己相関が最大となるインデックスを得る
        max_peak_index = max(peakindices, key= lambda index: autocorr[index])
        # インデックスに対応する周波数を得る
        f0 = 1.0 / max_peak_index * sampling_rate
        # 基本周波数をN個をプロット
        count = 0
        while count < N:
            result.append(f0)
            count += 1
        start += N
    return result


# 波形、スペクトログラム、音高を表示する関数
def auto(waveform, sampling_rate): 
    # ■波形を表示■
    sampling_interval = 1.0 / sampling_rate 
    times1 = np.arange(len(waveform)) * sampling_interval 
    plt.subplot(311)
    plt.plot(times1 , waveform) 
    plt.title("Waveform, Spectrogram, Pitch")
    plt.xlabel("Time[sec]")
    plt.ylabel("Amplitude")
    plt.xlim(0, len(waveform) / sampling_rate)
    plt.ylim([-1, 1])

   
    # ■スペクトログラムを表示■
    plt.subplot(312)
    window_duration = 40.0 * 1.0e-3 # 窓関数の長さ、単位は秒
    window_shift = 5.0 * 1.0e-3 # 窓関数をスライドさせる長さ、単位は秒
    window_size = int(window_duration * sampling_rate) # 窓関数のサンプル数
    # 隣接する窓関数の重なり
    window_overlap = int((window_duration - window_shift) * sampling_rate)
    window = scipy.hanning(window_size) # 窓関数(ハニング窓を使用)

    sp, freqs , times , ax = plt.specgram(
        waveform ,
        NFFT = window_size,
        Fs = sampling_rate,
        window = window,
        noverlap = window_overlap
    )

    plt.xlabel("Time[sec]")
    plt.ylabel("Frequency[Hz]")
    plt.xlim([0, times[-1]])
    plt.ylim([0, max(freqs)])

    
    # ■音高を表示(自己相関で推定)■  
    result = pitch(waveform, sampling_rate)
    times2 = np.arange(len(result)) * sampling_interval 
    plt.subplot(313)
    plt.plot(times2, result)
    plt.xlabel("Time[sec]")
    plt.ylabel("F0[Hz]")
    plt.xlim([0, len(result) * sampling_interval])
    plt.show()


if __name__ == "__main__": 
    argv = sys.argv
    if len(argv) != 2:
        print "Invalid arguments."
        print "Usage: python auto.py <input_filename>"

    filename = argv[1]
    sampling_rate , waveform = scipy.io.wavfile.read(filename)
    waveform = waveform / 32768.0
    auto(waveform, sampling_rate)
