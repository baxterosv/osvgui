#If the import fails, it's because Python 2.x is expecting "import Tkinter" and not "import tkinter".
#Use update-alternatives to force Python 3.  For instructions, see: https://raspberry-valley.azurewebsites.net/Python-Default-Version/

import tkinter
import zmq
import time

def zmq_publish_setpoint_callback():
    global setpntpub
    global OxygenLevel
    global TotalVolume
    global RespiratoryRate
    global InspiratoryRate
    m = (OxygenLevel, TotalVolume, RespiratoryRate, InspiratoryRate)
    setpntpub.send_pyobj(m)
    print(f"Published {m}...")


#This needs help!  These functions are being called by the button event and I did not know how to setup/handle a callback.  
#The quick fix was to make a function  for each button. :(  
def increment_oxygen_level(value,upper,lower,step):
    global OxygenLevel
    if value < upper:
        value = value + step
        if value > upper:
            value = upper
        OxygenLevel = value
        sOxygenLevel.set(OxygenLevel)
        zmq_publish_setpoint_callback()
        return
        
def decrement_oxygen_level(value,upper,lower,step):
    global OxygenLevel
    if value > lower:
        value = value - step
        if value < lower:
            value = lower
        OxygenLevel = value
        sOxygenLevel.set(OxygenLevel)
        zmq_publish_setpoint_callback()
        return

def increment_total_volume(value,upper,lower,step):
    global TotalVolume
    if value < upper:
        value = value + step
        if value > upper:
            value = upper
        TotalVolume = value
        sTotalVolume.set(TotalVolume)
        zmq_publish_setpoint_callback()
        return
        
def decrement_total_volume(value,upper,lower,step):
    global TotalVolume
    if value > lower:
        value = value - step
        if value < lower:
            value = lower
        TotalVolume = value
        sTotalVolume.set(TotalVolume)
        zmq_publish_setpoint_callback()
        return

def increment_respiratory_rate(value,upper,lower,step):
    global RespiratoryRate
    if value < upper:
        value = value + step
        if value > upper:
            value = upper
        RespiratoryRate = value
        sRespiratoryRate.set(RespiratoryRate)
        zmq_publish_setpoint_callback()
        return
        
def decrement_respiratory_rate(value,upper,lower,step):
    global RespiratoryRate
    if value > lower:
        value = value - step
        if value < lower:
            value = lower
        RespiratoryRate = value
        sRespiratoryRate.set(RespiratoryRate)
        zmq_publish_setpoint_callback()
        return
        
def increment_inspiratory_rate(value,upper,lower,step):
    global InspiratoryRate
    if value < upper:
        value = value + step
        if value > upper:
            value = upper
        InspiratoryRate = round(value,2)
        sInspiratoryRate.set(InspiratoryRate)
        zmq_publish_setpoint_callback()
        return
        
def decrement_inspiratory_rate(value,upper,lower,step):
    global InspiratoryRate
    if value > lower:
        value = value - step
        if value < lower:
            value = lower
        round(value, 3)
        InspiratoryRate = round(value,2)
        sInspiratoryRate.set(InspiratoryRate)
        zmq_publish_setpoint_callback()
        return

# Setup ZeroMQ
print("Initializing ZeroMQ...")
ZMQ_GUI_TOPIC = "ipc:///tmp/gui_setpoint.pipe"
ctxt = zmq.Context()
setpntpub = ctxt.socket(zmq.PUB)
setpntpub.connect(ZMQ_GUI_TOPIC)
time.sleep(0.2) # NOTE Solves "slow joiner"; better way is to set up local subscriber to check
print("ZeroMQ finished init...")

#Defaults.  Probably should persist these somehow. 
OxygenLevel = 40
TotalVolume = 500
RespiratoryRate = 14
InspiratoryRate = 1.0

m = (OxygenLevel, TotalVolume, RespiratoryRate, InspiratoryRate)
setpntpub.send_pyobj(m)
print(f"Published {m}...")

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
FontSize = 20#int(FullWidth/40)


