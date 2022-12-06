from PyQt6 import QtGui, QtWidgets, QtCore
from PyQt6.QtWidgets import QWidget, QApplication, QStyle
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QSettings

import sys
import pathlib
import psycopg2
import cv2
import numpy as np

import widgets
import backend
# from object_tracker import detect



# import torch
# import torch.backends.cudnn as cudnn

# from utils.datasets import LoadStreams, LoadImages
# from utils.general import non_max_suppression, scale_coords
# from utils.torch_utils import select_device, time_synchronized

# from models.models import *
# from utils.datasets import *
# from utils.general import *

# from deep_sort_pytorch.utils.parser import get_config
# from deep_sort_pytorch.deep_sort import DeepSort
# from collections import deque





# --------
# Settings
# --------
settings = QSettings(f'{sys.path[0]}/settings.ini', QSettings.Format.IniFormat)
language_value = int(settings.value('language'))
theme_value = int(settings.value('theme'))
color_value = settings.value('color')

idioma_dict = {0: ('Español', 'Spanish'), 1: ('Inglés', 'English')}
tema_dict = {0: ('Oscuro', 'Dark'), 1: ('Claro', 'Light')}
main_style_dict = {
    0: 'background-color: rgb(59,66,83); color: rgb(255,255,255)',
    1: 'background-color: rgb(229,233,240); color: rgb(0,0,0)'
}

palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)

data_deque = {}


# # -------------
# # Base de Datos
# # -------------
# connection = psycopg2.connect(user='postgres',
#                               password='ecf406Carolina',
#                               host='localhost',
#                               port='5432',
#                               database='video_annotator')
# cursor = connection.cursor()

# cursor.execute("""CREATE TABLE IF NOT EXISTS videos (
#                 id serial PRIMARY KEY,
#                 name VARCHAR(128) NOT NULL,
#                 path VARCHAR(128) UNIQUE NOT NULL,
#                 width INT NOT NULL,
#                 height INT NOT NULL,
#                 frame_count INT NOT NULL,
#                 fps FLOAT NOT NULL,
#                 is_calibrated BOOLEAN NOT NULL,
#                 matrix VARCHAR(128) NOT NULL
#                 )""")
# connection.commit()

