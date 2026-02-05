#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Sounding Analyzer
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

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore



from gnuradio import qtgui

class analyze(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Sounding Analyzer", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Sounding Analyzer")
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

        self.settings = Qt.QSettings("GNU Radio", "analyze")

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
        self.samp_rate = samp_rate = 20e6
        self.fft_size = fft_size = 256
        self.cf = cf = 3.1e9

        ##################################################
        # Blocks
        ##################################################
        self._cf_range = Range(1.8e9, 5.5e9, 1e6, 3.1e9, 200)
        self._cf_win = RangeWidget(self._cf_range, self.set_cf, "'cf'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._cf_win)
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("resource = RIO0", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        # No synchronization enforced.

        self.uhd_usrp_source_0.set_center_freq(cf, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_normalized_gain(1, 0)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            256, #size
            samp_rate, #samp_rate
            "Impulse Response", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.1)
        self.qtgui_time_sink_x_0.set_y_axis(0, 500)

        self.qtgui_time_sink_x_0.set_y_label("Magnitude", "")

        self.qtgui_time_sink_x_0.enable_tags(False)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)

        self.qtgui_time_sink_x_0.disable_legend()

        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_c(
            fft_size, #size
            window.WIN_RECTANGULAR, #wintype
            cf, #fc
            samp_rate, #bw
            "Frequency Response", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0.set_update_time(0.1)
        self.qtgui_freq_sink_x_0_0.set_y_axis(-40, 30)
        self.qtgui_freq_sink_x_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_0_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0_0.set_fft_window_normalized(False)

        self.qtgui_freq_sink_x_0_0.disable_legend()


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [2, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_0_win)
        self.fft_vxx_0_1 = fft.fft_vcc(256, False, window.rectangular(fft_size), False, 1)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_size, True, window.rectangular(fft_size), False, 1)
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, window.rectangular(fft_size), False, 1)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_vector_source_x_0 = blocks.vector_source_c((1+0j,1.0000+0.0000j,0.9997-0.0246j,0.9973-0.0739j,0.9891-0.1473j,0.9698-0.2439j,0.9325-0.3612j,0.8691-0.4947j,0.7713-0.6365j,0.6317-0.7752j,0.4457-0.8952j,0.2139-0.9768j,-0.0554-0.9985j,-0.3439-0.9390j,-0.6221-0.7829j,-0.8502-0.5264j,-0.9830-0.1837j,-0.9781+0.2079j,-0.8090+0.5878j,-0.4785+0.8781j,-0.0308+0.9995j,0.4457+0.8952j,0.8302+0.5575j,0.9988+0.0493j,0.8691-0.4947j,0.4457-0.8952j,-0.1534-0.9882j,-0.7136-0.7005j,-0.9939-0.1107j,-0.8370+0.5472j,-0.2737+0.9618j,0.4457+0.8952j,0.9411+0.3382j,0.9032-0.4291j,0.3090-0.9511j,-0.5000-0.8660j,-0.9830-0.1837j,-0.7634+0.6459j,0.0431+0.9991j,0.8302+0.5575j,0.9325-0.3612j,0.2139-0.9768j,-0.7136-0.7005j,-0.9667+0.2558j,-0.2499+0.9683j,0.7390+0.6737j,0.9325-0.3612j,0.0677-0.9977j,-0.8868-0.4622j,-0.7634+0.6459j,0.3324+0.9432j,1.0000+0.0000j,0.3090-0.9511j,-0.8233-0.5677j,-0.7634+0.6459j,0.4457+0.8952j,0.9698-0.2439j,-0.0554-0.9985j,-0.9939-0.1107j,-0.2499+0.9683j,0.9325+0.3612j,0.4457-0.8952j,-0.8629-0.5053j,-0.5421+0.8403j,0.8302+0.5575j,0.5524-0.8336j,-0.8502-0.5264j,-0.4785+0.8781j,0.9135+0.4067j,0.3090-0.9511j,-0.9830-0.1837j,-0.0308+0.9995j,0.9891-0.1473j,-0.3439-0.9390j,-0.8370+0.5472j,0.7390+0.6737j,0.4457-0.8952j,-0.9872-0.1595j,0.1656+0.9862j,0.8691-0.4947j,-0.7791-0.6269j,-0.2737+0.9618j,0.9891-0.1473j,-0.5626-0.8267j,-0.4785+0.8781j,1.0000+0.0000j,-0.5000-0.8660j,-0.4785+0.8781j,0.9973-0.0739j,-0.6221-0.7829j,-0.2737+0.9618j,0.9325-0.3612j,-0.8629-0.5053j,0.1656+0.9862j,0.6317-0.7752j,-0.9981+0.0616j,0.7390+0.6737j,-0.0554-0.9985j,-0.6412+0.7674j,0.9891-0.1473j,-0.8502-0.5264j,0.3324+0.9432j,0.3090-0.9511j,-0.8090+0.5878j,0.9997-0.0246j,-0.8502-0.5264j,0.4457+0.8952j,0.0677-0.9977j,-0.5421+0.8403j,0.8691-0.4947j,-0.9981+0.0616j,0.9325+0.3612j,-0.7136-0.7005j,0.4011+0.9160j,-0.0554-0.9985j,-0.2737+0.9618j,0.5524-0.8336j,-0.7634+0.6459j,0.9032-0.4291j,-0.9781+0.2079j,1.0000+0.0000j,-0.9830-0.1837j,0.9411+0.3382j,-0.8868-0.4622j,0.8302+0.5575j,-0.7791-0.6269j,0.7390+0.6737j,-0.7136-0.7005j,0.7049+0.7093j,-0.7136-0.7005j,0.7390+0.6737j,-0.7791-0.6269j,0.8302+0.5575j,-0.8868-0.4622j,0.9411+0.3382j,-0.9830-0.1837j,1.0000+0.0000j,-0.9781+0.2079j,0.9032-0.4291j,-0.7634+0.6459j,0.5524-0.8336j,-0.2737+0.9618j,-0.0554-0.9985j,0.4011+0.9160j,-0.7136-0.7005j,0.9325+0.3612j,-0.9981+0.0616j,0.8691-0.4947j,-0.5421+0.8403j,0.0677-0.9977j,0.4457+0.8952j,-0.8502-0.5264j,0.9997-0.0246j,-0.8090+0.5878j,0.3090-0.9511j,0.3324+0.9432j,-0.8502-0.5264j,0.9891-0.1473j,-0.6412+0.7674j,-0.0554-0.9985j,0.7390+0.6737j,-0.9981+0.0616j,0.6317-0.7752j,0.1656+0.9862j,-0.8629-0.5053j,0.9325-0.3612j,-0.2737+0.9618j,-0.6221-0.7829j,0.9973-0.0739j,-0.4785+0.8781j,-0.5000-0.8660j,1.0000+0.0000j,-0.4785+0.8781j,-0.5626-0.8267j,0.9891-0.1473j,-0.2737+0.9618j,-0.7791-0.6269j,0.8691-0.4947j,0.1656+0.9862j,-0.9872-0.1595j,0.4457-0.8952j,0.7390+0.6737j,-0.8370+0.5472j,-0.3439-0.9390j,0.9891-0.1473j,-0.0308+0.9995j,-0.9830-0.1837j,0.3090-0.9511j,0.9135+0.4067j,-0.4785+0.8781j,-0.8502-0.5264j,0.5524-0.8336j,0.8302+0.5575j,-0.5421+0.8403j,-0.8629-0.5053j,0.4457-0.8952j,0.9325+0.3612j,-0.2499+0.9683j,-0.9939-0.1107j,-0.0554-0.9985j,0.9698-0.2439j,0.4457+0.8952j,-0.7634+0.6459j,-0.8233-0.5677j,0.3090-0.9511j,1.0000+0.0000j,0.3324+0.9432j,-0.7634+0.6459j,-0.8868-0.4622j,0.0677-0.9977j,0.9325-0.3612j,0.7390+0.6737j,-0.2499+0.9683j,-0.9667+0.2558j,-0.7136-0.7005j,0.2139-0.9768j,0.9325-0.3612j,0.8302+0.5575j,0.0431+0.9991j,-0.7634+0.6459j,-0.9830-0.1837j,-0.5000-0.8660j,0.3090-0.9511j,0.9032-0.4291j,0.9411+0.3382j,0.4457+0.8952j,-0.2737+0.9618j,-0.8370+0.5472j,-0.9939-0.1107j,-0.7136-0.7005j,-0.1534-0.9882j,0.4457-0.8952j,0.8691-0.4947j,0.9988+0.0493j,0.8302+0.5575j,0.4457+0.8952j,-0.0308+0.9995j,-0.4785+0.8781j,-0.8090+0.5878j,-0.9781+0.2079j,-0.9830-0.1837j,-0.8502-0.5264j,-0.6221-0.7829j,-0.3439-0.9390j,-0.0554-0.9985j,0.2139-0.9768j,0.4457-0.8952j,0.6317-0.7752j,0.7713-0.6365j,0.8691-0.4947j,0.9325-0.3612j,0.9698-0.2439j,0.9891-0.1473j,0.9973-0.0739j,0.9997-0.0246j,1.0000+0.0000j), True, fft_size, )
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(fft_size)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.fft_vxx_0_1, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.qtgui_freq_sink_x_0_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.fft_vxx_0_1, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_stream_to_vector_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "analyze")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_freq_sink_x_0_0.set_frequency_range(self.cf, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size

    def get_cf(self):
        return self.cf

    def set_cf(self, cf):
        self.cf = cf
        self.qtgui_freq_sink_x_0_0.set_frequency_range(self.cf, self.samp_rate)
        self.uhd_usrp_source_0.set_center_freq(self.cf, 0)




def main(top_block_cls=analyze, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print("Error: failed to enable real-time scheduling.")

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

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
