#If the import fails, it's because Python 2.x is expecting "import Tkinter" and not "import tkinter".
#Use update-alternatives to force Python 3.  For instructions, see: https://raspberry-valley.azurewebsites.net/Python-Default-Version/

import tkinter

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
		return
		
def decrement_oxygen_level(value,upper,lower,step):
	global OxygenLevel
	if value > lower:
		value = value - step
		if value < lower:
			value = lower
		OxygenLevel = value
		sOxygenLevel.set(OxygenLevel)
		return

def increment_total_volume(value,upper,lower,step):
	global TotalVolume
	if value < upper:
		value = value + step
		if value > upper:
			value = upper
		TotalVolume = value
		sTotalVolume.set(TotalVolume)
		return
		
def decrement_total_volume(value,upper,lower,step):
	global TotalVolume
	if value > lower:
		value = value - step
		if value < lower:
			value = lower
		TotalVolume = value
		sTotalVolume.set(TotalVolume)
		return

def increment_respiratory_rate(value,upper,lower,step):
	global RespiratoryRate
	if value < upper:
		value = value + step
		if value > upper:
			value = upper
		RespiratoryRate = value
		sRespiratoryRate.set(RespiratoryRate)
		return
		
def decrement_respiratory_rate(value,upper,lower,step):
	global RespiratoryRate
	if value > lower:
		value = value - step
		if value < lower:
			value = lower
		RespiratoryRate = value
		sRespiratoryRate.set(RespiratoryRate)
		return
		
def increment_inspiratory_rate(value,upper,lower,step):
	global InspiratoryRate
	if value < upper:
		value = value + step
		if value > upper:
			value = upper
		InspiratoryRate = round(value,2)
		sInspiratoryRate.set(InspiratoryRate)
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
		return

#Defaults.  Probably should persist these somehow. 
OxygenLevel = 40
TotalVolume = 600
RespiratoryRate = 14
InspiratoryRate = 1.0

labelFont=('', 20, 'bold')
frameFont=('', 14, 'bold')
buttonFont=('', 20, 'bold')

root = tkinter.Tk()
root.title('OSV')
root.geometry("800x480") 
  
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
MainFrame = tkinter.LabelFrame(root, borderwidth = 0, highlightthickness = 0, width=800, height=480)
MainFrame.pack(anchor='center', fill='y', expand=False, side='top', pady=10)
MainFrame.grid_rowconfigure(0, weight=1)
MainFrame.grid_columnconfigure(0, weight=1)

#Oxygen Level Frame
OxygenLevelFrame = tkinter.LabelFrame(MainFrame, text='Oxygen Level', width=400, height=240, font=frameFont, borderwidth=3, relief='groove')
OxygenLevelFrame.grid(row=0, column=0, padx=10, pady=10)

btn1 = tkinter.Button(OxygenLevelFrame, text="+", width=4, height=1, font=buttonFont, bg='SlateGray3', command=lambda: increment_oxygen_level(OxygenLevel, 100, 20, 5))
btn1.grid(row=0, column=0, pady=5, padx=10)
btn2 = tkinter.Button(OxygenLevelFrame, text="-", width=4, height=1, font=buttonFont, bg='SlateGray3', command=lambda: decrement_oxygen_level(OxygenLevel, 100, 20, 5))
btn2.grid(row=1, column=0, pady=10, padx=10)

lbl1 = tkinter.Label(OxygenLevelFrame, textvariable=sOxygenLevel, width=7, height=4, bg='SlateGray3')
lbl1.grid(row=0, column=1,rowspan=2, pady=15, padx=10)
lbl1.config(font=labelFont)
lbl2 = tkinter.Label(OxygenLevelFrame, text="%", width=3, height=3)
lbl2.grid(row=0, column=2, rowspan=2, pady=1, padx=10)
lbl2.config(font=labelFont)

#Total Volume Frame
TotalVolumeFrame = tkinter.LabelFrame(MainFrame, text='Total Volume', width=400, height=240, font=frameFont, borderwidth=3, relief='groove')
TotalVolumeFrame.grid(row=0, column=1, padx=10, pady=10)

