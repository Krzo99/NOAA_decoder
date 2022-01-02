#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: NOAA satelite listener
# Author: domen
# GNU Radio version: v3.8.2.0-57-gd71cd177

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import blocks
import pmt
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
from gnuradio.filter import pfb
from gnuradio.qtgui import Range, RangeWidget

from gnuradio import qtgui

class NOAA_listener(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "NOAA satelite listener")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("NOAA satelite listener")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "NOAA_listener")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.SeletedSatFreq = SeletedSatFreq = 137620000
        self.BaudRate = BaudRate = 4160
        self.variable_qtgui_range_0 = variable_qtgui_range_0 = SeletedSatFreq
        self.samp_rate = samp_rate = 250000
        self.SampleRate = SampleRate = 4*BaudRate
        self.Contrast = Contrast = 300

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_push_sink_0 = zeromq.push_sink(gr.sizeof_char, 1, 'tcp://127.0.0.1:65443', 100, False, -1)
        self._variable_qtgui_range_0_range = Range(SeletedSatFreq-10000, SeletedSatFreq+10000, 1, SeletedSatFreq, 1000)
        self._variable_qtgui_range_0_win = RangeWidget(self._variable_qtgui_range_0_range, self.set_variable_qtgui_range_0, "Frequency shift:", "counter_slider", int)
        self.top_grid_layout.addWidget(self._variable_qtgui_range_0_win)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True #plotconst
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.pyqwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_grid_layout.addWidget(self._qtgui_sink_x_0_win)
        self.pfb_arb_resampler_xxx_0_0 = pfb.arb_resampler_fff(
            BaudRate/SampleRate,
            taps=None,
            flt_size=32)
        self.pfb_arb_resampler_xxx_0_0.declare_sample_delay(0)
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_fff(
            SampleRate/samp_rate,
            taps=None,
            flt_size=32)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)
        self.low_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                SampleRate,
                4160,
                10,
                firdes.WIN_HAMMING,
                6.76))
        self.hilbert_fc_0 = filter.hilbert_fc(10, firdes.WIN_HAMMING, 6.76)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink('F:\\Downloads\\backupRecording.wav', 2, samp_rate, 16)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(Contrast)
        self.blocks_float_to_uchar_0 = blocks.float_to_uchar()
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, 'H:\\Projects\\MeteorM2 listener\\GNURadio\\test\\good_og.wav', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_float_1 = blocks.complex_to_float(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.analog_rail_ff_0 = analog.rail_ff(0, 255)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_rail_ff_0, 0), (self.blocks_float_to_uchar_0, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_complex_to_float_1, 1), (self.blocks_wavfile_sink_0, 1))
        self.connect((self.blocks_complex_to_float_1, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.pfb_arb_resampler_xxx_0_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_float_to_uchar_0, 0), (self.zeromq_push_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_complex_to_float_1, 0))
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.hilbert_fc_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.hilbert_fc_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0_0, 0), (self.analog_rail_ff_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "NOAA_listener")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_SeletedSatFreq(self):
        return self.SeletedSatFreq

    def set_SeletedSatFreq(self, SeletedSatFreq):
        self.SeletedSatFreq = SeletedSatFreq
        self.set_variable_qtgui_range_0(self.SeletedSatFreq)

    def get_BaudRate(self):
        return self.BaudRate

    def set_BaudRate(self, BaudRate):
        self.BaudRate = BaudRate
        self.set_SampleRate(4*self.BaudRate)
        self.pfb_arb_resampler_xxx_0_0.set_rate(self.BaudRate/self.SampleRate)

    def get_variable_qtgui_range_0(self):
        return self.variable_qtgui_range_0

    def set_variable_qtgui_range_0(self, variable_qtgui_range_0):
        self.variable_qtgui_range_0 = variable_qtgui_range_0

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.pfb_arb_resampler_xxx_0.set_rate(self.SampleRate/self.samp_rate)
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_SampleRate(self):
        return self.SampleRate

    def set_SampleRate(self, SampleRate):
        self.SampleRate = SampleRate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.SampleRate, 4160, 10, firdes.WIN_HAMMING, 6.76))
        self.pfb_arb_resampler_xxx_0.set_rate(self.SampleRate/self.samp_rate)
        self.pfb_arb_resampler_xxx_0_0.set_rate(self.BaudRate/self.SampleRate)

    def get_Contrast(self):
        return self.Contrast

    def set_Contrast(self, Contrast):
        self.Contrast = Contrast
        self.blocks_multiply_const_vxx_0.set_k(self.Contrast)





def main(top_block_cls=NOAA_listener, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
