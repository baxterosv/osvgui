# If the import fails, it's because Python 2.x is expecting "import Tkinter" and not "import tkinter".
# Use update-alternatives to force Python 3.  For instructions, see: https://raspberry-valley.azurewebsites.net/Python-Default-Version/

import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
#import animation for continuous graphing update
import matplotlib.animation as animation


import numpy as np

import zmq
import time
from enum import Enum
import logging
import sys

logging.basicConfig(level=logging.INFO)

PLOT_INTERVAL = 0.1 #seconds
PLOT_LENGTH = 10 #seconds
BLANK_TIME = 0.2 #seconds
ARRAY_SIZE = int(PLOT_LENGTH/PLOT_INTERVAL)


class State(Enum):
    RUNNING = 1
    PAUSED = 2


class GraphFrame(tkinter.LabelFrame):

    def __init__(self, master, title, titleFont, padx, pady): #, domain):
        tkinter.LabelFrame.__init__(self, master, text=title, font=titleFont)

        self.fig = Figure(figsize=(10,2),dpi=100)
        
        #instantiate array sizes
        self.t_pts = np.arange(0,PLOT_LENGTH,PLOT_INTERVAL)
        self.vol_pts = np.empty(ARRAY_SIZE)
        self.press_pts = np.zeros(ARRAY_SIZE)
        
        #add blank graphs
        self.graph_vol = self.fig.add_subplot(211)
        self.graph_press = self.fig.add_subplot(212)
        self.graph_vol.plot(self.t_pts, self.vol_pts)
        self.graph_press.plot(self.t_pts, self.press_pts)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=padx, pady=pady, sticky='nesw')
        self.canvas.draw()

        #self.domain = domain

        self.plot_time = 0

        #variable for interating through index
        self.current_index = 0

        #self.toolbar = NavigationToolbar2Tk(self.canvas, master)
        #self.toolbar.update()
        #self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    #function to update values from vol_control.py
    # def add_point(self, val, t):
    #     p, v = val
    #     self.vol_pts[self.current_index] = v
    #     self.press_pts[self.current_index] = p
    #     for i in (1,round(BLANK_TIME/PLOT_INTERVAL)):
    #         self.vol_pts[(self.current_index+i)%ARRAY_SIZE] = np.NaN
    #         self.press_pts[(self.current_index+i)%ARRAY_SIZE] = np.NaN
    #     self.current_index = (self.current_index+1)%ARRAY_SIZE
        

    #function to auto-update graphing widget
    def update_graph(self, val):
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

        self.graph_press.set_ylabel('Pressure (PSI)')
        self.graph_vol.set_ylabel('Volume (ml)')
        self.graph_vol.set_xlabel('Time (s)')
        

        self.fig.set_size_inches(10,2) #For some reason (probably a bug in a library) the size gets forgotten and causes error
        self.canvas.draw()


class ValueControlFrame(tkinter.LabelFrame):

    def __init__(self, master, title, unit, default, minimum, maximum, 
                 step, enabled, padx, pady, font, titleFont):
        self.padx = padx
        self.pady = pady
        tkinter.LabelFrame.__init__(self, master, text=title, font=titleFont)

        self.tracked_val = default
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

        self.new_val_string = tkinter.StringVar()
        self.current_val_string = tkinter.StringVar()
        self.new_val_string.set(default)
        self.current_val_string.set('None')

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.btn1 = tkinter.Button(self, state=enabled, text="+",
                                   font=font, bg='SlateGray3', command=self._increment_val)
        self.btn1.grid(row=0, column=0, sticky='nesw',
                       padx=self.padx, pady=self.pady)
        self.btn2 = tkinter.Button(self, state=enabled, text="-",
                                   font=font, bg='SlateGray3', command=self._decrement_val)
        self.btn2.grid(row=3, column=0, sticky='nesw',
                       padx=self.padx, pady=self.pady)

        self.lbl1 = tkinter.Label(self, text='Current')
        self.lbl1.grid(row=0, column=1, sticky='esw')
        self.lbl1.config(font=font)

        self.lbl2 = tkinter.Label(
            self, textvariable=self.current_val_string, bg='SlateGray1')
        self.lbl2.grid(row=1, column=1, sticky='nesw')
        self.lbl2.config(font=font)

        self.lbl3 = tkinter.Label(
            self, textvariable=self.new_val_string, bg='SlateGray3')
        self.lbl3.grid(row=2, column=1, sticky='nesw')
        self.lbl3.config(font=font)

        self.lbl1 = tkinter.Label(self, text='New')
        self.lbl1.grid(row=3, column=1, sticky='new')
        self.lbl1.config(font=font)

        self.lbl5 = tkinter.Label(self, text=unit)
        self.lbl5.grid(row=0, column=2, rowspan=4, sticky='nesw')
        self.lbl5.config(font=font)

    def set_new_val_string(self, s):
        self.new_val_string.set(s)

    def set_current_val_string(self, s):
        self.current_val_string.set(s)

    def get_val(self):
        return self.tracked_val

    def _increment_val(self):

        upper = self.maximum
        step = self.step
        if self.tracked_val < upper:
            self.tracked_val = self.tracked_val + step
            if self.tracked_val > upper:
                self.tracked_val = upper
        self.set_new_val_string(round(self.tracked_val, 2))

    def _decrement_val(self):
        lower = self.minimum
        step = self.step
        if self.tracked_val > lower:
            self.tracked_val = self.tracked_val - step
            if self.tracked_val < lower:
                self.tracked_val = lower
        self.set_new_val_string(round(self.tracked_val, 2))


