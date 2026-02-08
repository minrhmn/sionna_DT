#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Raw Capturing
# Author: Nick Schwarzenberg
# GNU Radio version: 3.9.8.0

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

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time



from gnuradio import qtgui

class capture(gr.top_block, Qt.QWidget):

    def __init__(self, out_file='/root/cir/capture.dat', samp_rate=10e6):
        gr.top_block.__init__(self, "Raw Capturing", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Raw Capturing")
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

        self.settings = Qt.QSettings("GNU Radio", "capture")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Parameters
        ##################################################
        self.out_file = out_file
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.samples = samples = 2048
        self.capture_ms = capture_ms = 10

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "type = b200")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        # No synchronization enforced.

        self.uhd_usrp_source_0.set_center_freq(3.5e9, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_normalized_gain(1, 0)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, samples, int( capture_ms/1e3 * samp_rate ), 10000)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, out_file, False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_keep_m_in_n_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "capture")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_out_file(self):
        return self.out_file

    def set_out_file(self, out_file):
        self.out_file = out_file
        self.blocks_file_sink_0.open(self.out_file)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_keep_m_in_n_0.set_n(int( self.capture_ms/1e3 * self.samp_rate ))
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_samples(self):
        return self.samples

    def set_samples(self, samples):
        self.samples = samples
        self.blocks_keep_m_in_n_0.set_m(self.samples)

    def get_capture_ms(self):
        return self.capture_ms

    def set_capture_ms(self, capture_ms):
        self.capture_ms = capture_ms
        self.blocks_keep_m_in_n_0.set_n(int( self.capture_ms/1e3 * self.samp_rate ))



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--out-file", dest="out_file", type=str, default='/root/cir/capture.dat',
        help="Set out_file [default=%(default)r]")
    parser.add_argument(
        "--samp-rate", dest="samp_rate", type=eng_float, default=eng_notation.num_to_str(float(10e6)),
        help="Set samp_rate [default=%(default)r]")
    return parser


def main(top_block_cls=capture, options=None):
    if options is None:
        options = argument_parser().parse_args()
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print("Error: failed to enable real-time scheduling.")

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(out_file=options.out_file, samp_rate=options.samp_rate)

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
