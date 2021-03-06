#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 18:23:47 2020

@author: daniel
"""

import GitRepo as grepo
from UserInterface import UserInterface
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import shutil
import os

# will only be needed if the program crashed last time it was ran
if os.path.isdir('./work'):
    shutil.rmtree('./work')

app = QtWidgets.QApplication(sys.argv)
main_window = QtWidgets.QMainWindow()
ui = UserInterface(main_window)
main_window.show()

app.aboutToQuit.connect(ui.cleanup)
sys.exit(app.exec_())