class VentilatorGUI():

    def __init__(self, root):

        self.ZMQ_GUI_TOPIC = "ipc:///tmp/gui_setpoint.pipe"
        self.ZMQ_VOL_HEARTBEAT_TOPIC = "ipc:///tmp/vol_data.pipe"
        self.ZMQ_POLL_TIMEOUT_MS = 10
        self.ZMQ_POLLER_CHECK_PERIOD_MS = int(PLOT_INTERVAL*100)
        self.ZMQ_HEARTBEAT_INTERVAL_MS = 1000
        self.DEFAULT_OXYGEN_LEVEL = 40
        self.DEFAULT_TOTAL_VOLUME = 400
        self.DEFAULT_RESPITORY_RATE = 14
        self.DEFAULT_INSPITORY_PERIOD = 1.0
        self.MAX_OXYGEN_LEVEL = 100
        self.MAX_TOTAL_VOLUME = 700
        self.MAX_RESPITORY_RATE = 30
        self.MAX_INSPITORY_PERIOD = 2.0
        self.MIN_OXYGEN_LEVEL = 20
        self.MIN_TOTAL_VOLUME = 200
        self.MIN_RESPITORY_RATE = 10
        self.MIN_INSPITORY_PERIOD = 0.5
        self.STEP_OXYGEN_LEVEL = 10
        self.STEP_TOTAL_VOLUME = 50
        self.STEP_RESPITORY_RATE = 1
        self.STEP_INSPITORY_PERIOD = 0.1
        self.PADX = 10
        self.PADY = 10

        font = ('', 12, 'bold')
        titleFont = ('', 18, 'bold')

        self.state = State.PAUSED
        self.oxygenlevel = self.DEFAULT_OXYGEN_LEVEL
        self.totalvolume = self.DEFAULT_TOTAL_VOLUME
        self.respiratoryrate = self.DEFAULT_RESPITORY_RATE
        self.inspitoryperiod = self.DEFAULT_INSPITORY_PERIOD
        self.lastvolheartbeat = None
        self.status = tkinter.StringVar()
        self.status.set("Waiting for connection from daemon...")

        logging.info("Initializing ZeroMQ...")
        ctxt = zmq.Context()
        self.setpntpub = ctxt.socket(zmq.PUB)
        self.setpntpub.connect(self.ZMQ_GUI_TOPIC)

        self.voldatasub = ctxt.socket(zmq.SUB)
        self.voldatasub.bind(self.ZMQ_VOL_HEARTBEAT_TOPIC)
        self.voldatasub.setsockopt_string(zmq.SUBSCRIBE, '')

        self.poller = zmq.Poller()
        self.poller.register(self.voldatasub, zmq.POLLIN)

        # NOTE Solves "slow joiner"; better way is to set up local subscriber to check
        time.sleep(0.2)
        logging.info("ZeroMQ finished init...")

        self.root = root
        self.root.title('OSV')
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', self._quit_osv_gui_callback)

        # A frame to hold other frames
        # Currently working on a resizable version of this...
        self.MainFrame = tkinter.Frame(
            root, borderwidth=0, highlightthickness=0)
        self.MainFrame.pack(anchor='center', fill='both',
                            expand=True, side='top')
        #self.MainFrame.grid(row=0, column=0, sticky='nesw')

        self.MainFrame.grid_rowconfigure(0, weight=2)
        self.MainFrame.grid_rowconfigure(1, weight=2)
        self.MainFrame.grid_rowconfigure(2, weight=1)
        self.MainFrame.grid_rowconfigure(3, weight=3)
        self.MainFrame.grid_columnconfigure(0, weight=1)
        self.MainFrame.grid_columnconfigure(1, weight=1)

        # Frames to control values sent to daemon
        self.oxygenLevelFrame = ValueControlFrame(
            self.MainFrame, "Oxygen Level", "%", self.DEFAULT_OXYGEN_LEVEL, 
            self.MIN_OXYGEN_LEVEL, self.MAX_OXYGEN_LEVEL, self.STEP_OXYGEN_LEVEL, 
            'disabled', self.PADX, self.PADY, font, titleFont)
        self.oxygenLevelFrame.grid(
            row=0, column=0, padx=self.PADX, pady=self.PADY, sticky='nesw')

        self.totalVolumeFrame = ValueControlFrame(
            self.MainFrame, "Total Volume", "ml", self.DEFAULT_TOTAL_VOLUME, 
            self.MIN_TOTAL_VOLUME, self.MAX_TOTAL_VOLUME, self.STEP_TOTAL_VOLUME, 
            'normal', self.PADX, self.PADY, font, titleFont)
        self.totalVolumeFrame.grid(
            row=0, column=1, padx=self.PADX, pady=self.PADY, sticky='nesw')

        self.respiratoryRateFrame = ValueControlFrame(
            self.MainFrame, "Respiratory Rate", "bmp", self.DEFAULT_RESPITORY_RATE, 
            self.MIN_RESPITORY_RATE, self.MAX_RESPITORY_RATE, self.STEP_RESPITORY_RATE, 
            'normal', self.PADX, self.PADY, font, titleFont)
        self.respiratoryRateFrame.grid(
            row=1, column=0, padx=self.PADX, pady=self.PADY, sticky='nesw')

        self.inspiratoryPeriodFrame = ValueControlFrame(
            self.MainFrame, "Inspiration Period", "s", self.DEFAULT_INSPITORY_PERIOD, 
            self.MIN_INSPITORY_PERIOD, self.MAX_INSPITORY_PERIOD, self.STEP_INSPITORY_PERIOD, 
            'normal', self.PADX, self.PADY, font, titleFont)
        self.inspiratoryPeriodFrame.grid(
            row=1, column=1, padx=self.PADX, pady=self.PADY, sticky='nesw')

        # Stop/Start/Apply frame
        self.StopStartApplyFrame = tkinter.LabelFrame(
            self.MainFrame, text='Controls', font=titleFont)
        self.StopStartApplyFrame.grid(
            row=2, column=0, padx=self.PADX, pady=self.PADY, sticky='nesw')
        self.StopStartApplyFrame.grid_rowconfigure(0, weight=1)
        self.StopStartApplyFrame.grid_columnconfigure(0, weight=1)
        self.StopStartApplyFrame.grid_columnconfigure(1, weight=1)
        self.StopStartApplyFrame.grid_columnconfigure(2, weight=1)

        # NOTE Putting this button in its own frame with grid_propogate(False)
        # stops the text change from resizing other buttons
        self.frame_startstopbutton = tkinter.Frame(self.StopStartApplyFrame)
        self.frame_startstopbutton.grid(row=0, column=0, sticky='nesw')
        self.frame_startstopbutton.grid_rowconfigure(0, weight=1)
        self.frame_startstopbutton.grid_columnconfigure(0, weight=1)
        self.frame_startstopbutton.grid_propagate(False)
        self.button_startstop = tkinter.Button(
            self.frame_startstopbutton, text="Start", font=font, bg='Green', command=self._start_stop_pressed)
        self.button_startstop.grid(
            row=0, column=0, sticky='nesw', padx=self.PADX, pady=self.PADY)

        self.button_apply = tkinter.Button(
            self.StopStartApplyFrame, text="Apply Settings", font=font, bg='Blue', command=self._apply_pressed)
        self.button_apply.grid(
            row=0, column=1, sticky='nesw', padx=self.PADX, pady=self.PADY)

        self.button_quit = tkinter.Button(
            self.StopStartApplyFrame, text="Quit", font=font, bg='Orange', command=self._quit_osv_gui_callback)
        self.button_quit.grid(row=0, column=2, sticky='nesw',
                              padx=self.PADX, pady=self.PADY)

        # Status frame

        self.frame_status = tkinter.LabelFrame(
            self.MainFrame, text='Status', font=titleFont)
        self.frame_status.grid(
            row=2, column=1, padx=self.PADX, pady=self.PADY, sticky='nesw')
        self.frame_status.grid_rowconfigure(0, weight=1)
        self.frame_status.grid_columnconfigure(0, weight=1)
        self.frame_status.grid_propagate(False)

        self.lbl9 = tkinter.Label(
            self.frame_status, textvariable=self.status)
        self.lbl9.grid(row=0, column=0, sticky='nesw')
        self.lbl9.config(font=font)
        self.lbl9.configure(anchor='center')

        self.graph_test = GraphFrame(self.MainFrame, "A graph", titleFont, self.PADX, self.PADY)
        self.graph_test.grid(
            row=3, column=0, padx=self.PADX, pady=self.PADY, sticky='nesw', columnspan=2)
        self.graph_test.update()
        self.graph_test.fig.set_figheight(self.graph_test.winfo_height())
        self.graph_test.fig.set_figwidth(self.graph_test.winfo_width())
        self.graph_test.fig.set_dpi(100)
        self.graph_test.update()
        

        # Set a recurring task to poll for heartbeat from daemons
        self.root.after(self.ZMQ_POLLER_CHECK_PERIOD_MS,
                        self._zmq_poll_heartbeat_callback)

    def _zmq_poll_heartbeat_callback(self):
        socks = dict(self.poller.poll(self.ZMQ_POLL_TIMEOUT_MS))
        if self.voldatasub in socks:
            self.lastvolheartbeat = self.voldatasub.recv_pyobj()
            self.graph_test.update_graph(self.lastvolheartbeat)
            self.status.set(self.lastvolheartbeat)
        self.root.after(self.ZMQ_POLLER_CHECK_PERIOD_MS,
                        self._zmq_poll_heartbeat_callback)

    def _quit_osv_gui_callback(self, event=None):
        logging.info('Exiting OSV GUI...')
        self.root.destroy()

    # Just changes start/stop state, doesn't effect values
    def _start_stop_pressed(self):
        logging.info(self.state)
        
        # Starting
        if self.state == State.PAUSED:
            self.state = State.RUNNING
            Stopped = False
            self.button_startstop.configure(bg='Red', text='Stop')
        # Stopping
        elif self.state == State.RUNNING:
            self.state = State.PAUSED
            Stopped = True
            self.button_startstop.configure(bg='Green', text='Start')
        
        # Build and send message from current values
        m = (self.oxygenlevel, self.totalvolume, 
            self.respiratoryrate, self.inspitoryperiod, 
            Stopped)
        self.setpntpub.send_pyobj(m)

    # Just changes values, doesn't effect start/stop state
    def _apply_pressed(self):
            # Update current values
            self.oxygenlevel = self.oxygenLevelFrame.get_val()
            self.totalvolume = self.totalVolumeFrame.get_val()
            self.respiratoryrate = self.respiratoryRateFrame.get_val()
            self.inspitoryperiod = self.inspiratoryPeriodFrame.get_val()

            # Check if running
            if self.state == State.RUNNING:
                Stopped = False
            elif self.state == State.PAUSED:
                Stopped = True


            # Build and send message from current values
            m = (self.oxygenlevel, self.totalvolume, 
                self.respiratoryrate, self.inspitoryperiod, 
                Stopped)
            self.setpntpub.send_pyobj(m)

    # Heartbeat message sender
    # Runs on startup and then every ZMQ_HEARTBEAT_INTERVAL_MS
    def heartbeat(self):
            if self.state == State.RUNNING:
                Stopped = False
            elif self.state == State.PAUSED:
                Stopped = True

            # Build and send message from current values
            m = (self.oxygenlevel, self.totalvolume, 
                self.respiratoryrate, self.inspitoryperiod, 
                Stopped)
            self.setpntpub.send_pyobj(m)

            # Re-run this function in ZMQ_HEARTBEAT_INTERVAL_MS
            self.root.after(self.ZMQ_HEARTBEAT_INTERVAL_MS, self.heartbeat)


# Start the GUI...
root = tkinter.Tk()
vgui = VentilatorGUI(root)
vgui.heartbeat()
root.mainloop()
