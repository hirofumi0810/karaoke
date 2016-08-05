#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import wave
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from optparse import OptionParser
from threading import Thread
from player import Player
from recorder import Recorder

# WAVファイルの再生とマイクからの録音を同時に行いながら
# それらの短時間フレームのRMSをリアルタイムに表示する．

DELTA_TIME = 0.001  # seconds
PLOT_FRAMES = 50  # ×0.1秒プロット
PLOT_FREQ_MAX = 2000.0
START_NODE = 36  # 基本周波数の候補集合の開始ノードナンバー
END_NODE = 70  # 基本周波数の候補集合の終了ノードナンバー


class plotter(object):

    def __init__(self, player, recorder,
                 plot_frames=PLOT_FRAMES,
                 plot_freq_max=PLOT_FREQ_MAX,
                 delta_time=DELTA_TIME):
        self.p = player
        self.r = recorder
        self.plot_frames = plot_frames
        self.plot_freq_max = plot_freq_max
        self.delta_time = delta_time

        self.current_frame = -1
        self.p_pitch = np.zeros(self.plot_frames)
        self.r_pitch = np.zeros(self.plot_frames)
        self.r_rms = np.zeros(self.plot_frames)
        self.p_spectrogram = np.ndarray(
            [self.plot_frames, self.p.frame_size / 2 + 1])
        self.p_spectrogram.fill(20.0 * math.log10(1.0e-1))
        self.r_spectrogram = np.ndarray(
            [self.plot_frames, self.r.frame_size / 2 + 1])
        self.r_spectrogram.fill(20.0 * math.log10(1.0e-1))
        self.p_nyquist = self.p.sampling_rate * 0.5
        self.r_nyquist = self.r.sampling_rate * 0.5
        self.p_freqs = np.linspace(
            0.0, self.p_nyquist, self.p.frame_size / 2 + 1)
        self.r_freqs = np.linspace(
            0.0, self.r_nyquist, self.r.frame_size / 2 + 1)

        self.p_plot_freq_max_index = next(
            x[1] for x in zip(self.p_freqs, range(len(self.p_freqs)))
            if x[0] > self.plot_freq_max
        )
        self.r_plot_freq_max_index = next(
            x[1] for x in zip(self.r_freqs, range(len(self.r_freqs)))
            if x[0] > self.plot_freq_max
        )

        self.updated = True

    def __call__(self):
        # テキストファイルを読み込んで歌詞を端末上に表示
        print ""
        f = open('aisiteru.txt', 'r')
        for line in f:
            print line
        f.close()
        plt.ion()
        loop = plotterloop(self)
        loop.start()
        # 図のサイズの変更
        plt.figure(figsize=(12, 8))
        G = gridspec.GridSpec(3, 3)
        while True:
            if not self.updated:
                time.sleep(self.delta_time)
                continue
            plt.clf()
            self.plot_player_pitch(G)
            self.show_player_spec(G)
            self.plot_recorder_pitch(G)
            self.plot_recorder_rms(G)
            self.show_recorder_spec(G)
            plt.draw()
            self.updated = False

    # ■WAVファイル■
    # 基本周波数(SHSで推定)表示
    def plot_player_pitch(self, G):
        plt.subplot(G[1, :-1])
        times = (
            np.arange(self.plot_frames) - self.plot_frames +
            self.current_frame + 1
        ) / self.p.frame_rate
        plt.plot(times, self.p_pitch, 'o-b')
        plt.ylim([0, 500])
        plt.title("Pitch of WAV")
        plt.ylabel("F0[Hz]")

    # スペクトログラム表示
    def show_player_spec(self, G):
        plt.subplot(G[-1, 0])
        extent = [(self.current_frame - self.plot_frames) / self.p.frame_rate,
                  self.current_frame / self.p.frame_rate,
                  0.0, self.plot_freq_max]
        plt.imshow(np.transpose(self.p_spectrogram[:, :self.p_plot_freq_max_index]),
                   extent=extent, origin='lower', aspect='auto')
        plt.title("Spectrogram of WAV")

    # ■録音音声■
    # 基本周波数(SHSで推定)表示
    def plot_recorder_pitch(self, G):
        plt.subplot(G[0, :])
        times = (
            np.arange(self.plot_frames) - self.plot_frames +
            self.current_frame + 1
        ) / self.p.frame_rate
        plt.plot(times, self.r_pitch, 'o-b')
        plt.ylim([0, 500])
        plt.title("Pitch of Voice")
        plt.ylabel("F0[Hz]")

    # RMS表示
    def plot_recorder_rms(self, G):
        plt.subplot(G[1:, -1])
        times = (
            np.arange(self.plot_frames) - self.plot_frames +
            self.current_frame + 1
        ) / self.r.frame_rate
        plt.plot(times, self.r_rms, 'o-b')
        plt.ylim([0, 0.3])
        plt.title("RMS of Voice")
        plt.ylabel("RMS")

    # 録音音声のスペクトログラム表示
    def show_recorder_spec(self, G):
        plt.subplot(G[-1, -2])
        extent = [(self.current_frame - self.plot_frames) / self.r.frame_rate,
                  self.current_frame / self.r.frame_rate,
                  0.0, self.plot_freq_max]
        plt.imshow(np.transpose(self.r_spectrogram[:, :self.r_plot_freq_max_index]),
                   extent=extent, origin='lower', aspect='auto')
        plt.title("Spectrogram of Voice")

    # ■更新■
    def update(self):
        if not self.p.queue.empty():
            wframe = self.p.queue.get()
            sampling_rate = self.p.sampling_rate
            f0 = self.shs(wframe, sampling_rate)  # 基本周波数
            value = self.zerocross_player(wframe, f0)
            if value == 0:
                self.p_pitch[0] = 0  # 無声音
            else:
                self.p_pitch[0] = f0  # 有声音
            self.p_pitch = np.roll(self.p_pitch, -1)
            self.p_spectrogram[0] = np.log(np.abs(np.fft.rfft(wframe)))
            self.p_spectrogram = np.roll(self.p_spectrogram, -1, axis=0)

        if not self.r.queue.empty():
            wframe = self.r.queue.get()
            sampling_rate = self.r.sampling_rate
            f0 = self.shs(wframe, sampling_rate)  # 基本周波数
            value = self.zerocross_recorder(wframe, f0)
            if value == 0:
                self.r_pitch[0] = 0  # 無声音
            else:
                self.r_pitch[0] = f0  # 有声音
            self.r_pitch = np.roll(self.r_pitch, -1)
            self.r_rms[0] = self.rms(wframe)
            self.r_rms = np.roll(self.r_rms, -1)
            self.r_spectrogram[0] = np.log(np.abs(np.fft.rfft(wframe)))
            self.r_spectrogram = np.roll(self.r_spectrogram, -1, axis=0)

        self.updated = True

    # ■RMSを計算■
    def rms(self, waveform):
        amp = abs(np.fft.fft(waveform))  # 振幅
        return math.sqrt(np.dot(amp, amp) / len(amp))

    # ■ノードナンバーを周波数に変換する関数■
    def nn2hz(self, notenum):
        return 440.0 * (2.0 ** ((notenum - 69) / 12.0))

    # ■周波数をノードナンバーに変換する関数■
    def hz2nn(self, frequency):
        return int(round(12.0 * (np.log(frequency / 440.0) / np.log(2.0)))) + 69

    # ■SHSで基本周波数を推定■
    def shs(self, waveform, sampling_rate):
        # フーリエ変換して振幅軸を計算
        amp = abs(np.fft.fft(waveform))
        amp = amp[:len(amp) / 2]
        # 周波数軸を計算
        frq = np.fft.fftfreq(len(amp), d=1.0 / sampling_rate)
        frq = frq[:len(frq) / 2]

        # SHSで基本周波数を推定
        L_List = []  # 基本周波数らしさの集合
        i = START_NODE
        while i < END_NODE:
            L = 0  # 基本周波数らしさ
            f = self.nn2hz(i)  # ノードナンバーを周波数に変換
            # 仮定した基本周波数に最も近い周波数のインデックスを取得(5倍音までとる)
            near = np.searchsorted(frq, f)
            near2 = np.searchsorted(frq, f * 2)
            near3 = np.searchsorted(frq, f * 3)
            near4 = np.searchsorted(frq, f * 4)
            near5 = np.searchsorted(frq, f * 5)
            # そのインデックスに対するパワーを足し合わせる(周辺も加味する)
            L += amp[near - 4] + amp[near - 3] + amp[near - 2] + amp[near - 1] + \
                amp[near] + amp[near + 1]**2 + amp[near + 2] + \
                amp[near + 3] + amp[near + 4]
            L += (amp[near2 - 4] + amp[near2 - 3] + amp[near2 - 2] + amp[near2 - 1] + amp[
                  near2] + amp[near2 + 1]**2 + amp[near2 + 2] + amp[near2 + 3] + amp[near2 + 4]) * 0.9
            L += (amp[near3 - 4] + amp[near3 - 3] + amp[near3 - 2] + amp[near3 - 1] + amp[
                  near3] + amp[near3 + 1]**2 + amp[near3 + 2] + amp[near3 + 3] + amp[near3 + 4]) * 0.8
            L += (amp[near4 - 4] + amp[near4 - 3] + amp[near4 - 2] + amp[near4 - 1] + amp[
                  near4] + amp[near4 + 1]**2 + amp[near4 + 2] + amp[near4 + 3] + amp[near4 + 4]) * 0.7
            L += (amp[near5 - 4] + amp[near5 - 3] + amp[near5 - 2] + amp[near5 - 1] + amp[
                  near5] + amp[near5 + 1]**2 + amp[near5 + 2] + amp[near5 + 3] + amp[near5 + 4]) * 0.6
            # 基本周波数らしさの集合に追加
            L_List.append(L)
            i += 1
        # 尤度を比較して最大となる候補を基本周波数とする
        max_L = L_List.index(max(L_List)) + START_NODE
        f0 = self.nn2hz(max_L)
        return f0

    # ■有声音・無声音を判定■
    # 楽曲用
    def zerocross_player(self, waveform, f0):
        # ゼロ交差数を計算
        zc = 0
        i = 0
        while i < len(waveform) - 1:
            if ((waveform[i] > 0.0 and waveform[i + 1] < 0.0) or
                    (waveform[i] < 0.0 and waveform[i + 1] > 0.0)):
                zc += 1
            i += 1

        # 有声・無声を判定
        if 2 * zc < f0:
            return 0  # 無声音または非発音区間(基本周波数は0)
        else:
            return 1  # 有声音

    # 歌声用
    def zerocross_recorder(self, waveform, f0):
        # ゼロ交差数を計算
        zc = 0
        i = 0
        while i < len(waveform) - 1:
            if ((waveform[i] > 0.0 and waveform[i + 1] < 0.0) or
                    (waveform[i] < 0.0 and waveform[i + 1] > 0.0)):
                zc += 1
            i += 1

        # 有声・無声を判定
        if zc < 20:
            return 0  # 無声音または非発音区間(基本周波数は0)
        else:
            return 1  # 有声音


class plotterloop(Thread):

    def __init__(self, plotter):
        super(plotterloop, self).__init__()
        self.setDaemon(True)
        self.plotter = plotter

    def run(self):
        while True:
            if self.plotter.p.queue.empty() and self.plotter.r.queue.empty():
                time.sleep(DELTA_TIME * 100)
                continue
            self.plotter.update()


def main():
    parser = OptionParser()
    parser.add_option('-v', '--verbose',
                      dest='verbose', action='store_true', default=False,
                      help='verbose output')
    (options, args) = parser.parse_args()
    verbose = options.verbose
    if verbose:
        print 'verbose output mode.'

    if len(args) == 0:
        print 'no input files.'
        exit

    filename = args[0]
    if verbose:
        print 'filename: ' + filename
    p = Player(filename)

    r = Recorder()
    r.start()

    pl = plotter(p, r)
    th = Thread(target=pl)
    th.daemon = True
    th.start()

    p.run()

if __name__ == '__main__':
    main()
