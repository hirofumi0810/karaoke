#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import scipy.io.wavfile
import matplotlib.pyplot as plt

# 周波数をノードナンバーに変換する関数
def hz2nn(frequency):
    return int(round(12.0 * (np.log(frequency / 440.0) / np.log(2.0)))) + 69


# クロマベクトルを計算する関数
def chroma_vector(waveform, sampling_rate):
    # フーリエ変換して振幅軸を計算
    dt = np.fft.fft(waveform)
    amp = abs(dt)
    spectrum = amp[:len(amp)/2]

    # 周波数軸を計算
    frq = np.fft.fftfreq(len(amp), d = 1.0 / sampling_rate)
    frequencies = frq[:len(frq)/2]

    # 0=C, 1=C#, 2=D, ..., 11=B
    cv = np.zeros(12)
    for s, f in zip(spectrum, frequencies):
        if f == 0:
            f = 0.00001  # デフォルト
        nn = hz2nn(f)
        cv[nn % 12] += s
    return cv


# 和音らしさを計算する関数
def waon(cv):
    i = 0 # カウンタ
    root = 0 # 根音
    c3 = 0 # 第3音
    c5 = 0 # 第5音
    L = [] # 和音らしさを格納する配列
     
    # 根音、第3,5音を計算
    while i < 23:
        if i == 0:
            root, c3, c5 = 0, 4, 7
        elif i == 1:
            root, c3, c5 = 1, 5, 8
        elif i == 2:
            root, c3, c5 = 2, 6, 9     
        elif i == 3:
            root, c3, c5 = 3, 7, 10
        elif i == 4:
            root, c3, c5 = 4, 8, 11
        elif i == 5:
            root, c3, c5 = 5, 9, 0
        elif i == 6:
            root, c3, c5 = 6, 10, 1
        elif i == 7:
            root, c3, c5 = 7, 11, 2
        elif i == 8:
            root, c3, c5 = 8, 0, 3
        elif i == 9:
            root, c3, c5 = 9, 1, 4
        elif i == 10:
            root, c3, c5 = 10, 2, 5
        elif i == 11:       
            root, c3, c5 = 11, 3, 6    
        elif i == 12:
            root, c3, c5 = 0, 3, 7
        elif i == 13:
            root, c3, c5 = 1, 4, 8
        elif i == 14:
            root, c3, c5 = 2, 5, 9     
        elif i == 15:
            root, c3, c5 = 3, 6, 10
        elif i == 16:
            root, c3, c5 = 4, 7, 11
        elif i == 17:
            root, c3, c5 = 5, 8, 0
        elif i == 18:
            root, c3, c5 = 6, 9, 1
        elif i == 19:
            root, c3, c5 = 7, 10, 2
        elif i == 20:
            root, c3, c5 = 8, 11, 3
        elif i == 21:
            root, c3, c5 = 9, 0, 4
        elif i == 22:
            root, c3, c5 = 10, 1, 5
        elif i == 23:       
            root, c3, c5 = 11, 2, 6
        # 和音らしさを計算
        L.append(1.0 * cv[root] + 0.5 * cv[c3] + 0.8 * cv[c5])
        i += 1
  
    return L


def harmony(waveform, sampling_rate):
    # ■スペクトログラムを表示■
    plt.subplot(211)
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

    plt.title("Spectrogram, Chromagram")
    plt.xlabel("Time[sec]")
    plt.ylabel("Frequency[Hz]")
    plt.xlim([0, times[-1]])
    plt.ylim([0, max(freqs)])
   
    
    # ■クロマグラムを表示■
    # 短時間フレームごとに和音を推定
    frame = 100 # 分割フレーム数
    N = len(waveform) / frame # フレーム幅
    start = 0 # 開始位置
    result = [] # 推定した和音
  
    while start < len(waveform):
        # 波形を短時間フレームに分割
        short_wave = waveform[start:start+N]
        # クロマベクトルを計算
        cv = chroma_vector(short_wave, sampling_rate)
        # 和音らしさを計算
        L = waon(cv)
        # 和音らしさが最大の和音をこのフレームでの和音と推定
        maxL = L.index(max(L))
        result.append(maxL)
        start += N  

    length = float(len(waveform) / sampling_rate) # 音声の長さ
    times = np.arange(len(result)) * length / frame
    plt.subplot(212)
    plt.plot(times, result)
    plt.xlabel("Time[sec]")
    plt.ylabel("Harmony")
    plt.xlim([0, length])
    plt.ylim([0, 25])
    plt.show()
    

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 2:
        print "Invalid arguments."
        print "Usage: python harmony.py <input_filename>"
        exit()
       
    filename = argv[1]
    sampling_rate , waveform = scipy.io.wavfile.read(filename)
    waveform = waveform / 32768.0
    harmony(waveform , sampling_rate)
