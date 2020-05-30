
import zmq
from math import sin
import time
import signal

ZMQ_MEASUREMENT_TOPIC = "ipc:///tmp/graph_data.pipe"

ctxt = zmq.Context()
voldatapub = ctxt.socket(zmq.PUB)
voldatapub.connect(ZMQ_MEASUREMENT_TOPIC)

def sigint_handler(sig, frame):
	print('\r' + ' '*20)
	exit()

signal.signal(signal.SIGINT, sigint_handler)

def main():
	while True:
		t = time.time()
		pressure = 3 * sin(1.5 * t)
		volume = 10 * sin(1.0 * t)

		testData = (t, pressure, volume)
		voldatapub.send_pyobj(testData)
		print(testData)
		time.sleep(0.05)

if __name__ == '__main__':
    main()