labelFont=('', FontSize, 'bold')
frameFont=('', int(FontSize*2/3), 'bold')
buttonFont=('', FontSize, 'bold')


root = tkinter.Tk()
root.title('OSV')
root.geometry(str(FullWidth) + "x" + str(FullHeight))
  
#Declare some SrtingVars as they are needed when using textvariable= in a label. 
sOxygenLevel=tkinter.StringVar()
sTotalVolume=tkinter.StringVar()
sRespiratoryRate=tkinter.StringVar()
sInspiratoryRate=tkinter.StringVar()

#Set the StringVars to default settings.
sOxygenLevel.set(OxygenLevel)
sTotalVolume.set(TotalVolume)
sRespiratoryRate.set(RespiratoryRate)
sInspiratoryRate.set(InspiratoryRate)

#A frame to hold other frames
#Currently working on a resizable version of this... 
MainFrame = tkinter.LabelFrame(root, borderwidth = 0, highlightthickness = 0, width=FullWidth, height=FullHeight)
MainFrame.pack(anchor='center', fill='y', expand=False, side='top', pady=PadY)
MainFrame.grid_rowconfigure(0, weight=1)
MainFrame.grid_columnconfigure(0, weight=1)

#Oxygen Level Frame
OxygenLevelFrame = tkinter.LabelFrame(MainFrame, text='Oxygen Level', width=QuarterWidth, height=QuarterHeight, font=frameFont, borderwidth=BorderWidth, relief='groove')
OxygenLevelFrame.grid(row=0, column=0, padx=PadX, pady=PadY)

btn1 = tkinter.Button(OxygenLevelFrame, text="+", width=ButtonWidth, height=ButtonHeight, font=buttonFont, bg='SlateGray3', command=lambda: increment_oxygen_level(OxygenLevel, 100, 20, 5))
btn1.grid(row=0, column=0, pady=int(PadY/2), padx=PadX)
btn2 = tkinter.Button(OxygenLevelFrame, text="-", width=ButtonWidth, height=ButtonHeight, font=buttonFont, bg='SlateGray3', command=lambda: decrement_oxygen_level(OxygenLevel, 100, 20, 5))
btn2.grid(row=1, column=0, pady=PadY, padx=PadX)

lbl1 = tkinter.Label(OxygenLevelFrame, textvariable=sOxygenLevel, width=int(TextWidth*0.7), height=int(TextHeight*0.57), bg='SlateGray3')
lbl1.grid(row=0, column=1,rowspan=2, pady=int(PadY*1.5), padx=PadX)
lbl1.config(font=labelFont)
lbl2 = tkinter.Label(OxygenLevelFrame, text="%", width=int(TextWidth*0.3), height=int(TextHeight*0.43))
lbl2.grid(row=0, column=2, rowspan=2, pady=int(PadY/10), padx=PadX)
lbl2.config(font=labelFont)

#Total Volume Frame
TotalVolumeFrame = tkinter.LabelFrame(MainFrame, text='Total Volume', width=QuarterWidth, height=QuarterHeight, font=frameFont, borderwidth=BorderWidth, relief='groove')
TotalVolumeFrame.grid(row=0, column=1, padx=PadX, pady=PadY)

btn3 = tkinter.Button(TotalVolumeFrame, text="+", width=ButtonWidth, height=ButtonHeight, font=buttonFont, bg='SlateGray3', command=lambda: increment_total_volume(TotalVolume, 1000, 200, 10))
btn3.grid(row=0, column=0, pady=PadY, padx=PadX)
btn4 = tkinter.Button(TotalVolumeFrame, text="-", width=ButtonWidth, height=ButtonHeight, font=buttonFont, bg='SlateGray3', command=lambda: decrement_total_volume(TotalVolume, 1000, 200, 10))
btn4.grid(row=1, column=0, pady=PadY, padx=PadX)

