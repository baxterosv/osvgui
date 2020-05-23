from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import zmq

from threading import Lock


class MedicalGraph(FigureCanvas):

    def __init__(self, data_subscriber, data_poller, domain=10.0, fps=30):

        # TODO Make the figure size configurable or automatic
        f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

        ax1.set_ylabel('Volume')
        ax2.set_ylabel('Pressure')
        ax2.set_xlabel('Time (s)')

        ax1.set_xlim(0, domain)
        ax2.set_xlim(0, domain)

        ax1.set_ylim(-4, 4)
        ax2.set_ylim(-12, 12)

        self.vl1 = ax1.axvline(x=0, color='k', linestyle='--')
        self.vl2 = ax2.axvline(x=0, color='k', linestyle='--')

        self.line1, = ax1.plot([], [])
        self.line2, = ax2.plot([], [])

        self.domain = domain
        self.fps = fps

        # The data stored in the graph
        self.data = []

        self.data_subscriber = data_subscriber
        self.data_subscriber_poller = data_poller

        self.initial_time = None
        self.most_recent_relative_time = None

        self.plot_data_lock = Lock()

        self._timer = self.new_timer(
            10, [(self._callbackPollZMQ, (), {})])

        super().__init__(f)
        interval = 1000/self.fps
        animation.FuncAnimation(f, lambda i: self._callbackAnimateGraph(), interval=interval, blit=True) 

        self._timer.start()

    def _callbackPollZMQ(self):
        socks = dict(self.data_subscriber_poller.poll(10))
        if self.data_subscriber in socks:
            v = self.data_subscriber.recv_pyobj()

            if self.initial_time == None:
                self.initial_time = v[0]

            self.most_recent_relative_time = v[0] - self.initial_time

            with self.plot_data_lock:
                rt = v[0] - self.initial_time
                modrt = rt % self.domain
                a = (rt, modrt, v[1], v[2])
                # This should check for when we wrap around and insert a blank
                self.data.append(a)
                try:
                    if (modrt - self.data[-2][1]) < 0:
                        an = (self.most_recent_relative_time, None, None, None)
                        self.data.insert(-1, an)
                except IndexError:
                    #print('Failed to check rollover None')
                    pass
                except TypeError:
                    #print('Tried to subtrack none')
                    pass

        # List maintinance
        # 1) Remove all entries older than domain
        # NOTE Might want to use filterfalse() ?
        with self.plot_data_lock:
            self.data[:] = [
                x for x in self.data if self.most_recent_relative_time - x[0] < self.domain]

    def _callbackAnimateGraph(self):
        with self.plot_data_lock:
            t = [x[1] for x in self.data]
            v1 = [x[2] for x in self.data]
            v2 = [x[3] for x in self.data]
        try:
            self.vl1.set_xdata(t[-1])
            self.vl2.set_xdata(t[-1])
        except IndexError:
            pass

        self.line1.set_xdata(t)
        self.line2.set_xdata(t)
        self.line1.set_ydata(v1)
        self.line2.set_ydata(v2)

        return self.vl1, self.vl2, self.line1, self.line2