#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import wave
import pyaudio

BUF_SIZE = 1024  # samples, must be >= 64


def play(filename):
    """
    WAVファイルを再生
    """

    # WAVファイルを開き，フォーマットなどを読み込む
    wavfile = wave.open(filename, 'rb')
    nchannels = wavfile.getnchannels()
    sampling_rate = wavfile.getframerate()
    quantization_bits = wavfile.getsampwidth() * 8
    sample_width = wavfile.getsampwidth()
    nsamples = wavfile.getnframes()
    # length = float(nsamples / sampling_rate)  # 音声の長さ
    # start = int(nsamples * start_time / length)  # 開始フレーム
    # end = int(nsamples * end_time / length)  # 終了フレーム

    print "%s:" % filename
    print "Channels: %d" % nchannels
    print "Sampling Rate: %d Hz" % sampling_rate
    print "Quantization Bits: %d" % quantization_bits
    print "Samples: %d" % nsamples
    print "Duration: %.2f seconds" % (nsamples / float(sampling_rate))

    p = pyaudio.PyAudio()
    # 再生デバイス（スピーカやヘッドホン）と紐付けられたストリームを開く
    stream = p.open(format=p.get_format_from_width(quantization_bits / 8),
                    channels=nchannels,
                    rate=sampling_rate,
                    output=True)

    print "start playing"
    # BUF_SIZE ずつファイルから読み込み，ストリームに書き出す
    remain_samples = nsamples
    while remain_samples > 0:
        buf = wavfile.readframes(BUF_SIZE)
        stream.write(buf)
        remain_samples -= BUF_SIZE
    print "finishplaying"

    stream.stop_stream()
    stream.close()
    p.terminate()
    wavfile.close()


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 2:
        print "Invalid arguments."
        print "Usage: python play.py <input_filename>"
        exit()

    filename = argv[1]
    # start = float(argv[2])
    # end = float(argv[3])
    play(filename)
