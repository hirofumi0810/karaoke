#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import wave
import pyaudio

SAMPLING_RATE = 48000  # Hz
QUANTIZATION_BITS = 16  # bits
CHANNELS = 1  # monaural
BUF_SIZE = 1024

# 録音用のバッファのサイズ．単位はサンプル1
# バッファサイズ・遅延・音飛びには以下の関係がある
# ハードウェアやアプリケーションに合わせた適切な値の設定が必要
# ----------
# バッファサイズ     大     ---     小
# 遅延              小     ---     大
# 音飛び       起こりにくい --- 起こりやすい


def record(seconds, filename):
    """
    WAVファイルに録音
    """

    # WAVファイルを開き，フォーマットなどを書き込む
    wavfile = wave.open(filename, 'wb')
    wavfile.setframerate(SAMPLING_RATE)
    wavfile.setsampwidth(QUANTIZATION_BITS / 8)
    wavfile.setnchannels(CHANNELS)

    p = pyaudio.PyAudio()
    # 録音デバイス（マイクロホン）と紐付けられたストリームを開く
    stream = p.open(format=p.get_format_from_width(QUANTIZATION_BITS / 8),
                    channels=CHANNELS,
                    rate=SAMPLING_RATE,
                    input=True,
                    frames_per_buffer=BUF_SIZE)

    print "start recording"
    # BUF_SIZE ずつストリームから読み込み，ファイルに書き出す
    remain_samples = int(SAMPLING_RATE * seconds)
    while remain_samples > 0:
        data = stream.read(min(BUF_SIZE, remain_samples))
        wavfile.writeframes(data)
        remain_samples -= BUF_SIZE
    print "finish recording"

    wavfile.close()
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 3:
        print "Invalid arguments."
        print "Usage: python record.py <record_seconds> <output_filename>"
        exit()

    record_seconds = argv[1]
    output_filename = argv[2]
    record(float(record_seconds), output_filename)