lbl3 = tkinter.Label(TotalVolumeFrame, textvariable=sTotalVolume, width=int(TextWidth*0.7), height=int(TextHeight*0.57), bg='SlateGray3')
lbl3.grid(row=0, column=1,rowspan=2, pady=int(PadY*1.5), padx=PadX)
lbl3.config(font=labelFont)
lbl4 = tkinter.Label(TotalVolumeFrame, text="ml", width=int(TextWidth*0.3), height=int(TextHeight*0.43))
lbl4.grid(row=0, column=2, rowspan=2, pady=int(PadY/10), padx=PadX)
lbl4.config(font=labelFont)

#Respiratory Rate Frame
RespiratoryRateFrame = tkinter.LabelFrame(MainFrame, text='Respiratory Rate', width=QuarterWidth, height=QuarterHeight, font=frameFont, borderwidth=int(TextWidth*0.3), relief='groove')
RespiratoryRateFrame.grid(row=1, column=0, padx=PadX, pady=PadY)

btn5 = tkinter.Button(RespiratoryRateFrame, text="+", width=ButtonWidth, height=ButtonHeight, font=buttonFont, bg='SlateGray3', command=lambda: increment_respiratory_rate(RespiratoryRate, 30, 12, 1))
btn5.grid(row=0, column=0, pady=int(PadY/2), padx=PadX)
btn6 = tkinter.Button(RespiratoryRateFrame, text="-", width=ButtonWidth, height=ButtonHeight, font=buttonFont, bg='SlateGray3', command=lambda: decrement_respiratory_rate(RespiratoryRate, 30, 12, 1))
btn6.grid(row=1, column=0, pady=PadY, padx=PadX)

lbl5 = tkinter.Label(RespiratoryRateFrame, textvariable=sRespiratoryRate, width=int(TextWidth*0.7), height=int(TextHeight*0.57), bg='SlateGray3')
lbl5.grid(row=0, column=1,rowspan=2, pady=int(PadY*1.5), padx=PadX)
lbl5.config(font=labelFont)
lbl6 = tkinter.Label(RespiratoryRateFrame, text="bpm", width=int(TextWidth*0.3), height=int(TextHeight*0.43))
lbl6.grid(row=0, column=2, rowspan=2, pady=int(PadY/10), padx=PadX)
lbl6.config(font=labelFont)

#Inspiratory Rate Frame
InspiratoryRateFrame = tkinter.LabelFrame(MainFrame, text='Inspiratory Period', width=QuarterWidth, height=QuarterHeight, font=frameFont, borderwidth=int(TextWidth*0.3), relief='groove')
InspiratoryRateFrame.grid(row=1, column=1, padx=PadX, pady=PadY)

btn7 = tkinter.Button(InspiratoryRateFrame, text="+", width=ButtonWidth, height=ButtonHeight, font=buttonFont, bg='SlateGray3', command=lambda: increment_inspiratory_rate(InspiratoryRate, 2, 0.5,0.1))
btn7.grid(row=0, column=0, pady=int(PadY/2), padx=PadX)
btn8 = tkinter.Button(InspiratoryRateFrame, text="-", width=ButtonWidth, height=ButtonHeight, font=buttonFont, bg='SlateGray3', command=lambda: decrement_inspiratory_rate(InspiratoryRate, 2, 0.5,0.1))
btn8.grid(row=1, column=0, pady=PadY, padx=PadX)

lbl7 = tkinter.Label(InspiratoryRateFrame, textvariable=sInspiratoryRate, width=int(TextWidth*0.7), height=int(TextHeight*0.57), bg='SlateGray3')
lbl7.grid(row=0, column=1,rowspan=2, pady=int(PadY*1.5), padx=PadX)
lbl7.config(font=labelFont)
lbl8 = tkinter.Label(InspiratoryRateFrame, text="s", width=int(TextWidth*0.3), height=int(TextHeight*0.43))
lbl8.grid(row=0, column=2, rowspan=2, pady=int(PadY/10), padx=PadX)
lbl8.config(font=labelFont)

root.mainloop()