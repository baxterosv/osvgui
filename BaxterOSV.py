# If the import fails, it's because Python 2.x is expecting "import Tkinter" and not "import tkinter".
# Use update-alternatives to force Python 3.  For instructions, see: https://raspberry-valley.azurewebsites.net/Python-Default-Version/

import tkinter
import zmq
import time
from enum import Enum
import logging
import sys

logging.basicConfig(level=logging.INFO)


class State(Enum):
    RUNNING = 1
    PAUSED = 2


class VentilatorGUI():

    def __init__(self, root):

        self.ZMQ_GUI_TOPIC = "ipc:///tmp/gui_setpoint.pipe"
        self.ZMQ_VOL_HEARTBEAT_TOPIC = "ipc:///tmp/vol_heartbeat.pipe"
        self.ZMQ_POLL_TIMEOUT_MS = 10
        self.ZMQ_POLLER_CHECK_PERIOD_MS = 1000
        self.DEFAULT_OXYGEN_LEVEL = 40
        self.DEFAULT_TOTAL_VOLUME = 500
        self.DEFAULT_RESPITORY_RATE = 14
        self.DEFAULT_INSPITORY_PERIOD = 1.0
        self.MAX_OXYGEN_LEVEL = 100
        self.MAX_TOTAL_VOLUME = 1000
        self.MAX_RESPITORY_RATE = 30
        self.MAX_INSPITORY_PERIOD = 2.0
        self.MIN_OXYGEN_LEVEL = 20
        self.MIN_TOTAL_VOLUME = 200
        self.MIN_RESPITORY_RATE = 12
        self.MIN_INSPITORY_PERIOD = 0.5
        self.STEP_OXYGEN_LEVEL = 5
        self.STEP_TOTAL_VOLUME = 10
        self.STEP_RESPITORY_RATE = 1
        self.STEP_INSPITORY_PERIOD = 0.1

        self.status = tkinter.StringVar()
        self.status.set("Stopped")

        # Declare some SrtingVars as they are needed when using textvariable= in a label.
        self.sOxygenLevel = tkinter.StringVar()
        self.sTotalVolume = tkinter.StringVar()
        self.sRespiratoryRate = tkinter.StringVar()
        self.sInspiratoryRate = tkinter.StringVar()

        # GUI Defaults
        FullHeight = 1080
        FullWidth = 1920
        BorderWidth = 3
        HighlightThickness = 0
        QuarterWidth = int(FullWidth/2)
        QuarterHeight = int(FullHeight/2)
        PadX = int(FullWidth/80)
        PadY = int(FullHeight/48)
        ButtonWidth = int(FullWidth/200)
        ButtonHeight = int(ButtonWidth/4)
        TextWidth = int(FullWidth/80)
        TextHeight = int(FullHeight/68)
        FontSize = 20  # int(FullWidth/40)

        labelFont = ('', FontSize, 'bold')
        frameFont = ('', int(FontSize), 'bold')
        buttonFont = ('', FontSize, 'bold')

        self.state = State.PAUSED
        self.oxygenlevel = self.DEFAULT_OXYGEN_LEVEL
        self.totalvolume = self.DEFAULT_TOTAL_VOLUME
        self.respiratoryrate = self.DEFAULT_RESPITORY_RATE
        self.inspitoryperiod = self.DEFAULT_INSPITORY_PERIOD
        self.lastvolheartbeat = None

        # Set the StringVars to default settings.
        self.sOxygenLevel.set(self.oxygenlevel)
        self.sTotalVolume.set(self.totalvolume)
        self.sRespiratoryRate.set(self.respiratoryrate)
        self.sInspiratoryRate.set(self.inspitoryperiod)

        logging.info("Initializing ZeroMQ...")
        ctxt = zmq.Context()
        self.setpntpub = ctxt.socket(zmq.PUB)
        self.setpntpub.connect(self.ZMQ_GUI_TOPIC)

        self.volheartbeatsub = ctxt.socket(zmq.SUB)
        self.volheartbeatsub.bind(self.ZMQ_VOL_HEARTBEAT_TOPIC)
        self.volheartbeatsub.setsockopt_string(zmq.SUBSCRIBE, '')

        self.poller = zmq.Poller()
        self.poller.register(self.volheartbeatsub, zmq.POLLIN)

        # NOTE Solves "slow joiner"; better way is to set up local subscriber to check
        time.sleep(0.2)
        logging.info("ZeroMQ finished init...")

        self.root = root
        self.root.title('OSV')
        self.root.geometry(str(FullWidth) + "x" + str(FullHeight))

        # A frame to hold other frames
        # Currently working on a resizable version of this...
        self.MainFrame = tkinter.LabelFrame(
            root, borderwidth=0, highlightthickness=0, width=FullWidth, height=FullHeight)
        self.MainFrame.pack(anchor='center', fill='y',
                            expand=False, side='top', pady=PadY)
        self.MainFrame.grid_rowconfigure(0, weight=1)
        self.MainFrame.grid_columnconfigure(0, weight=1)

        # Oxygen Level Frame
        self.OxygenLevelFrame = tkinter.LabelFrame(self.MainFrame, text='Oxygen Level', width=QuarterWidth,
                                                   height=QuarterHeight, font=frameFont, borderwidth=BorderWidth, relief='groove')
        self.OxygenLevelFrame.grid(row=0, column=0, padx=PadX, pady=PadY)

        self.btn1 = tkinter.Button(self.OxygenLevelFrame, state="disabled", text="+", width=ButtonWidth, height=ButtonHeight,
                                   font=buttonFont, bg='SlateGray3', command=self.increment_oxygen_level)
        self.btn1.grid(row=0, column=0, pady=int(PadY/2), padx=PadX)
        self.btn2 = tkinter.Button(self.OxygenLevelFrame, state="disabled", text="-", width=ButtonWidth, height=ButtonHeight,
                                   font=buttonFont, bg='SlateGray3', command=self.decrement_oxygen_level)
        self.btn2.grid(row=1, column=0, pady=PadY, padx=PadX)

        self.lbl1 = tkinter.Label(self.OxygenLevelFrame, textvariable=self.sOxygenLevel, width=int(
            TextWidth*0.7), height=int(TextHeight*0.57), bg='SlateGray3')
        self.lbl1.grid(row=0, column=1, rowspan=2,
                       pady=int(PadY*1.5), padx=PadX)
        self.lbl1.config(font=labelFont)
        self.lbl2 = tkinter.Label(self.OxygenLevelFrame, text="%", width=int(
            TextWidth*0.3), height=int(TextHeight*0.43))
        self.lbl2.grid(row=0, column=2, rowspan=2,
                       pady=int(PadY/10), padx=PadX)
        self.lbl2.config(font=labelFont)

        # Total Volume Frame
        self.TotalVolumeFrame = tkinter.LabelFrame(self.MainFrame, text='Total Volume', width=QuarterWidth,
                                                   height=QuarterHeight, font=frameFont, borderwidth=BorderWidth, relief='groove')
        self.TotalVolumeFrame.grid(row=0, column=1, padx=PadX, pady=PadY)

        self.btn3 = tkinter.Button(self.TotalVolumeFrame, text="+", width=ButtonWidth, height=ButtonHeight, font=buttonFont,
                                   bg='SlateGray3', command=self.increment_total_volume)
        self.btn3.grid(row=0, column=0, pady=PadY, padx=PadX)
        self.btn4 = tkinter.Button(self.TotalVolumeFrame, text="-", width=ButtonWidth, height=ButtonHeight, font=buttonFont,
                                   bg='SlateGray3', command=self.decrement_total_volume)
        self.btn4.grid(row=1, column=0, pady=PadY, padx=PadX)

        self.lbl3 = tkinter.Label(self.TotalVolumeFrame, textvariable=self.sTotalVolume, width=int(
            TextWidth*0.7), height=int(TextHeight*0.57), bg='SlateGray3')
        self.lbl3.grid(row=0, column=1, rowspan=2,
                       pady=int(PadY*1.5), padx=PadX)
        self.lbl3.config(font=labelFont)
        self.lbl4 = tkinter.Label(self.TotalVolumeFrame, text="ml", width=int(
            TextWidth*0.3), height=int(TextHeight*0.43))
        self.lbl4.grid(row=0, column=2, rowspan=2,
                       pady=int(PadY/10), padx=PadX)
        self.lbl4.config(font=labelFont)

        # Respiratory Rate Frame
        self.RespiratoryRateFrame = tkinter.LabelFrame(self.MainFrame, text='Respiratory Rate', width=QuarterWidth,
                                                       height=QuarterHeight, font=frameFont, borderwidth=int(TextWidth*0.3), relief='groove')
        self.RespiratoryRateFrame.grid(row=1, column=0, padx=PadX, pady=PadY)

        self.btn5 = tkinter.Button(self.RespiratoryRateFrame, text="+", width=ButtonWidth, height=ButtonHeight, font=buttonFont,
                                   bg='SlateGray3', command=self.increment_respiratory_rate)
        self.btn5.grid(row=0, column=0, pady=int(PadY/2), padx=PadX)
        self.btn6 = tkinter.Button(self.RespiratoryRateFrame, text="-", width=ButtonWidth, height=ButtonHeight, font=buttonFont,
                                   bg='SlateGray3', command=self.decrement_respiratory_rate)
        self.btn6.grid(row=1, column=0, pady=PadY, padx=PadX)

        self.lbl5 = tkinter.Label(self.RespiratoryRateFrame, textvariable=self.sRespiratoryRate, width=int(
            TextWidth*0.7), height=int(TextHeight*0.57), bg='SlateGray3')
        self.lbl5.grid(row=0, column=1, rowspan=2,
                       pady=int(PadY*1.5), padx=PadX)
        self.lbl5.config(font=labelFont)
        self.lbl6 = tkinter.Label(self.RespiratoryRateFrame, text="bpm", width=int(
            TextWidth*0.3), height=int(TextHeight*0.43))
        self.lbl6.grid(row=0, column=2, rowspan=2,
                       pady=int(PadY/10), padx=PadX)
        self.lbl6.config(font=labelFont)

        # Inspiratory Rate Frame
        self.InspiratoryRateFrame = tkinter.LabelFrame(self.MainFrame, text='Inspiratory Period', width=QuarterWidth,
                                                       height=QuarterHeight, font=frameFont, borderwidth=int(TextWidth*0.3), relief='groove')
        self.InspiratoryRateFrame.grid(row=1, column=1, padx=PadX, pady=PadY)

        self.btn7 = tkinter.Button(self.InspiratoryRateFrame, text="+", width=ButtonWidth, height=ButtonHeight, font=buttonFont,
                                   bg='SlateGray3', command=self.increment_inspiratory_period)
        self.btn7.grid(row=0, column=0, pady=int(PadY/2), padx=PadX)
        self.btn8 = tkinter.Button(self.InspiratoryRateFrame, text="-", width=ButtonWidth, height=ButtonHeight, font=buttonFont,
                                   bg='SlateGray3', command=self.decrement_inspiratory_period)
        self.btn8.grid(row=1, column=0, pady=PadY, padx=PadX)

        self.lbl7 = tkinter.Label(self.InspiratoryRateFrame, textvariable=self.sInspiratoryRate, width=int(
            TextWidth*0.7), height=int(TextHeight*0.57), bg='SlateGray3')
        self.lbl7.grid(row=0, column=1, rowspan=2,
                       pady=int(PadY*1.5), padx=PadX)
        self.lbl7.config(font=labelFont)
        self.lbl8 = tkinter.Label(self.InspiratoryRateFrame, text="s", width=int(
            TextWidth*0.3), height=int(TextHeight*0.43))
        self.lbl8.grid(row=0, column=2, rowspan=2,
                       pady=int(PadY/10), padx=PadX)
        self.lbl8.config(font=labelFont)

        # Stop/Start/Apply Frame
        self.StopStartApplyFrame = tkinter.LabelFrame(
            self.MainFrame, borderwidth=0, highlightthickness=0)
        self.StopStartApplyFrame.grid(row=2, column=0, padx=5, pady=5,
                                      columnspan=2, sticky='nsew')
        self.StopStartApplyFrame.grid_rowconfigure(0, weight=1)
        self.StopStartApplyFrame.grid_rowconfigure(1, weight=1)
        self.StopStartApplyFrame.grid_rowconfigure(2, weight=2)
        self.StopStartApplyFrame.grid_columnconfigure(0, weight=1)
        self.StopStartApplyFrame.grid_columnconfigure(1, weight=1)
        self.StopStartApplyFrame.grid_columnconfigure(2, weight=2)

        self.button_startstop = tkinter.Button(self.StopStartApplyFrame, text="Start", width=ButtonWidth, height=ButtonHeight,
                                               font=buttonFont, bg='Green', command=self.start_stop_pressed)
        self.button_startstop.grid(row=0, column=0, sticky='w')

        self.lbl9 = tkinter.Label(
            self.StopStartApplyFrame, textvariable=self.status, width=8, height=1)
        self.lbl9.grid(row=0, column=2, rowspan=2)
        self.lbl9.config(font=labelFont)

        self.button_apply = tkinter.Button(self.StopStartApplyFrame, text="Apply Settings", width=ButtonWidth*2, height=ButtonHeight,
                                           font=buttonFont, bg='Blue', command=self.apply_pressed)
        self.button_apply.grid(row=0, column=1, sticky='w')

        self.root.after(self.ZMQ_POLLER_CHECK_PERIOD_MS, self.zmq_poll_heartbeat_callback)

    def zmq_publish_setpoint_callback(self):
        # self.setpntpub.send_pyobj(m)
        # print(f"Published {m}...")
        pass

    def zmq_poll_heartbeat_callback(self):
        socks = dict(self.poller.poll(self.ZMQ_POLL_TIMEOUT_MS))
        if self.volheartbeatsub in socks:
            self.lastvolheartbeat = self.volheartbeatsub.recv_pyobj()
        self.root.after(self.ZMQ_POLLER_CHECK_PERIOD_MS, self.zmq_poll_heartbeat_callback)
        
    # This needs help!  These functions are being called by the button event and I did not know how to setup/handle a callback.
    # The quick fix was to make a function  for each button. :(

    def increment_oxygen_level(self):
        value = self.oxygenlevel
        upper = self.MAX_OXYGEN_LEVEL
        step = self.STEP_OXYGEN_LEVEL
        if value < upper:
            value = value + step
            if value > upper:
                value = upper
            self.sOxygenLevel.set(value)

    def decrement_oxygen_level(self):
        value = self.oxygenlevel
        lower = self.MIN_OXYGEN_LEVEL
        step = self.STEP_OXYGEN_LEVEL
        if value > lower:
            value = value - step
            if value < lower:
                value = lower
            self.sOxygenLevel.set(value)

    def increment_total_volume(self):
        value = self.totalvolume
        upper = self.MAX_TOTAL_VOLUME
        step = self.STEP_TOTAL_VOLUME
        if value < upper:
            value = value + step
            if value > upper:
                value = upper
            self.sTotalVolume.set(value)

    def decrement_total_volume(self):
        value = self.totalvolume
        lower = self.MIN_TOTAL_VOLUME
        step = self.STEP_TOTAL_VOLUME
        if value > lower:
            value = value - step
            if value < lower:
                value = lower
            self.sTotalVolume.set(value)

    def increment_respiratory_rate(self):
        value = self.respiratoryrate
        upper = self.MAX_RESPITORY_RATE
        step = self.STEP_RESPITORY_RATE
        if value < upper:
            value = value + step
            if value > upper:
                value = upper
            self.sRespiratoryRate.set(value)

    def decrement_respiratory_rate(self):
        value = self.respiratoryrate
        lower = self.MIN_RESPITORY_RATE
        step = self.STEP_RESPITORY_RATE
        if value > lower:
            value = value - step
            if value < lower:
                value = lower
            self.sRespiratoryRate.set(value)

    def increment_inspiratory_period(self):
        value = self.inspitoryperiod
        upper = self.MAX_INSPITORY_PERIOD
        step = self.STEP_INSPITORY_PERIOD
        if value < upper:
            value = value + step
            if value > upper:
                value = upper
            self.sInspiratoryRate.set(value)

    def decrement_inspiratory_period(self):
        value = self.inspitoryperiod
        lower = self.MIN_INSPITORY_PERIOD
        step = self.STEP_INSPITORY_PERIOD
        if value > lower:
            value = value - step
            if value < lower:
                value = lower
            self.sInspiratoryRate.set(value)

    def start_stop_pressed(self):
        logging.info(self.state)
        if self.state == State.PAUSED:
            self.state = State.RUNNING
            self.button_startstop.configure(bg='Red', text='Stop')
        elif self.state == State.RUNNING:
            self.state = State.PAUSED
            self.button_startstop.configure(bg='Green', text='Start')

    def apply_pressed(self):
        self.status.set("Stopped")


# Start the GUI...
root = tkinter.Tk()
vgui = VentilatorGUI(root)
root.mainloop()
