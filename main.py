from logic import mywindow
from PyQt5 import QtWidgets, QtGui
import sys

app = QtWidgets.QApplication([])
 
application = mywindow()

if 'Breeze' in QtWidgets.QStyleFactory.keys():
    ## Linux case
    app.setStyle('Breeze')
else:
    ## Windows case
    app.setStyle('Fusion')
# icon = QtGui.QIcon()
# icon.addPixmap(QtGui.QPixmap("images/main_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
# app.setWindowIcon(icon)
application.show()
 
sys.exit(app.exec())