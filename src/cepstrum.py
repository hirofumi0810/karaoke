#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import wave
import numpy as np
import pylab


def cepstrum(filename, start_time, end_time):
    """
    ケプストラムを推定
    """

    wavfile = wave.open(filename, "r")
    fs = wavfile.getframerate()  # サンプリング周波数
    nsamples = wavfile.getnframes()  # サンプル数
    x = wavfile.readframes(nsamples)
    x = np.frombuffer(x, dtype="int16") / 32768.0  # [-1, +1]に正規化
    wavfile.close()

    # 対数振幅スペクトルを計算
    length = len(x) / fs  # 音声の長さ
    start = int(nsamples * start_time / length)  # 開始フレーム
    end = int(nsamples * end_time / length)  # 終了フレーム
    dt = np.fft.fft(x[start:end])
    amplitude = abs(dt)
    log = 10 * np.log10(amplitude)  # dBに変換(■10倍でおK？？？■)

    # スペクトル領域をフーリエ変換してケプストラム領域に移す
    cepstrum = np.real(np.fft.fft(log))

    # 高周波数成分を除去
    cepCoef = 13  # ケプストラム次数
    cpsLif = np.array(cepstrum)  # ケプストラムをコピー
    cpsLif[cepCoef:len(cpsLif) - cepCoef] = 0  # ケプストラムは左右対称

    # ケプストラム領域を逆フーリエ変換してスペクトル領域に戻す
    dftSpc = np.real(np.fft.ifft(cpsLif[:nsamples]))

    # 周波数軸の値を計算
    frq = np.fft.fftfreq(len(dftSpc), d=1.0 / fs)

    # ケプストラムを描画(■ケフレンシー軸の値が不明■)
    pylab.subplot(211)
    pylab.title("Cepstrum")
    pylab.plot(frq[:len(cepstrum) / 2], cepstrum[:len(cepstrum) / 2])
    pylab.xlabel("Quefrency")
    pylab.ylabel("Cepstrum")
    pylab.xlim([0, 200])

    # スペクトル包絡を描画
    pylab.subplot(212)
    pylab.title("Spectrum Envelope")
    pylab.plot(frq[:len(log) / 2], log[:len(log) / 2])
    pylab.plot(frq[:len(dftSpc) / 2], dftSpc[:len(dftSpc) / 2], color="red")
    pylab.xlabel("Frequency{Hz]")
    pylab.ylabel("log Amplitude Spectrum[dB]")
    pylab.xlim([0, fs / 2.0])  # ナイキスト周波数まで
    pylab.savefig("graph/cepstrum/" + filename.split("/")[1].split(".")[0] + ".png")
    # pylab.show()


if __name__ == "__main__":
    argv = sys.argv

    if not len(argv) in [2, 4]:
        print "Invalid arguments."
        print "Usage: python cepstrum.py <input_filename> (from <start> to <end>)"
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

    # 区間を指定してケプストラム分析
    cepstrum(filename, start, end)
