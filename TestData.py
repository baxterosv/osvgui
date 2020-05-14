
import zmq
import random
import time

ZMQ_MEASUREMENT_TOPIC = "ipc:///tmp/vol_data.pipe"

def main():
	
	ctxt = zmq.Context()
	voldatapub = ctxt.socket(zmq.PUB)
	voldatapub.connect(ZMQ_MEASUREMENT_TOPIC)

	while True:

		pressure = random.random() * 1.25
		volume = random.random() * 1000

		testData = (pressure, volume)
		voldatapub.send_pyobj(testData)

		time.sleep(0.1)


if __name__ == '__main__':
    main()