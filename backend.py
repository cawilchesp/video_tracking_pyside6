from PyQt6 import QtWidgets, QtGui
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import cv2

style_colors = {
    'azul_gris': '59,66,83',
    'azul_negro': '46,52,65',
    'azul': '128,160,194',
    'amarillo': '237,204,135',
    'rojo': '193,96,105',
    'verde': '162,191,138',
    'blanco': '229,233,240',
    'gris': '178,178,178',
    'negro': '0,0,0'
}

def convert_cv_qt(cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(1280, 720, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)

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
        'first_frame': frame
    }

    cap.release()

    return video_properties

def about_dialog(style: int, language:int):
    message = ''
    title = ''
    if language == 0:
        title = 'Acerca de...'
        message = (
            """
            VIDEO ANNOTATOR V1.0
            \n
            Desarrollado por:
            \n
            CARLOS ANDRÉS WILCHES PÉREZ
            INGENIERO ELECTRÓNICO, BSc. MSc. PhD.
            Contacto: c.wilches@javeriana.edu.co
            \n
            PONTIFICIA UNIVERSIDAD JAVERIANA
            FACULTAD DE INGENIERÍA
            DEPARTAMENTO DE INGENIERÍA ELECTRÓNICA
            \n
            2022
            """
        )
    elif language == 1:
        title = 'About...'
        message = (
            """
            VIDEO ANNOTATOR V1.0
            \n
            Developed by:
            \n
            CARLOS ANDRÉS WILCHES PÉREZ
            ELECTRONIC ENGINEER, BSc. MSc. PhD.
            Contact: c.wilches@javeriana.edu.co
            \n
            PONTIFICIA UNIVERSIDAD JAVERIANA
            FACULTY OF ENGINEERING
            DEPARTAMENT OF ELECTRONIC ENGINEERING
            \n
            2022
            """
        )

    about_style = ''
    if style == 0:
        about_style = (f'background-color: rgb({style_colors["azul_gris"]});'
                       f'color: rgb({style_colors["blanco"]});')
    elif style == 1:
        about_style = (f'background-color: rgb({style_colors["blanco"]});'
                       f'color: rgb({style_colors["negro"]});')
    
    # Mensaje
    about = QtWidgets.QMessageBox()
    about.setWindowTitle(title)
    about.setText(message)
    about.setStyleSheet(about_style)
    about.exec()

def about_qt_dialog(parent, language:int):
    title = ''
    if language == 0:
        title = 'Acerca de Qt...'
    elif language == 1:
        title = 'About Qt...'

    QtWidgets.QMessageBox.aboutQt(parent, title)