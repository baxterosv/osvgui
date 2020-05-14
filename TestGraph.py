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


PLOT_INTERVAL = 0.1 #seconds
PLOT_LENGTH = 10 #seconds
BLANK_TIME = 0.2 #seconds
ARRAY_SIZE = int(PLOT_LENGTH/PLOT_INTERVAL)

ZMQ_POLLER_CHECK_PERIOD_MS = 100 #ms


class Application(tk.Frame):
    def __init__(self, master=None):
        
        tk.Frame.__init__(self,master)

        self.root=master

        self.fig = plt.figure(figsize=(8,8))
        self.graph_press = self.fig.add_subplot(211)
        self.graph_vol = self.fig.add_subplot(212)

        self.graph_press.set_ylabel('Pressure (PSI)')
        self.graph_vol.set_ylabel('Volume (ml)')
        self.graph_vol.set_xlabel('Time (s)')

        self.canvas = FigureCanvasTkAgg(self.fig,master=root)
        self.canvas.get_tk_widget().grid(row=0,column=1)
        self.canvas.draw()

        self.ZMQ_MEASUREMENT_TOPIC = "ipc:///tmp/vol_data.pipe"
        self.lastvolread = None

        ctxt = zmq.Context()
        self.voldatasub = ctxt.socket(zmq.SUB)
        self.voldatasub.bind(self.ZMQ_MEASUREMENT_TOPIC)
        self.voldatasub.setsockopt_string(zmq.SUBSCRIBE, '')

        self.poller = zmq.Poller()
        self.poller.register(self.voldatasub, zmq.POLLIN)



        #self.fig = Figure()
        
        #instantiate array sizes
        self.t_pts = np.arange(0,PLOT_LENGTH,PLOT_INTERVAL)
        self.vol_pts = np.empty(ARRAY_SIZE)
        self.press_pts = np.empty(ARRAY_SIZE)
        
        #add blank graphs
        #self.vol_graph = self.fig.add_subplot(211).plot(self.t_pts, self.vol_pts)
        #self.press_graph = self.fig.add_subplot(212).plot(self.t_pts, self.press_pts)

        #self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        #self.canvas.draw()
        #self.canvas.get_tk_widget().grid(row=0, column=0, padx=padx, pady=pady, sticky='nesw')

        #self.domain = domain

        self.plot_time = 0

        #variable for interating through index
        self.current_index = 0

        master.after(ZMQ_POLLER_CHECK_PERIOD_MS, self._zmq_poll_callback)



    def plot(self,val):
        p, v = val
        self.vol_pts[self.current_index] = v
        self.press_pts[self.current_index] = p
        for i in (1,round(BLANK_TIME/PLOT_INTERVAL)):
            self.vol_pts[(self.current_index+i)%ARRAY_SIZE] = np.NaN
            self.press_pts[(self.current_index+i)%ARRAY_SIZE] = np.NaN
        self.current_index = (self.current_index+1)%ARRAY_SIZE

        self.graph_press.clear()
        self.graph_vol.clear()

        self.graph_press.plot(self.t_pts, self.press_pts)
        self.graph_vol.plot(self.t_pts, self.vol_pts)

        self.canvas.draw()


    def _zmq_poll_callback(self):
        socks = dict(self.poller.poll(10))
        if self.voldatasub in socks:
            self.lastvolheartbeat = self.voldatasub.recv_pyobj()
            self.plot(self.lastvolheartbeat)
        self.root.after(ZMQ_POLLER_CHECK_PERIOD_MS, self._zmq_poll_callback)


root=tk.Tk()
app=Application(master=root)
app.mainloop()