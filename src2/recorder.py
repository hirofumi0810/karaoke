#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import wave
import numpy as np
import pyaudio
import time
from optparse import OptionParser
from threading import Thread
from Queue import Queue

RECORDER_NCHANNELS = 1
RECORDER_SAMPLING_RATE = 44100
RECORDER_DURATION = 310.0 # 録音時間
RECORDER_FILENAME = "out.wav"
RECORDER_SAMPLE_WIDTH = 2 # bytes
RECORDER_BUF_SIZE = 4000 # samples, must be >= 64

FRAME_DURATION = 0.1 # フレームの長さ[秒]
FRAME_RATE = 10.0 # 1秒あたりのフレーム数

class Recorder(Thread):
    """音響信号録音クラス．
    内部で信号をバッファリングするので
    バッファサイズの設定によらず自由な長さの音響信号を取得可能．
    """

    def __init__(self,
                 sampling_rate = RECORDER_SAMPLING_RATE,
                 duration = RECORDER_DURATION,
                 filename = RECORDER_FILENAME,
                 buf_size = RECORDER_BUF_SIZE,
                 frame_duration = FRAME_DURATION,
                 frame_rate = FRAME_RATE,
                 verbose = False):
        """ Recorderクラスのコンストラクタ．

        Arguments:
        sampling_rate -- サンプリング周波数[Hz]
        duration -- 録音時間[秒]
        filename -- 保存WAVファイル名
        buf_size -- 再生バッファのサイズ[bytes]
        frame_duration -- フレームの長さ[秒]
        frame_rate -- 1秒あたりのフレーム数
        verbose -- 詳細な情報の出力
        """

        super(Recorder, self).__init__()
        self.sampling_rate = sampling_rate
        self.duration = duration
        self.filename = filename
        self.buf_size = buf_size
        self.frame_duration = frame_duration
        self.frame_rate = frame_rate
        self.frame_interval = 1.0 / self.frame_rate
        self.verbose = verbose
        if self.verbose: print"Recorder: sampling_rate: %d" % (self.sampling_rate)
        if self.verbose: print"Recorder: duration: %f" % (self.duration)

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format = self.pa.get_format_from_width(RECORDER_SAMPLE_WIDTH),
            channels = RECORDER_NCHANNELS,
            rate = self.sampling_rate,
            frames_per_buffer = self.buf_size,
            input = True
        )
        self.wav_write = wave.open(filename, 'wb')
        self.wav_write.setnchannels(RECORDER_NCHANNELS)
        self.wav_write.setsampwidth(RECORDER_SAMPLE_WIDTH)
        self.wav_write.setframerate(self.sampling_rate)

        self.frame_size = int(self.sampling_rate * self.frame_duration)
        self.frame_shift = int(self.sampling_rate * self.frame_interval)
        self.frame = np.zeros(self.frame_size)
        self.window = np.hanning(self.frame_size)
        self.frame_replace = min(self.frame_size, self.frame_shift)

        self.pcount = 0
        self.buf = np.ndarray(self.buf_size)
        self.buf_pos = self.buf_size 
        self.queue = Queue()

    def record(self, size):
        buf_remain = len(self.buf) - self.buf_pos
        if buf_remain >= size:
            buf_pos0 = self.buf_pos
            self.buf_pos += size
            return self.buf[buf_pos0:self.buf_pos]
        else:
            frame = np.ndarray(size)
            frame[:buf_remain] = self.buf[self.buf_pos:]
            frame_remain = size - buf_remain
            while frame_remain > self.buf_size:
                buf = self.stream.read(self.buf_size)
                self.wav_write.writeframes("".join(buf))
                self.pcount += 1
                w = np.fromstring(buf, dtype = 'int16') * (2.0 ** -15)
                frame[-frame_remain:-frame_remain + self.buf_size] = w
                frame_remain -= self.buf_size
            if frame_remain > 0: # 0 < frame_remain < self.buf_size
                buf = self.stream.read(self.buf_size) 
                self.wav_write.writeframes("".join(buf))
                self.pcount += 1
                w = np.fromstring(buf, dtype = 'int16') * (2.0 ** -15)
                self.buf[:len(w)] = w[:]
                frame[-frame_remain:] = self.buf[:frame_remain]
                self.buf_pos = frame_remain
            return frame

    def run(self):
        """録音を開始する．
        """
        nsamples_remain = int(self.sampling_rate * self.duration)
        while nsamples_remain > 0:
            frame0 = self.record(self.frame_shift)
            nsamples_remain -= len(frame0)
            if (self.frame_size > self.frame_shift):
                self.frame[:self.frame_shift] = frame0[-self.frame_shift:]
                self.frame = np.roll(self.frame, -self.frame_shift)
            else:
                self.frame = frame0
            wframe = self.frame * self.window
            if self.verbose:
                rms = np.sqrt(np.sum(wframe * wframe) / len(wframe))
                print"Recorder: rms: %g" % (rms)
            self.queue.put(wframe)

def main():
    parser = OptionParser()
    parser.add_option('-v','--verbose',
                      dest ='verbose', action = 'store_true', default = False,
                      help = "verbose output")
    parser.add_option('-d','--duration',
                      dest = 'duration',
                      type = 'float', default = RECORDER_DURATION, 
                      help = "recording duration in seconds")
    parser.add_option('-r','--rate',
                      dest = 'sampling_rate', type= 'int',
                      default = RECORDER_SAMPLING_RATE,
                      help = "sampling rate in Hz")
    parser.add_option('--frame_rate',
                      dest = 'frame_rate', type = 'float', default = FRAME_RATE,
                      help = "number of frames per second")
    parser.add_option('--frame_duration',
                      dest = 'frame_duration', type = 'float', default = FRAME_DURATION,
                      help = "duration of frame in seconds")
    (options , args) = parser.parse_args()
    if options.verbose:
        print "recorder: main: verbose output mode."

    r = Recorder(
        duration = options.duration,
        sampling_rate = options.sampling_rate,
        filename = args[0] if len(args) > 0 else RECORDER_FILENAME,
        frame_rate = options.frame_rate,
        frame_duration = options.frame_duration,
        verbose = options.verbose
    )
    r.start()

if __name__ == '__main__':
    main()
