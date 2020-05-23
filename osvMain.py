from PyQt5 import QtCore, QtGui, QtWidgets
from osvImpl import OSV
from osvGUI import Ui_MainWindow

import sys

# Setup for the QT GUI
app = QtWidgets.QApplication(sys.argv)
ui = Ui_MainWindow()
osv = OSV(ui, app)

# Show the GUI
osv.show()

# Exit when the GUI is closed
sys.exit(app.exec_())
