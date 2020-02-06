#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 18:23:47 2020

@author: daniel
"""

import GitRepo as grepo
from guiObjects import *
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import shutil


def cleanup(ui):
    work_dir = ui.user_input_dir
    if work_dir == './work':
        shutil.rmtree(work_dir)


app = QtWidgets.QApplication(sys.argv)
main_window = QtWidgets.QMainWindow()
ui = Ui_CodeAnalysisTool()
ui.setupUi(main_window)
main_window.show()

app.aboutToQuit.connect(lambda : cleanup(ui))
sys.exit(app.exec_())