btn3 = tkinter.Button(TotalVolumeFrame, text="+", width=4, height=1, font=buttonFont, bg='SlateGray3', command=lambda: increment_total_volume(TotalVolume, 1000, 200, 10))
btn3.grid(row=0, column=0, pady=5, padx=10)
btn4 = tkinter.Button(TotalVolumeFrame, text="-", width=4, height=1, font=buttonFont, bg='SlateGray3', command=lambda: decrement_total_volume(TotalVolume, 1000, 200, 10))
btn4.grid(row=1, column=0, pady=10, padx=10)

lbl3 = tkinter.Label(TotalVolumeFrame, textvariable=sTotalVolume, width=7, height=4, bg='SlateGray3')
lbl3.grid(row=0, column=1,rowspan=2, pady=15, padx=10)
lbl3.config(font=labelFont)
lbl4 = tkinter.Label(TotalVolumeFrame, text="ml", width=3, height=3)
lbl4.grid(row=0, column=2, rowspan=2, pady=1, padx=10)
lbl4.config(font=labelFont)

#Respiratory Rate Frame
RespiratoryRateFrame = tkinter.LabelFrame(MainFrame, text='Respiratory Rate', width=400, height=240, font=frameFont, borderwidth=3, relief='groove')
RespiratoryRateFrame.grid(row=1, column=0, padx=10, pady=10)

btn5 = tkinter.Button(RespiratoryRateFrame, text="+", width=4, height=1, font=buttonFont, bg='SlateGray3', command=lambda: increment_respiratory_rate(RespiratoryRate, 30, 12, 1))
btn5.grid(row=0, column=0, pady=5, padx=10)
btn6 = tkinter.Button(RespiratoryRateFrame, text="-", width=4, height=1, font=buttonFont, bg='SlateGray3', command=lambda: decrement_respiratory_rate(RespiratoryRate, 30, 12, 1))
btn6.grid(row=1, column=0, pady=10, padx=10)

lbl5 = tkinter.Label(RespiratoryRateFrame, textvariable=sRespiratoryRate, width=7, height=4, bg='SlateGray3')
lbl5.grid(row=0, column=1,rowspan=2, pady=15, padx=10)
lbl5.config(font=labelFont)
lbl6 = tkinter.Label(RespiratoryRateFrame, text="bpm", width=3, height=3)
lbl6.grid(row=0, column=2, rowspan=2, pady=1, padx=10)
lbl6.config(font=labelFont)

#Inspiratory Rate Frame
InspiratoryRateFrame = tkinter.LabelFrame(MainFrame, text='Inspiratory Rate', width=400, height=240, font=frameFont, borderwidth=3, relief='groove')
InspiratoryRateFrame.grid(row=1, column=1, padx=10, pady=10)

btn7 = tkinter.Button(InspiratoryRateFrame, text="+", width=4, height=1, font=buttonFont, bg='SlateGray3', command=lambda: increment_inspiratory_rate(InspiratoryRate, 2, 0.1,0.1))
btn7.grid(row=0, column=0, pady=5, padx=10)
btn8 = tkinter.Button(InspiratoryRateFrame, text="-", width=4, height=1, font=buttonFont, bg='SlateGray3', command=lambda: decrement_inspiratory_rate(InspiratoryRate, 2, 0.1,0.1))
btn8.grid(row=1, column=0, pady=10, padx=10)

lbl7 = tkinter.Label(InspiratoryRateFrame, textvariable=sInspiratoryRate, width=7, height=4, bg='SlateGray3')
lbl7.grid(row=0, column=1,rowspan=2, pady=15, padx=10)
lbl7.config(font=labelFont)
lbl8 = tkinter.Label(InspiratoryRateFrame, text="s", width=3, height=3)
lbl8.grid(row=0, column=2, rowspan=2, pady=1, padx=10)
lbl8.config(font=labelFont)

root.mainloop()