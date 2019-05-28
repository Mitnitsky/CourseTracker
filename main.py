from logic import mywindow
from PyQt5 import QtWidgets, QtGui
import sys
import json

def createSettingsFile():
    with open("settings.json", "w") as write_file:
        data = {'user_name': '', 'dimensions': [{'width': 1320, 'height': 565}]}
        json.dump(data, write_file, indent=4)


def checkSettingsFile():
    try:
        read_write_file = open("settings.json", "r+")
        if read_write_file:
            data = json.load(read_write_file)
            if 'user_name' not in data.keys():
                data['user_name'] = ''
            if 'dimensions' not in data.keys():
                data['dimensions'] = [{'width': 1320, 'height': 565}]
            read_write_file.seek(0)
            json.dump(data, read_write_file, indent=4)
            read_write_file.truncate()
        else:
            createSettingsFile()
    except (FileNotFoundError, KeyError, json.decoder.JSONDecodeError):
        createSettingsFile()

if __name__ == "__main__":
    checkSettingsFile()
    app = QtWidgets.QApplication([])
    application = mywindow()
    app.setQuitOnLastWindowClosed(True)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("images/main_icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    app.setWindowIcon(icon)
    application.setWindowIcon(icon)
    if 'Breeze' in QtWidgets.QStyleFactory.keys():
        ## Linux case
        app.setStyle('Breeze')
    else:
        ## Windows case
        app.setStyle('Fusion')
    application.show()
    exit(app.exec_())
