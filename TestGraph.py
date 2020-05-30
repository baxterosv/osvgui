import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import tkinter as tk
import tkinter.ttk as ttk
import sys

import zmq

from ScrollingMedicalGraph import ScrollingMedical2Graph


PLOT_INTERVAL = 0.1 #seconds
PLOT_LENGTH = 10 #seconds
BLANK_TIME = 0.2 #seconds
ARRAY_SIZE = int(PLOT_LENGTH/PLOT_INTERVAL)

ZMQ_POLLER_CHECK_PERIOD_MS = 10 #ms

ZMQ_MEASUREMENT_TOPIC = "ipc:///tmp/vol_data.pipe"
lastvolread = None

root=tk.Tk()

scrolling_medical_graph = ScrollingMedical2Graph(root, 10.0, 'Pressure', 'Volume')
scrolling_medical_graph.grid(row=0, column=0, sticky='nesw')

'''
ctxt = zmq.Context()
voldatasub = ctxt.socket(zmq.SUB)
voldatasub.bind(ZMQ_MEASUREMENT_TOPIC)
voldatasub.setsockopt_string(zmq.SUBSCRIBE, '')

poller = zmq.Poller()
poller.register(voldatasub, zmq.POLLIN)

def _zmq_poll_callback():
    socks = dict(poller.poll(10))
    if voldatasub in socks:
        v = voldatasub.recv_pyobj()
        scrolling_medical_graph.add_point(v)
    root.after(ZMQ_POLLER_CHECK_PERIOD_MS, _zmq_poll_callback)

root.after(ZMQ_POLLER_CHECK_PERIOD_MS, _zmq_poll_callback)
'''

root.mainloop()