from threading import Lock
from PyQt5.QtCore import QTimer
from PyQt5 import QtWidgets
from osvGUI import Ui_MainWindow
from zmqTopics import *
from mediacalGraph import MedicalGraph
from enum import Enum

import zmq

import logging
logging.basicConfig(level=logging.INFO)

class OperationMode(Enum):
    VOLUME_CONTROL = 0
    PRESSURE_CONTROL = 1
    PRESSURE_SUPPORTED_CONTROL = 2


class ConstrainedIncrementedSetAndRedDimensionalValue():
    def __init__(self, val=0.0, minimum=-1.0, maximum=1.0, step=0.1, unit=''):
        self.val = val
        self.red_val = None
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.unit = unit

    def incremenet(self):
        self.val = round(min(self.maximum, self.val + self.step), 2)

    def decrement(self):
        self.val = round(max(self.minimum, self.val - self.step), 2)

    def getValue(self):
        return self.val

    def getRedValue(self):
        return self.red_val

    def setRedValue(self, v):
        self.red_val = v

    def getUnit(self):
        return self.unit


class OSV(QtWidgets.QMainWindow):

    def __init__(self, ui: Ui_MainWindow, app: QtWidgets.QApplication):

        self.ZMQ_POLLING_PERIOD = 10  # ms

        super().__init__()
        self.app = app
        self.ui = ui
        self.ui.setupUi(self)

        self._setupZMQIPC()
        self._setupGraph()

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._callbackZMQPolling)
        self.poll_timer.start(self.ZMQ_POLLING_PERIOD)

        self.zmq_poll_lock = Lock()

        self.stoppedBool = True

        self.operation_mode = OperationMode.VOLUME_CONTROL

        self.statusText = "GUI Initializing"
        self.statusColor = (255, 255, 255)
        self._updateStatus()

        self.alarmState = False
        self.ui.pushButtonMuteAlarm.setEnabled(False)

        self.val_tv = ConstrainedIncrementedSetAndRedDimensionalValue(val=500, step=100, maximum=1000, minimum=200,
                                                                      unit='ml')
        self.val_ie = ConstrainedIncrementedSetAndRedDimensionalValue(
            val=0.5, step=0.05, maximum=1.0, minimum=0.1)
        self.val_rr = ConstrainedIncrementedSetAndRedDimensionalValue(val=15, step=1, maximum=20, minimum=10,
                                                                      unit='bpm')
        self.val_do2 = ConstrainedIncrementedSetAndRedDimensionalValue(
            unit='%')
        self.val_peep = ConstrainedIncrementedSetAndRedDimensionalValue(
            unit='cm-H2O')
        self.val_pp = ConstrainedIncrementedSetAndRedDimensionalValue(
            unit='cm-H2O')

        self.vals = [self.val_do2, self.val_ie, self.val_pp,
                     self.val_rr, self.val_tv, self.val_peep]

        self.val_labels = [self.ui.label_DO2, self.ui.label_IE, self.ui.label_PP,
                           self.ui.label_RR, self.ui.label_TV, self.ui.label_PEEP]

        for a in list(zip(self.vals, self.val_labels)):
            r = None
            v = a[0].getValue()
            u = a[0].getUnit()
            a[0].setText(f'{r}/{v} {u}')

        self.ui.pushButton_DO2_Up.clicked.connect(
            lambda: self._incrementValue(self.val_do2, self.ui.label_DO2))
        self.ui.pushButton_IE_Up.clicked.connect(
            lambda: self._incrementValue(self.val_ie, self.ui.label_IE))
        self.ui.pushButton_PP_Up.clicked.connect(
            lambda: self._incrementValue(self.val_pp, self.ui.label_PP))
        self.ui.pushButton_RR_Up.clicked.connect(
            lambda: self._incrementValue(self.val_rr, self.ui.label_RR))
        self.ui.pushButton_TV_Up.clicked.connect(
            lambda: self._incrementValue(self.val_tv, self.ui.label_TV))
        self.ui.pushButton_PEEP_Up.clicked.connect(
            lambda: self._incrementValue(self.val_peep, self.ui.label_PEEP))

        self.ui.pushButton_DO2_Down.clicked.connect(
            lambda: self._decrementValue(self.val_do2, self.ui.label_DO2))
        self.ui.pushButton_IE_Down.clicked.connect(
            lambda: self._decrementValue(self.val_ie, self.ui.label_IE))
        self.ui.pushButton_PP_Down.clicked.connect(
            lambda: self._decrementValue(self.val_pp, self.ui.label_PP))
        self.ui.pushButton_RR_Down.clicked.connect(
            lambda: self._decrementValue(self.val_rr, self.ui.label_RR))
        self.ui.pushButton_TV_Down.clicked.connect(
            lambda: self._decrementValue(self.val_tv, self.ui.label_TV))
        self.ui.pushButton_PEEP_Down.clicked.connect(
            lambda: self._decrementValue(self.val_peep, self.ui.label_PEEP))

        self.ui.pushButtonApply.clicked.connect(self._applyClicked)
        self.ui.pushButtonStart.clicked.connect(self._startStopClicked)
        self.ui.pushButtonMuteAlarm.clicked.connect(self._muteAlarmClicked)
        self.ui.pushButtonQuit.clicked.connect(self._quitClicked)

        ''' TODO Assisted breathing not yet implemented
        self.ui.comboBoxModeSelect.addItems(
            ['Volume Control', 'Pressure Control', 'Assisted Breathing'])
        '''
        self.ui.comboBoxModeSelect.addItems(
            ['Volume Control', 'Pressure Control'])


    def _setupGraph(self):
        self.mg = MedicalGraph(self.graph_data_sub, self.graph_data_poller)
        self.ui.verticalLayoutGraph.addWidget(self.mg)

    def _setupZMQIPC(self):
        '''
        Topics:
            Incomming...
        - data for graph
        - measured values
        - current set values
        - status
        - triggered alarms
            Outgoing...
        - alarm setpoints
        - control setpoints
        - start stop comands
        - mute alarm commands
        - set the mode of control
        '''

        self.ctxt = zmq.Context()

        self.graph_data_sub = self.ctxt.socket(zmq.SUB)
        self.graph_data_sub.bind(ZMQ_GRAPH_DATA_TOPIC)
        self.graph_data_sub.setsockopt_string(zmq.SUBSCRIBE, '')

        self.measured_values_sub = self.ctxt.socket(zmq.SUB)
        self.measured_values_sub.bind(ZMQ_MEASURED_VALUES)
        self.measured_values_sub.setsockopt_string(zmq.SUBSCRIBE, '')

        self.controller_settings_echo_sub = self.ctxt.socket(zmq.SUB)
        self.controller_settings_echo_sub.bind(ZMQ_CONTROLLER_SETTINGS_ECHO)
        self.controller_settings_echo_sub.setsockopt_string(zmq.SUBSCRIBE, '')

        self.osv_status_sub = self.ctxt.socket(zmq.SUB)
        self.osv_status_sub.bind(ZMQ_OSV_STATUS)
        self.osv_status_sub.setsockopt_string(zmq.SUBSCRIBE, '')

        self.triggered_alarms_sub = self.ctxt.socket(zmq.SUB)
        self.triggered_alarms_sub.bind(ZMQ_TRIGGERED_ALARMS)
        self.triggered_alarms_sub.setsockopt_string(zmq.SUBSCRIBE, '')

        self.graph_data_poller = zmq.Poller()
        self.graph_data_poller.register(self.graph_data_sub, zmq.POLLIN)

        self.subscribers_poller = zmq.Poller()
        self.subscribers_poller.register(self.measured_values_sub, zmq.POLLIN)
        self.subscribers_poller.register(
            self.controller_settings_echo_sub, zmq.POLLIN)
        self.subscribers_poller.register(self.osv_status_sub, zmq.POLLIN)
        self.subscribers_poller.register(self.triggered_alarms_sub, zmq.POLLIN)

        self.controller_settings_pub = self.ctxt.socket(zmq.PUB)
        self.controller_settings_pub.connect(ZMQ_CONTROLLER_SETTINGS)

        self.mute_alarms_pub = self.ctxt.socket(zmq.PUB)
        self.mute_alarms_pub.connect(ZMQ_MUTE_ALARMS)

    def _callbackZMQPolling(self):
        socks = dict(self.subscribers_poller.poll(self.ZMQ_POLLING_PERIOD))

        if self.measured_values_sub in socks:
            r = self.measured_values_sub.recv_pyobj()
            with self.zmq_poll_lock:
                o2, peep, peak = r
                self.val_do2.setRedValue(o2)
                self.val_peep.setRedValue(peep)
                self.val_pp.setRedValue(peak)
            self._updateControlGroupBoxValues()

        if self.controller_settings_echo_sub in socks:
            r = self.controller_settings_echo_sub.recv_pyobj()
            with self.zmq_poll_lock:
                stopped, opmode, vtv, vie, vrr, vdo2, vpeep, vpp = r
                self.val_tv.setRedValue(vtv)
                self.val_ie.setRedValue(vie)
                self.val_rr.setRedValue(vrr)
                self.stoppedBool = stopped
            self._updateStartStopButton()
            self._updateControlGroupBoxValues()

        if self.osv_status_sub in socks:
            r = self.osv_status_sub.recv_pyobj()
            with self.zmq_poll_lock:
                self.statusText, self.statusColor = r
            self._updateStatus()

        if self.triggered_alarms_sub in socks:
            r = self.triggered_alarms_sub.recv_pyobj()
            with self.zmq_poll_lock:
                self.alarmState = r
                if self.alarmState:
                    self.ui.pushButtonMuteAlarm.setEnabled(True)
                else:
                    self.ui.pushButtonMuteAlarm.setEnabled(False)

        if len(socks) > 0:
            self.update()

    def _updateStatus(self):
        self.ui.labelStatus.setText(self.statusText)
        colorStr = (
            f"background-color: rgb({self.statusColor[0]},{self.statusColor[1]},{self.statusColor[2]});")
        self.ui.labelStatus.setStyleSheet(colorStr)

    def _updateControlGroupBoxValues(self):
        for a in list(zip(self.vals, self.val_labels)):
            r = a[0].getRedValue()
            v = a[0].getValue()
            u = a[0].getUnit()
            a[0].setText(f'{r}/{v} {u}')

    def _startStopClicked(self):
        with self.zmq_poll_lock:
            if self.stoppedBool:
                vdo2 = self.val_do2.getValue()
                vpeep = self.val_peep.getValue()
                vpp = self.val_pp.getValue()
                vtv = self.val_tv.getValue()
                vie = self.val_ie.getValue()
                vrr = self.val_rr.getValue()
                opmode = self.operation_mode.name

                m = (False, opmode, vtv, vie, vrr, vdo2, vpeep, vpp)
                self.controller_settings_pub.send_pyobj(m)
            else:
                vdo2 = self.val_do2.getValue()
                vpeep = self.val_peep.getValue()
                vpp = self.val_pp.getValue()
                vtv = self.val_tv.getValue()
                vie = self.val_ie.getValue()
                vrr = self.val_rr.getValue()
                opmode = self.operation_mode.name

                m = (True, opmode, vtv, vie, vrr, vdo2, vpeep, vpp)
                self.controller_settings_pub.send_pyobj(m)

    def _updateStartStopButton(self):
        if not self.stoppedBool:
            self.ui.pushButtonStart.setText('STOP')
            self.ui.pushButtonStart.setStyleSheet(
                "background-color: rgb(255, 0, 0);\n")
        else:
            self.ui.pushButtonStart.setText('START')
            self.ui.pushButtonStart.setStyleSheet(
                "background-color: rgb(0, 255, 0);\n")

    def _applyClicked(self):
        with self.zmq_poll_lock:
            vdo2 = self.val_do2.getValue()
            vpeep = self.val_peep.getValue()
            vpp = self.val_pp.getValue()
            vtv = self.val_tv.getValue()
            vie = self.val_ie.getValue()
            vrr = self.val_rr.getValue()
            stopped = self.stoppedBool
            opmode = self.operation_mode.name

            m = (stopped, opmode, vtv, vie, vrr, vdo2, vpeep, vpp)
            self.controller_settings_pub.send_pyobj(m)

    def _muteAlarmClicked(self):
        self.mute_alarms_pub.send_pyobj(True)

    def _quitClicked(self):
        self.app.quit()

    def _incrementValue(self, val: ConstrainedIncrementedSetAndRedDimensionalValue, label: QtWidgets.QLabel):
        with self.zmq_poll_lock:
            # 1) increment internal value
            val.incremenet()
            # 2) change the label
            r = val.getRedValue()
            v = val.getValue()
            u = val.getUnit()
            label.setText(f'{r}/{v} {u}')

    def _decrementValue(self, val: ConstrainedIncrementedSetAndRedDimensionalValue, label: QtWidgets.QLabel):
        with self.zmq_poll_lock:
            # 1) decrement internal value
            val.decrement()
            # 2) change the label
            r = val.getRedValue()
            v = val.getValue()
            u = val.getUnit()
            label.setText(f'{r}/{v} {u}')
