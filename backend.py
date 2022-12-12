from PyQt6 import QtWidgets, QtGui
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import cv2


def convert_cv_qt(cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        # p = convert_to_Qt_format.scaled(1280, 720, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(convert_to_Qt_format)


def open_video(source_file: str):
    cap = cv2.VideoCapture(source_file)
    if not cap.isOpened():
        print('Error opening video stream or file')
        return 0

    ret, frame = cap.read()

    video_properties = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'fps': float(cap.get(cv2.CAP_PROP_FPS)),
        'first_frame': convert_cv_qt(frame)
    }

    cap.release()

    return video_properties


def about_qt_dialog(parent, language:int):
    title = ''
    if language == 0:
        title = 'Acerca de Qt...'
    elif language == 1:
        title = 'About Qt...'

    QtWidgets.QMessageBox.aboutQt(parent, title)