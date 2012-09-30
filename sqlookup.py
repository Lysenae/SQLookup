#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import gui as Gui
from PySide import QtGui

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    wnd = Gui.SQLookup()
    sys.exit(app.exec_())
