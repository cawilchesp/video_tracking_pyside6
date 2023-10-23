from PySide6 import QtWidgets, QtGui
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import cv2






def about_qt_dialog(parent, language:int):
    title = ''
    if language == 0:
        title = 'Acerca de Qt...'
    elif language == 1:
        title = 'About Qt...'

    QtWidgets.QMessageBox.aboutQt(parent, title)