# cursor.execute('SELECT * FROM videos')
# recent_videos = cursor.fetchall()
# connection.close()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Video Tracker')
        self.setGeometry(100, 100, 1700, 830)
        self.setMinimumSize(1700, 830)
        self.setMaximumSize(1700, 830)
        self.setStyleSheet(main_style_dict[theme_value])
        
        # ------------
        # Sidebar Left
        # ------------
        self.sidebar_left = widgets.Sidebar(self, 'sidebar_left', (0, 0, 200, 830), theme_value)
        
        # Menú Archivo
        y_sidebar_left = 10
        self.archivo_label = widgets.TitleLabel(self.sidebar_left, 'archivo_label', ('Origen del Video', 'Video Source'), (10, y_sidebar_left, 180), theme_value, language_value)

        y_sidebar_left += 40
        self.webcam_button = widgets.TextButton(self.sidebar_left, 'webcam_button', ('Cámara Web', 'Webcam'), (10, y_sidebar_left, 180), 'SP_DialogOpenButton', theme_value, language_value)
        self.webcam_button.clicked.connect(self.on_webcam_button_clicked)

        y_sidebar_left += 40
        self.ip_camera_button = widgets.TextButton(self.sidebar_left, 'ip_camera_button', ('Cámara IP', 'IP Camera'), (10, y_sidebar_left, 180), 'SP_DialogOpenButton', theme_value, language_value)
        self.ip_camera_button.clicked.connect(self.on_ip_camera_button_clicked)

        y_sidebar_left += 40
        self.video_button = widgets.TextButton(self.sidebar_left, 'video_button', ('Archivo de Video', 'Video File'), (10, y_sidebar_left, 180), 'SP_DialogOpenButton', theme_value, language_value)
        self.video_button.clicked.connect(self.on_video_button_clicked)
        
        y_sidebar_left += 40
        self.line1 = widgets.lineSeparator(self.sidebar_left, 10, y_sidebar_left, 180, theme_value)
        
        # Menú Información del Video
        y_sidebar_left += 10
        self.informacion_label = widgets.TitleLabel(self.sidebar_left, 'informacion_label', ('Información del Video', 'Video Information'), (10, y_sidebar_left, 180), theme_value, language_value)
        
        y_sidebar_left += 40
        self.ancho_label = widgets.ItemLabel(self.sidebar_left, 'ancho_label', ('Ancho', 'Width'), (10, y_sidebar_left, 90), theme_value, language_value)
        
        self.anchoValue_label = widgets.ItemLabel(self.sidebar_left, 'anchoValue_label', ('', ''), (100, y_sidebar_left, 90), theme_value, language_value)
        
        y_sidebar_left += 40
        self.alto_label = widgets.ItemLabel(self.sidebar_left, 'alto_label', ('Alto', 'Height'), (10, y_sidebar_left, 90), theme_value, language_value)
        
        self.altoValue_label = widgets.ItemLabel(self.sidebar_left, 'altoValue_label', ('', ''), (100, y_sidebar_left, 90), theme_value, language_value)

        y_sidebar_left += 40
        self.fps_label = widgets.ItemLabel(self.sidebar_left, 'fps_label', ('FPS', 'FPS'), (10, y_sidebar_left, 90), theme_value, language_value)
        
        self.fpsValue_label = widgets.ItemLabel(self.sidebar_left, 'fpsValue_label', ('', ''), (100, y_sidebar_left, 90), theme_value, language_value)

        y_sidebar_left += 40
        self.line2 = widgets.lineSeparator(self.sidebar_left, 10, y_sidebar_left, 180, theme_value)

        # Menú Calibración
        y_sidebar_left += 40
        self.calibracion_button = widgets.TextButton(self.sidebar_left, 'calibracion_button', ('Calibrar', 'Calibrate'), (10, y_sidebar_left, 150, ), 'SP_FileDialogListView', theme_value, language_value)
        
        self.calibracionStatusLabel = widgets.IconLabel(self.sidebar_left, 'calibracionStatusLabel', (160, y_sidebar_left, 30, 30), 'SP_DialogCancelButton')
        
        y_sidebar_left += 40
        self.line3 = widgets.lineSeparator(self.sidebar_left, 10, y_sidebar_left, 180, theme_value)
        
        

        # -------------
        # Sidebar Right
        # -------------
        self.sidebar_right = widgets.Sidebar(self, 'sidebar_right', (1500, 0, 200, 830), theme_value)

        # Menú Anotaciones
        y_sidebar_right = 10
        self.anotacion_label = widgets.TitleLabel(self.sidebar_right, 'anotacion_label', ('Anotaciones', 'Annotations'), (10, y_sidebar_right, 180), theme_value, language_value)
        
        y_sidebar_right += 30
        self.clases_label = widgets.ItemLabel(self.sidebar_right, 'clases_label', ('Clases', 'Classes'), (10, y_sidebar_right, 180), theme_value, language_value)
        
        y_sidebar_right += 40
        self.clases_combobox = widgets.ListComboBox(self.sidebar_right, 'clases_combobox', (10, y_sidebar_right, 180), 2, 2, theme_value)
        
        y_sidebar_right += 40
        self.color_button = widgets.ColorButton(self.sidebar_right, 'color_button', ('Color', 'Colour'), (10, y_sidebar_right, 180), 'images/color.png', color_value, theme_value, language_value)
        self.color_button.clicked.connect(self.on_color_button_clicked)

        y_sidebar_right += 40
        self.line4 = widgets.lineSeparator(self.sidebar_right, 10, y_sidebar_right, 180, theme_value)
        
        # Menú Configuración
        y_sidebar_right += 10
        self.configuracion_label = widgets.TitleLabel(self.sidebar_right, 'configuracion_label', ('Configuración', 'Settings'), (10, y_sidebar_right, 180), theme_value, language_value)
        
        y_sidebar_right += 30
        self.idioma_label = widgets.ItemLabel(self.sidebar_right, 'idioma_label', ('Idioma', 'Language'), (10, y_sidebar_right, 180), theme_value, language_value)
        
        y_sidebar_right += 40
        self.idioma_combobox = widgets.StaticComboBox(self.sidebar_right, 'idioma_combobox', (10, y_sidebar_right, 180), 2, idioma_dict, theme_value, language_value)
        self.idioma_combobox.currentIndexChanged.connect(self.on_idioma_combobox_currentIndexChanged)
        
        y_sidebar_right += 40
        self.tema_label = widgets.ItemLabel(self.sidebar_right, 'tema_label', ('Tema', 'Theme'), (10, y_sidebar_right, 180), theme_value, language_value)
        
        y_sidebar_right += 40
        self.tema_combobox = widgets.StaticComboBox(self.sidebar_right, 'tema_combobox', (10, y_sidebar_right, 180), 2, tema_dict, theme_value, language_value)
        self.tema_combobox.currentIndexChanged.connect(self.on_tema_combobox_currentIndexChanged)
        
        y_sidebar_right += 40
        self.line5 = widgets.lineSeparator(self.sidebar_right, 10, y_sidebar_right, 180, theme_value)

        # Menú Ayuda
        y_sidebar_right += 10
        self.help_label = widgets.TitleLabel(self.sidebar_right, 'help_label', ('Ayuda', 'Help'), (10, y_sidebar_right, 180), theme_value, language_value)
        
        y_sidebar_right += 40
        self.manual_button = widgets.TextButton(self.sidebar_right, 'manual_button', ('Manual', 'Manual'), (10, y_sidebar_right, 180), 'SP_TitleBarContextHelpButton', theme_value, language_value)
        self.manual_button.clicked.connect(self.on_manual_button_clicked)

        y_sidebar_right += 40
        self.about_button = widgets.TextButton(self.sidebar_right, 'about_button', ('Acerca de...', 'About...'), (10, y_sidebar_right, 180), 'SP_CommandLink', theme_value, language_value)
        self.about_button.clicked.connect(self.on_about_button_clicked)

        y_sidebar_right += 40
        self.aboutQt_button = widgets.TextButton(self.sidebar_right, 'aboutQt_button', ('Acerca de Qt...', 'About Qt...'), (10, y_sidebar_right, 180), 'SP_TitleBarMenuButton', theme_value, language_value)
        self.aboutQt_button.clicked.connect(self.on_aboutQt_button_clicked)
        

        
        # --------
        # Upperbar
        # --------
        self.upperbar = widgets.Sidebar(self, 'upperbar', (200, 0, 1300, 50), theme_value)
        
        x_upperbar = 10
        self.slow_button = widgets.IconButton(self.upperbar, 'slow_button', (x_upperbar, 10), 'images/slow_play.png', theme_value)
        
        x_upperbar += 40
        self.backFrame_button = widgets.IconButton(self.upperbar, 'backFrame_button', (x_upperbar, 10), 'images/back_frame.png', theme_value)
        
        x_upperbar += 40
        self.backPlay_button = widgets.IconButton(self.upperbar, 'backPlay_button', (x_upperbar, 10), 'images/back_play.png', theme_value)
        
        x_upperbar += 40
        self.pause_button = widgets.IconButton(self.upperbar, 'pause_button', (x_upperbar, 10), 'images/pause.png', theme_value)
        
        x_upperbar += 40
        self.play_button = widgets.IconButton(self.upperbar, 'play_button', (x_upperbar, 10), 'images/play.png', theme_value)
        
        x_upperbar += 40
        self.frontFrame_button = widgets.IconButton(self.upperbar, 'frontFrame_button', (x_upperbar, 10), 'images/front_frame.png', theme_value)
        
        x_upperbar += 40
        self.fastPlay_button = widgets.IconButton(self.upperbar, 'fastPlay_button', (x_upperbar, 10), 'images/fast_play.png', theme_value)
        
        x_upperbar += 40
        self.video_slider = widgets.ObjectSlider(self.upperbar, 'video_slider', (x_upperbar, 10, 580), theme_value)
        self.video_slider.sliderMoved.connect(self.on_video_slider_sliderMoved)
        self.video_slider.sliderReleased.connect(self.on_video_slider_sliderReleased)
        
        x_upperbar += 590
        self.frameNumber_edit = widgets.ObjectLineEdit(self.upperbar, 'frameNumber_edit', (x_upperbar, 10, 100), theme_value)
        
        # -----------
        # Main Window
        # -----------
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setGeometry(QtCore.QRect(210, 60, 1280, 720))
        self.video_label.setFrameStyle(QtWidgets.QFrame.Shape.Box)
        
    # ----------------------
    # Funciones de Controles
    # ----------------------
    # Menú Archivo
    def on_webcam_button_clicked(self):
        self.detect('0', 'D:/SIER/Datasets/Bogota_ETB/Resultados/source_1_YOLOR_DS', 576, '0', True, 32)
        return 0


    def on_ip_camera_button_clicked(self):

        return 0


    def on_video_button_clicked(self):

        return 0


    def on_abrir_button_clicked(self):
        global recent_videos

        connection = psycopg2.connect(user='postgres',
                              password='ecf406Carolina',
                              host='localhost',
                              port='5432',
                              database='video_annotator')
        cursor = connection.cursor()

        last_folder = settings.value('video_folder')
        selected_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Seleccione el archivo de video', last_folder,
                                                              'Archivos de Video (*.avi *.mp4 *.mpg *.m4v *.mkv)')
        if selected_file[0]:
            file_path = pathlib.Path(selected_file[0])
            video_path = str(file_path.resolve())
            video_name = str(file_path.name)

            settings.setValue('video_folder', str(file_path.parent))

            cursor.execute(f"SELECT * FROM videos WHERE path='{video_path}'")
            data = cursor.fetchall()

            if not data:
                video_properties = backend.open_video(video_path)

                width = video_properties['width']
                height = video_properties['height']
                frame_count = video_properties['frame_count']
                fps = video_properties['fps']
                is_calibrated = False
                matrix = ''

                insert_query = f"""INSERT INTO videos (name, path, width, height, frame_count, fps, is_calibrated, matrix) 
                                VALUES ('{video_name[:-4]}', '{video_path}', '{width}', '{height}', '{frame_count}', '{fps}', '{is_calibrated}', '{matrix}')"""
                cursor.execute(insert_query)
                connection.commit()
                cursor.execute('SELECT * FROM videos')
                recent_videos = cursor.fetchall()

                self.recientes_combobox.clear()
                for data in recent_videos:
                    self.recientes_combobox.addItem(data[1])
                self.recientes_combobox.setCurrentIndex(self.recientes_combobox.count() - 1)

                self.anchoValue_label.setText(f'{width}')
                self.altoValue_label.setText(f'{height}')
                self.video_slider.setMaximum(frame_count)

                cv_img = video_properties['first_frame']
                qt_img = backend.convert_cv_qt(cv_img)
                self.video_label.setPixmap(qt_img)
            else:
                error_message = QtWidgets.QMessageBox.critical(self, 'Error de Video', 'El video ya se encuentra en la base de datos')


    def on_eliminar_button_clicked(self):
        global recent_videos

        connection = psycopg2.connect(user='postgres',
                              password='ecf406Carolina',
                              host='localhost',
                              port='5432',
                              database='video_annotator')
        cursor = connection.cursor()
        
        video_name = self.recientes_combobox.currentText()
        if video_name != '':
            delete_query = f"DELETE FROM videos WHERE name='{video_name}'"
            cursor.execute(delete_query)
            connection.commit()
            cursor.execute('SELECT * FROM videos')
            recent_videos = cursor.fetchall()

            self.recientes_combobox.clear()
            for data in recent_videos:
                self.recientes_combobox.addItem(data[1])
            self.recientes_combobox.setCurrentIndex(-1)

            self.anchoValue_label.setText('')
            self.altoValue_label.setText('')
            self.video_label.clear()
            
            connection.close()

            success_message = QtWidgets.QMessageBox.information(self, 'Datos Guardados', 'Video eliminado de la base de datos')
        else:
            error_message = QtWidgets.QMessageBox.critical(self, 'Error de Video', 'No se seleccionó ningún video')


    def on_idioma_combobox_currentIndexChanged(self, index: int):
        self.archivo_label.language_text(index)
        self.configuracion_label.language_text(index)
        self.idioma_label.language_text(index)
        self.idioma_combobox.language_text(index)
        self.tema_label.language_text(index)
        self.tema_combobox.language_text(index)
        self.informacion_label.language_text(index)
        self.ancho_label.language_text(index)
        self.alto_label.language_text(index)
        self.calibracion_button.language_text(index)
        self.help_label.language_text(index)
        self.about_button.language_text(index)
        self.aboutQt_button.language_text(index)
        self.anotacion_label.language_text(index)
        self.clases_label.language_text(index)
        self.color_button.language_text(index)
        

        settings.setValue('language', str(index))

    def on_tema_combobox_currentIndexChanged(self, index: int):
        self.setStyleSheet(main_style_dict[index])
        self.sidebar_left.style_sheet(index)
        self.archivo_label.style_sheet(index)
        self.line1.style_sheet(index)
        self.configuracion_label.style_sheet(index)
        self.idioma_label.style_sheet(index)
        self.idioma_combobox.style_sheet(index)
        self.tema_label.style_sheet(index)
        self.tema_combobox.style_sheet(index)
        self.line2.style_sheet(index)
        self.informacion_label.style_sheet(index)
        self.ancho_label.style_sheet(index)
        self.anchoValue_label.style_sheet(index)
        self.alto_label.style_sheet(index)
        self.altoValue_label.style_sheet(index)
        self.calibracion_button.style_sheet(index)
        self.line3.style_sheet(index)
        self.help_label.style_sheet(index)
        self.manual_button.style_sheet(index)
        self.about_button.style_sheet(index)
        self.aboutQt_button.style_sheet(index)
        self.sidebar_right.style_sheet(index)
        self.anotacion_label.style_sheet(index)
        self.clases_label.style_sheet(index)
        self.clases_combobox.style_sheet(index)
        self.color_button.style_sheet(index, settings.value('color'))
        self.line4.style_sheet(index)
        
        self.line5.style_sheet(index)
        
        self.upperbar.style_sheet(index)
        self.slow_button.style_sheet(index)
        self.backFrame_button.style_sheet(index)
        self.backPlay_button.style_sheet(index)
        self.pause_button.style_sheet(index)
        self.play_button.style_sheet(index)
        self.frontFrame_button.style_sheet(index)
        self.fastPlay_button.style_sheet(index)
        self.frameNumber_edit.style_sheet(index)

        settings.setValue('theme', str(index))


    # Menú Ayuda
    def on_manual_button_clicked(self):
        # HelpWindow helpVideoApp
        # helpVideoApp.exec()
        return 0
        

    def on_about_button_clicked(self):
        backend.about_dialog(int(settings.value('theme')), int(settings.value('language')))


    def on_aboutQt_button_clicked(self):
        backend.about_qt_dialog(self, int(settings.value('language')))


    def on_color_button_clicked(self):
        selected_color = QtWidgets.QColorDialog.getColor()
        color = f'{selected_color.red()}, {selected_color.green()}, {selected_color.blue()}'
        self.color_button.style_sheet(theme_value, color)
        settings.setValue('color', color)
        

    # Barra de Video
    def on_video_slider_sliderMoved(self):
        self.frameNumber_edit.setText(str(self.video_slider.value()))


    def on_video_slider_sliderReleased(self):
        # backend.set_PTZ(self.pan_edit.text(), self.tilt_edit.text(), self.zoom_edit.text(), 
        #                 self.ipaddress_combobox.currentText(), self.user_edit.text(), 
        #                 self.password_edit.text())
        return 0
    
           

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
        if self.record_button.isChecked():
            self.thread.output.write(cv_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(1280, 720, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)


    # --------------------------------------------------------------------------
    #                                   YOLOR
    # --------------------------------------------------------------------------

    def xyxy_to_xywh(self, *xyxy):
        """" Calculates the relative bounding box from absolute pixel values. """
        bbox_left = min([xyxy[0].item(), xyxy[2].item()])
        bbox_top = min([xyxy[1].item(), xyxy[3].item()])
        bbox_w = abs(xyxy[0].item() - xyxy[2].item())
        bbox_h = abs(xyxy[1].item() - xyxy[3].item())
        x_c = (bbox_left + bbox_w / 2)
        y_c = (bbox_top + bbox_h / 2)
        w = bbox_w
        h = bbox_h

        return x_c, y_c, w, h


    def xyxy_to_tlwh(self, bbox_xyxy):
        tlwh_bboxs = []
        for i, box in enumerate(bbox_xyxy):
            x1, y1, x2, y2 = [int(i) for i in box]
            top = x1
            left = y1
            w = int(x2 - x1)
            h = int(y2 - y1)
            tlwh_obj = [top, left, w, h]
            tlwh_bboxs.append(tlwh_obj)

        return tlwh_bboxs


    def compute_color(self, label: str) -> tuple:
        """
        Simple function that adds fixed color depending on the class
        """
        if label == 0: #person  #BGR
            color = (85, 45, 255)
        elif label == 1: #bicycle
            color = (7, 127, 15)
        elif label == 2: # Car
            color = (255, 149, 0)
        elif label == 3:  # Motobike
            color = (0, 204, 255)
        elif label == 5:  # Bus
            color = (0, 149, 255)
        elif label == 7:  # truck
            color = (222, 82, 175)
        # else:
        #     color = [int((p * (label ** 2 - label + 1)) % 255) for p in palette]
        return color


    # def draw_trajectories(self, img: np.array, bbox: np.array, object_id: np.array,
    #                 identities: np.array, trailslen: int) -> None:
    #     # Remove tracked point from buffer if object is lost
    #     for key in list(data_deque):
    #         if key not in identities:
    #             data_deque.pop(key)

    #     for i, box in enumerate(bbox):
    #         x1, y1, x2, y2 = [int(i) for i in box]
    #         center = (int((x2+x1)/2), int((y2+y1)/2))
    #         id = int(identities[i]) if identities is not None else 0
    #         if id not in data_deque:
    #             data_deque[id] = deque(maxlen=trailslen)
    #         color = self.compute_color(object_id[i])
    #         data_deque[id].appendleft(center)
    
    #         # Draw trajectory
    #         for i in range(1, len(data_deque[id])):
    #             if data_deque[id][i-1] is None or data_deque[id][i] is None:
    #                 continue

    #             # thickness = int(np.sqrt(opt.trailslen/float(i+i))*1.5)
    #             cv2.line(img, data_deque[id][i-1], data_deque[id][i], color, 2)


    # def draw_boxes(self, img: np.array, bbox: np.array, object_id: np.array,
    #                 identities: np.array) -> None:
    #     for i, box in enumerate(bbox):
    #         x1, y1, x2, y2 = [int(i) for i in box]
    #         id = int(identities[i]) if identities is not None else 0
    #         color = self.compute_color(object_id[i])
    #         label = f'{names[object_id[i]]} {id}'

    #         # Draw box
    #         cv2.rectangle(img, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

    #         # Draw labels
    #         t_size = cv2.getTextSize(label, 0, 2/3, 1)[0]
    #         cv2.rectangle(img, (x1, y1-t_size[1]-3), (x1 + t_size[0], y1+3), color, -1, cv2.LINE_AA)
    #         cv2.putText(img, label, (x1, y1 - 2), 0, 2/3, [225, 255, 255], 1, cv2.LINE_AA)


    # def save_objects(self, bbox: np.array, object_id: np.array, identities: np.array, 
    #                     txt_path: str, frame_num: int) -> None:
    #     for i, box in enumerate(bbox):
    #         x1, y1, x2, y2 = [int(i) for i in box]

    #         id = int(identities[i]) if identities is not None else 0
    #         with open(txt_path + '.txt', 'a') as f:
    #             f.write(f'{frame_num},{id},{str(names[object_id[i]])},{x1},{y1},{x2-x1},{y2-y1},0,\n')


    def load_classes(self, path):
        # Loads *.names file at 'path'
        with open(path, 'r') as f:
            names = f.read().split('\n')
        return list(filter(None, names))  # filter removes empty strings (such as last line)


    # def main(self, source, out, imgsz, device, view_img, trailslen):
    #     global names
    #     names = self.load_classes('data/coco.names')
    #     save_img = False

    #     # sources
    #     webcam = source == '0' or source.startswith('rtsp') or source.startswith('http') or source.endswith('.txt')

    #     # initialize deepsort
    #     cfg_deep = get_config()
    #     cfg_deep.merge_from_file("deep_sort_pytorch/configs/deep_sort.yaml")
    #     deepsort = DeepSort(cfg_deep.DEEPSORT.REID_CKPT,
    #                         max_dist=cfg_deep.DEEPSORT.MAX_DIST, min_confidence=cfg_deep.DEEPSORT.MIN_CONFIDENCE,
    #                         nms_max_overlap=cfg_deep.DEEPSORT.NMS_MAX_OVERLAP, max_iou_distance=cfg_deep.DEEPSORT.MAX_IOU_DISTANCE,
    #                         max_age=cfg_deep.DEEPSORT.MAX_AGE, n_init=cfg_deep.DEEPSORT.N_INIT, nn_budget=cfg_deep.DEEPSORT.NN_BUDGET,
    #                         use_cuda=True)

    #     # Initialize
    #     device = select_device(device) 
    #     half = device.type != 'cpu'  # half precision only supported on CUDA

    #     # Load model
    #     cfg = 'cfg/yolor_p6.cfg'
    #     weights = 'cfg/yolor_p6.pt'
    #     model = Darknet(cfg, imgsz).cuda()
    #     model.load_state_dict(torch.load(weights, map_location=device)['model'])
    #     model.to(device).eval()
    #     if half:
    #         model.half()  # to FP16

    #     # Set Dataloader
    #     vid_path, vid_writer = None, None
    #     if webcam:
    #         view_img = True
    #         # cudnn.benchmark = True  # set True to speed up constant image size inference
    #         dataset = LoadStreams(source, img_size=imgsz)
    #     else:
    #         save_img = True
    #         dataset = LoadImages(source, img_size=imgsz, auto_size=64)

    #     self.anchoValue_label.setText(f'{dataset.w}')
    #     self.altoValue_label.setText(f'{dataset.h}')
    #     self.fpsValue_label.setText(f'{dataset.fps}')
        
    #     # Run inference
    #     frame_num = 0
    #     t0 = time.time()
    #     img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    #     _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once
    #     prevTime = 0
    #     for path, img, im0s, vid_cap in dataset:
    #         img = torch.from_numpy(img).to(device)
    #         img = img.half() if half else img.float()  # uint8 to fp16/32
    #         img /= 255.0  # 0 - 255 to 0.0 - 1.0
    #         if img.ndimension() == 3:
    #             img = img.unsqueeze(0)

    #         # Inference
    #         t1 = time_synchronized()
    #         pred = model(img)[0]

    #         # Apply NMS
    #         conf_thres = 0.5
    #         iou_thres = 0.5
    #         classes = [0,1,2,3,5,7] # Filtro de clases: yolor_deepsort/data/coco.names
    #         pred = non_max_suppression(pred, conf_thres, iou_thres, False, classes, False)
    #         t2 = time_synchronized()

    #         # Process detections
    #         for i, det in enumerate(pred):  # detections per image
    #             if webcam:  # batch_size >= 1
    #                 p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
    #             else:
    #                 p, s, im0 = path, '', im0s

    #             save_path = str(Path(out) / Path(p).name)
    #             txt_path = str(Path(out) / Path(p).stem)

    #             if det is not None and len(det):
    #                 # Rescale boxes from img_size to im0 size
    #                 det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

    #                 xywh_bboxs = []
    #                 confs = []
    #                 oids = []
    #                 # Write results
    #                 for *xyxy, conf, cls in det:
    #                     # to deep sort format
    #                     x_c, y_c, bbox_w, bbox_h = self.xyxy_to_xywh(*xyxy)
    #                     xywh_obj = [x_c, y_c, bbox_w, bbox_h]
    #                     xywh_bboxs.append(xywh_obj)
    #                     confs.append([conf.item()])
    #                     oids.append(int(cls))

    #                 xywhs = torch.Tensor(xywh_bboxs)
    #                 confss = torch.Tensor(confs)
                    
    #                 outputs = deepsort.update(xywhs, confss, oids, im0)
    #                 if len(outputs) > 0:
    #                     bbox_xyxy = outputs[:, :4]
    #                     identities = outputs[:, -2]
    #                     object_id = outputs[:, -1]

    #                     self.draw_boxes(im0, bbox_xyxy, object_id, identities)
    #                     self.draw_trajectories(im0, bbox_xyxy, object_id, identities, trailslen)
    #                     self.save_objects(bbox_xyxy, object_id, identities, txt_path, frame_num)
                        
    #             # Print time (inference + NMS)
    #             print(f' Done. ({(t2 - t1):.3f} s)')

    #             currTime = time.time()
    #             fps = 1 / (currTime - prevTime)
    #             prevTime = currTime
                
    #             # Stream results
    #             if view_img:
    #                 cv2.imshow(p, im0)

    #             # Save results (image with detections)
    #             if save_img:
    #                 if dataset.mode == 'images':
    #                     cv2.imwrite(save_path, im0)
    #                 else:
    #                     if vid_path != save_path:  # new video
    #                         vid_path = save_path
    #                         if isinstance(vid_writer, cv2.VideoWriter):
    #                             vid_writer.release()  # release previous video writer

    #                         fourcc = 'mp4v'  # output video codec
    #                         fps = vid_cap.get(cv2.CAP_PROP_FPS)
    #                         w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #                         h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #                         vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
    #                     vid_writer.write(im0)
            
    #         if cv2.waitKey(1) & 0xFF == 27:  # Esc to quit
    #             break
    #         frame_num += 1

    #     print('Done. (%.3fs)' % (time.time() - t0))


    # def detect(self, source, out, imgsz, device, view_img, trailslen):
    #     with torch.no_grad():
    #         self.main(source, out, imgsz, device, view_img, trailslen)



















if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec())