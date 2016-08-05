#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt

START_NODE = 36 # 基本周波数の候補集合の開始ノードナンバー
END_NODE = 60 # 基本周波数の候補集合の終了ノードナンバー

# ノードナンバーを周波数に変換する関数
def nn2hz(notenum):
    return 440.0 * (2.0 ** ((notenum - 69) / 12.0))


# 周波数をノードナンバーに変換する関数
def hz2nn(frequency):
    return int(round(12.0 * (np.log(frequency / 440.0) / np.log(2.0)))) + 69


# SHSで基本周波数を推定する関数
def shs(waveform, sampling_rate):
    # フーリエ変換して振幅軸を計算 
    amp = abs(np.fft.fft(waveform))
    amp = amp[:len(amp)/2]

    # 周波数軸を計算
    frq = np.fft.fftfreq(len(amp), d = 1.0 / sampling_rate)
    frq = frq[:len(frq)/2]
 
    # SHSで基本周波数を推定
    L_List = [] # 基本周波数らしさの集合
    i = START_NODE 
    while i < END_NODE:
        L = 0 # 基本周波数らしさ
        f = nn2hz(i)# ノードナンバーを周波数に変換
        # 仮定した基本周波数に最も近い周波数のインデックスを取得(5倍音までとる)
        near = np.searchsorted(frq, f)
        near2 = np.searchsorted(frq, f*2)
        near3 = np.searchsorted(frq, f*3) 
        near4 = np.searchsorted(frq, f*4)
        near5 = np.searchsorted(frq, f*5)
        # そのインデックスに対するパワーを足し合わせる(周辺も加味する)
        L += (amp[near-3]**2  + amp[near-2]**2  + amp[near-1]**2  + amp[near]**2  + amp[near+1]**2  + amp[near+2]**2  + amp[near+3]**2) 
        L += (amp[near2-3]**2 + amp[near2-2]**2 + amp[near2-1]**2 + amp[near2]**2 + amp[near2+1]**2 + amp[near2+2]**2 + amp[near2+3]**2) * 0.9
        L += (amp[near3-3]**2 + amp[near3-2]**2 + amp[near3-1]**2 + amp[near3]**2 + amp[near3+1]**2 + amp[near3+2]**2 + amp[near3+3]**2) * 0.8
        L += (amp[near4-3]**2 + amp[near4-2]**2 + amp[near4-1]**2 + amp[near4]**2 + amp[near4+1]**2 + amp[near4+2]**2 + amp[near4+3]**2) * 0.7
        L += (amp[near5-3]**2 + amp[near5-2]**2 + amp[near5-1]**2 + amp[near5]**2 + amp[near5+1]**2 + amp[near5+2]**2 + amp[near5+3]**2) * 0.6
        L_List.append(L)
        i += 1

    # 尤度を比較して最大となる候補を基本周波数とする
    max_L = L_List.index(max(L_List)) + START_NODE
    f0 = nn2hz(max_L)
    return f0


# 波形、スペクトログラム、音高を表示する関数
def kadai23(waveform, sampling_rate): 
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

    
    # ■音高を表示(SHSで推定)■
    frame = 100 # 分割フレーム数
    N = len(waveform) / frame # フレーム幅
    start = 0 # 開始位置
    result = [] # 基本周波数を格納する配列
  
    # 短時間フレームごとに基本周波数を推定
    while start < len(waveform):
        # 波形を短時間フレームに分ける
        short_wave = waveform[start:start+N]
        # SHSで基本周波数を推定
        f0 = shs(short_wave, sampling_rate)
        # 基本周波数をN個をプロット
        count = 0
        while count < N:
            result.append(f0)
            count += 1
        start += N

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
        print "Usage: python shs.py <input_filename>"

    filename = argv[1]
    sampling_rate , waveform = scipy.io.wavfile.read(filename)
    waveform = waveform / 32768.0
    kadai23(waveform, sampling_rate)
