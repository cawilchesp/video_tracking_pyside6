from PyQt6 import QtGui, QtWidgets, QtCore
from PyQt6.QtWidgets import QWidget, QApplication, QStyle
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QSettings

import sys
import pathlib
import psycopg2
import cv2
import numpy as np

from ui import UI

import backend

from backend import open_video
from dialogs.about_app import AboutApp

from yolor_class import YOLOR_DEEPSORT





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
        # --------
        # Settings
        # --------
        self.settings = QSettings(f'{sys.path[0]}/settings.ini', QSettings.Format.IniFormat)
        self.language_value = int(self.settings.value('language'))
        self.theme_value = eval(self.settings.value('theme'))
        self.default_path = self.settings.value('default_path')

        # ----------------
        # Generación de UI
        # ----------------
        self.ui = UI(self)


    # -----
    # Title
    # -----
    def on_idioma_menu_currentIndexChanged(self, index: int) -> None:
        """ Language menu control to change components text language
        
        Parameters
        ----------
        index: int
            Index of language menu control
        
        Returns
        -------
        None
        """
        for key, value in self.ui.gui_widgets.items():
            self.ui.gui_widgets[key].language_text(index)

        self.settings.setValue('language', str(index))
        self.language_value = int(self.settings.value('language'))



    def on_tema_switch_light_clicked(self, state: bool) -> None:
        """ Dark Theme switch control to change components stylesheet
        
        Parameters
        ----------
        state: bool
            State of theme switch control
        
        Returns
        -------
        None
        """
        if state: 
            for key, value in self.ui.gui_widgets.items():
                self.ui.gui_widgets[key].apply_styleSheet(True)
            self.ui.gui_widgets['tema_switch_light'].set_state(True)
            self.ui.gui_widgets['tema_switch_dark'].set_state(False)
        
            self.settings.setValue('theme', f'{True}')
            self.theme_value = eval(self.settings.value('theme'))


    def on_tema_switch_dark_clicked(self, state: bool) -> None:
        """ Light Theme switch control to change components stylesheet
        
        Parameters
        ----------
        state: bool
            State of theme switch control
        
        Returns
        -------
        None
        """
        if state: 
            for key, value in self.ui.gui_widgets.items():
                self.ui.gui_widgets[key].apply_styleSheet(False)
            self.ui.gui_widgets['tema_switch_light'].set_state(False)
            self.ui.gui_widgets['tema_switch_dark'].set_state(True)
    
            self.settings.setValue('theme', f'{False}')
            self.theme_value = eval(self.settings.value('theme'))


    # def on_database_button_clicked(self) -> None:
    #     """ Database button to configure the database """
    #     self.db_info = database.Database()
    #     self.db_info.exec()
        
    #     if self.db_info.database_data:
    #         self.patientes_list = backend.create_db('pacientes')
    #         self.estudios_list = backend.create_db('estudios')

    #         for data in self.patientes_list:
    #             self.pacientes_menu.addItem(str(data[4]))
    #         self.pacientes_menu.setCurrentIndex(-1)

    #         self.pacientes_menu.setEnabled(True)
    #         self.paciente_add_button.setEnabled(True)
    #         self.paciente_edit_button.setEnabled(True)
    #         self.paciente_del_button.setEnabled(True)

    #         if self.language_value == 0:
    #             QtWidgets.QMessageBox.information(self, 'Datos Guardados', 'Base de datos configurada')
    #         elif self.language_value == 1:
    #             QtWidgets.QMessageBox.information(self, 'Data Saved', 'Database configured')
    #     else:
    #         if self.language_value == 0:
    #             QtWidgets.QMessageBox.critical(self, 'Error de Datos', 'No se dio información de la base de datos')
    #         elif self.language_value == 1:
    #             QtWidgets.QMessageBox.critical(self, 'Data Error', 'No information on the database was given')


    def on_manual_button_clicked(self) -> None:
        """ Manual button to open manual window """
        return 0


    def on_about_button_clicked(self) -> None:
        """ About app button to open about app window dialog """
        self.about_app = AboutApp()
        self.about_app.exec()


    def on_aboutQt_button_clicked(self) -> None:
        """ About Qt button to open about Qt window dialog """
        backend.about_qt_dialog(self, self.language_value)


    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        """ Resize event to control size and position of app components """
        width = self.geometry().width()
        height = self.geometry().height()

        self.ui.gui_widgets['titulo_card'].resize(width - 16, 48)
        self.ui.gui_widgets['idioma_menu'].move(self.ui.gui_widgets['titulo_card'].width() - 300, 8)
        self.ui.gui_widgets['tema_switch_light'].move(self.ui.gui_widgets['titulo_card'].width() - 220, 8)
        self.ui.gui_widgets['tema_switch_dark'].move(self.ui.gui_widgets['titulo_card'].width() - 194, 8)
        self.ui.gui_widgets['database_button'].move(self.ui.gui_widgets['titulo_card'].width() - 160, 8)
        self.ui.gui_widgets['manual_button'].move(self.ui.gui_widgets['titulo_card'].width() - 120, 8)
        self.ui.gui_widgets['about_button'].move(self.ui.gui_widgets['titulo_card'].width() - 80, 8)
        self.ui.gui_widgets['aboutQt_button'].move(self.ui.gui_widgets['titulo_card'].width() - 40, 8)

        self.ui.gui_widgets['video_toolbar_card'].resize(width - 412, 72)
        self.ui.gui_widgets['video_slider'].resize(self.ui.gui_widgets['video_toolbar_card'].width() - 404, 32)
        self.ui.gui_widgets['frame_value_text'].move(self.ui.gui_widgets['video_toolbar_card'].width() - 108, 8)

        self.ui.gui_widgets['video_output_card'].setGeometry(196, 144, width - 412, height - 152)
        self.ui.gui_widgets['video_output_card'].title.resize(width - 204, 32)
        self.ui.gui_widgets['video_label'].setGeometry(8, 48, self.ui.gui_widgets['video_output_card'].width() - 16, self.ui.gui_widgets['video_output_card'].height() - 56)
        
        self.ui.gui_widgets['yolor_deepsort_card'].move(self.ui.gui_widgets['video_toolbar_card'].x() + self.ui.gui_widgets['video_toolbar_card'].width() + 8, self.ui.gui_widgets['titulo_card'].y() + self.ui.gui_widgets['titulo_card'].height() + 8)

        return super().resizeEvent(a0)


    # ------
    # Source
    # ------
    def on_source_menu_textActivated(self, source: str) -> None:
        self.ui.gui_widgets['source_add_button'].setEnabled(True)


    def on_source_add_button_clicked(self) -> None:
        source = self.ui.gui_widgets['source_menu'].currentText()

        if source == 'Webcam':
            source_file = 0
            self.ui.gui_widgets['source_icon'].set_icon('webcam', self.theme_value)
            self.ui.gui_widgets['filename_value'].setText('')
        elif source == 'Archivo de Video' or source == 'Video File':
            source_file = QtWidgets.QFileDialog.getOpenFileName(None,
                'Seleccione el archivo de video', self.default_path,
                'Archivos de Video (*.mp4 *.avi *.mov)')[0]
            self.ui.gui_widgets['source_icon'].set_icon('file_video', self.theme_value)
            self.ui.gui_widgets['filename_value'].setText(source_file)

        if source_file is not None:
            source_properties = open_video(source_file)

            self.ui.gui_widgets['source_value'].setText(source)
            self.ui.gui_widgets['width_value'].setText(f"{source_properties['width']}")
            self.ui.gui_widgets['height_value'].setText(f"{source_properties['height']}")
            self.ui.gui_widgets['count_value'].setText(f"{source_properties['frame_count']}")
            self.ui.gui_widgets['fps_value'].setText(f"{source_properties['fps']:.2f}")

            self.ui.gui_widgets['video_slider'].setEnabled(True)
            self.ui.gui_widgets['video_slider'].setMaximum(source_properties['frame_count'])

            # Presentación del frame 0
            self.ui.gui_widgets['video_label'].setPixmap(source_properties['first_frame'])
            self.ui.gui_widgets['frame_value_text'].text_field.setText('0')

            # YOLOR - DeepSORT Settings
            
            
            
            
            
            self.ui.gui_widgets['save_switch_off'].isChecked()
            self.ui.gui_widgets['save_switch_on'].isChecked()
            self.ui.gui_widgets['frame_save_text'].text_field.text()
            self.ui.gui_widgets['trail_text'].text_field.text()

            yolor_options = {
                'cfg': self.ui.gui_widgets['model_configuration_menu'].currentIndex(),
                'weights': self.ui.gui_widgets['model_weights_menu'].currentIndex(),
                'names_file': self.ui.gui_widgets['names_menu'].currentIndex(),
                'inference_size': int(self.ui.gui_widgets['size_menu'].currentIndex()),
                'use_gpu': True if self.ui.gui_widgets['gpu_menu'].currentIndex() == 'GPU' else False
            }

            video_options = {
                'source': source_file,
                'output': "D:\Data\Videos_Bogotá\ouput",
                'view_image': True,
                'save_text': True,
                'frame_save': 300,
                'trail': 64,
                'class_filter': [0,1,2,3,5,7], # Based on coco.names
                'show_boxes': True,
                'show_trajectories': True,
                'save_video': True
            }

            yolor = YOLOR_DEEPSORT(yolor_options, video_options)
            yolor.detect()







    # -------
    # Classes
    # -------
    def on_classes_menu_textActivated(self, class_name: str) -> None:
        return 0


    def on_color_button_clicked(self) -> None:
        selected_color = QtWidgets.QColorDialog.getColor()
        color = f'{selected_color.red()}, {selected_color.green()}, {selected_color.blue()}'
        # self.color_button.style_sheet(theme_value, color)
        # settings.setValue('color', color)
        
        return 0


    # -------------
    # Video Toolbar
    # -------------
    def on_slow_button_clicked(self) -> None:
        return 0


    def on_backFrame_button_clicked(self) -> None:
        return 0


    def on_reverse_button_clicked(self) -> None:
        return 0


    def on_pause_button_clicked(self) -> None:
        return 0


    def on_play_button_clicked(self) -> None:
        return 0


    def on_frontFrame_button_clicked(self) -> None:
        return 0


    def on_fast_button_clicked(self) -> None:
        return 0


    def on_video_slider_sliderMoved(self):
        self.ui.gui_widgets['frame_value_text'].text_field.setText(str(self.ui.gui_widgets['video_slider'].value()))


    def on_video_slider_sliderReleased(self):
        # backend.set_PTZ(self.pan_edit.text(), self.tilt_edit.text(), self.zoom_edit.text(), 
        #                 self.ipaddress_combobox.currentText(), self.user_edit.text(), 
        #                 self.password_edit.text())
        return 0





    # -----------------
    # YOLOR - Deep SORT
    # -----------------
    def on_save_switch_off_clicked(self, state: bool) -> None:
        """ Image Save Off switch control to change components stylesheet
        
        Parameters
        ----------
        state: bool
            State of image save off switch control
        
        Returns
        -------
        None
        """
        if state: 
            self.ui.gui_widgets['save_switch_on'].set_state(False)
            self.ui.gui_widgets['save_switch_off'].set_state(True)


    def on_save_switch_on_clicked(self, state: bool) -> None:
        """ Image Save On switch control to change components stylesheet
        
        Parameters
        ----------
        state: bool
            State of image save on switch control
        
        Returns
        -------
        None
        """
        if state:
            self.ui.gui_widgets['save_switch_on'].set_state(True)
            self.ui.gui_widgets['save_switch_off'].set_state(False)









    # def on_abrir_button_clicked(self):
    #     global recent_videos

    #     connection = psycopg2.connect(user='postgres',
    #                           password='ecf406Carolina',
    #                           host='localhost',
    #                           port='5432',
    #                           database='video_annotator')
    #     cursor = connection.cursor()

    #     last_folder = settings.value('video_folder')
    #     selected_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Seleccione el archivo de video', last_folder,
    #                                                           'Archivos de Video (*.avi *.mp4 *.mpg *.m4v *.mkv)')
    #     if selected_file[0]:
    #         file_path = pathlib.Path(selected_file[0])
    #         video_path = str(file_path.resolve())
    #         video_name = str(file_path.name)

    #         settings.setValue('video_folder', str(file_path.parent))

    #         cursor.execute(f"SELECT * FROM videos WHERE path='{video_path}'")
    #         data = cursor.fetchall()

    #         if not data:
    #             video_properties = backend.open_video(video_path)

    #             width = video_properties['width']
    #             height = video_properties['height']
    #             frame_count = video_properties['frame_count']
    #             fps = video_properties['fps']
    #             is_calibrated = False
    #             matrix = ''

    #             insert_query = f"""INSERT INTO videos (name, path, width, height, frame_count, fps, is_calibrated, matrix) 
    #                             VALUES ('{video_name[:-4]}', '{video_path}', '{width}', '{height}', '{frame_count}', '{fps}', '{is_calibrated}', '{matrix}')"""
    #             cursor.execute(insert_query)
    #             connection.commit()
    #             cursor.execute('SELECT * FROM videos')
    #             recent_videos = cursor.fetchall()

    #             self.recientes_combobox.clear()
    #             for data in recent_videos:
    #                 self.recientes_combobox.addItem(data[1])
    #             self.recientes_combobox.setCurrentIndex(self.recientes_combobox.count() - 1)

    #             self.anchoValue_label.setText(f'{width}')
    #             self.altoValue_label.setText(f'{height}')
    #             self.video_slider.setMaximum(frame_count)

    #             cv_img = video_properties['first_frame']
    #             qt_img = backend.convert_cv_qt(cv_img)
    #             self.video_label.setPixmap(qt_img)
    #         else:
    #             error_message = QtWidgets.QMessageBox.critical(self, 'Error de Video', 'El video ya se encuentra en la base de datos')


    # def on_eliminar_button_clicked(self):
    #     global recent_videos

    #     connection = psycopg2.connect(user='postgres',
    #                           password='ecf406Carolina',
    #                           host='localhost',
    #                           port='5432',
    #                           database='video_annotator')
    #     cursor = connection.cursor()
        
    #     video_name = self.recientes_combobox.currentText()
    #     if video_name != '':
    #         delete_query = f"DELETE FROM videos WHERE name='{video_name}'"
    #         cursor.execute(delete_query)
    #         connection.commit()
    #         cursor.execute('SELECT * FROM videos')
    #         recent_videos = cursor.fetchall()

    #         self.recientes_combobox.clear()
    #         for data in recent_videos:
    #             self.recientes_combobox.addItem(data[1])
    #         self.recientes_combobox.setCurrentIndex(-1)

    #         self.anchoValue_label.setText('')
    #         self.altoValue_label.setText('')
    #         self.video_label.clear()
            
    #         connection.close()

    #         success_message = QtWidgets.QMessageBox.information(self, 'Datos Guardados', 'Video eliminado de la base de datos')
    #     else:
    #         error_message = QtWidgets.QMessageBox.critical(self, 'Error de Video', 'No se seleccionó ningún video')


if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec())
