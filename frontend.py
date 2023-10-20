"""
Main

This file contains main UI class and methods to control components operations.
"""

from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QSettings
from PySide6.QtGui import QPixmap

import sys
import pathlib
import cv2
import numpy as np

from main_ui import UI

import backend
from backend import open_video
from dialogs.about_app import AboutApp





class MainWindow(QMainWindow):
    def __init__(self):
        """ UI main application """
        super().__init__()
        # --------
        # Settings
        # --------
        self.settings = QSettings(f'{sys.path[0]}/settings.ini', QSettings.Format.IniFormat)
        self.language_value = int(self.settings.value('language'))
        self.theme_value = eval(self.settings.value('theme'))
        self.default_path = self.settings.value('default_path')

        # ---
        # GUI
        # ---
        self.ui = UI(self)


    # ---------------
    # Title Functions
    # ---------------
    def on_language_changed(self, index: int) -> None:
        """ Language menu control to change components text language
        
        Parameters
        ----------
        index: int
            Index of language menu control
        
        Returns
        -------
        None
        """
        for key in self.ui.gui_widgets.keys():
            if hasattr(self.ui.gui_widgets[key], 'setLanguage'):
                self.ui.gui_widgets[key].setLanguage(index)

        self.settings.setValue('language', str(index))
        self.language_value = int(self.settings.value('language'))


    def on_light_theme_clicked(self, state: bool) -> None:
        """ Light theme segmented control to change components stylesheet
        
        Parameters
        ----------
        state: bool
            State of light theme segmented control
        
        Returns
        -------
        None
        """
        if state: 
            for key in self.ui.gui_widgets.keys():
                self.ui.gui_widgets[key].setThemeStyle(True)
            self.ui.gui_widgets['dark_theme_button'].setState(False, True)

            self.settings.setValue('theme', f'{True}')
            self.theme_value = eval(self.settings.value('theme'))
        
        self.ui.gui_widgets['light_theme_button'].setState(True, True)


    def on_dark_theme_clicked(self, state: bool) -> None:
        """ Dark theme segmented control to change components stylesheet
        
        Parameters
        ----------
        state: bool
            State of dark theme segmented control
        
        Returns
        -------
        None
        """
        if state: 
            for key in self.ui.gui_widgets.keys():
                self.ui.gui_widgets[key].setThemeStyle(False)
            self.ui.gui_widgets['light_theme_button'].setState(False, False)

            self.settings.setValue('theme', f'{False}')
            self.theme_value = eval(self.settings.value('theme'))

        self.ui.gui_widgets['dark_theme_button'].setState(True, False)


    def on_about_button_clicked(self) -> None:
        """ About app button to open about app window dialog """
        self.about_app = AboutApp()
        self.about_app.exec()


    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        """ Resize event to control size and position of app components """
        width = self.geometry().width()
        height = self.geometry().height()

        self.ui.gui_widgets['title_bar_card'].resize(width - 16, 48)
        self.ui.gui_widgets['language_menu'].move(width - 224, 8)
        self.ui.gui_widgets['light_theme_button'].move(width - 144, 8)
        self.ui.gui_widgets['dark_theme_button'].move(width - 104, 8)
        self.ui.gui_widgets['about_button'].move(width - 56, 8)

        self.ui.gui_widgets['video_toolbar_card'].resize(width - 204, 68)
        self.ui.gui_widgets['video_slider'].resize(self.ui.gui_widgets['video_toolbar_card'].width() - 404, 32)
        self.ui.gui_widgets['frame_value_textfield'].move(self.ui.gui_widgets['video_toolbar_card'].width() - 108, 8)
        self.ui.gui_widgets['video_output_card'].resize(width - 204, height - 148)
        self.ui.gui_widgets['video_label'].resize(self.ui.gui_widgets['video_output_card'].width() - 16, self.ui.gui_widgets['video_output_card'].height() - 56)
        
        
        # self.ui.gui_widgets['parameters_XT_card'].move(width - 216, 64)
        # self.ui.gui_widgets['parameters_YT_card'].move(width - 216, 200)
        # self.ui.gui_widgets['parameters_XY_card'].move(width - 216, 336)
        # self.ui.gui_widgets['areas_card'].move(width - 216, 472)

        return super().resizeEvent(a0)


    # ------
    # Source
    # ------
    def on_source_add_button_clicked(self) -> None:
        source_file = QtWidgets.QFileDialog.getOpenFileName(None,
            'Seleccione el archivo de video', self.default_path,
            'Archivos de Video (*.mp4 *.avi *.mov)')[0]
        self.ui.gui_widgets['source_icon'].setIconLabel('file_video', self.theme_value)
        self.ui.gui_widgets['filename_value'].setText(source_file)

        if source_file is not None:
            source_properties = open_video(source_file)

            self.ui.gui_widgets['width_value'].setText(f"{source_properties['width']}")
            self.ui.gui_widgets['height_value'].setText(f"{source_properties['height']}")
            self.ui.gui_widgets['count_value'].setText(f"{source_properties['frame_count']}")
            self.ui.gui_widgets['fps_value'].setText(f"{source_properties['fps']:.2f}")

            self.ui.gui_widgets['video_slider'].setEnabled(True)
            self.ui.gui_widgets['video_slider'].setMaximum(source_properties['frame_count'])

            # Presentación del frame 0
            self.ui.gui_widgets['video_label'].setPixmap(source_properties['first_frame'])
            self.ui.gui_widgets['frame_value_textfield'].text_field.setText('0')

            # # YOLOR - DeepSORT Settings
            # yolor_options = {
            #     'cfg': self.ui.gui_widgets['model_configuration_menu'].currentText(),
            #     'weights': self.ui.gui_widgets['model_weights_menu'].currentText(),
            #     'names_file': self.ui.gui_widgets['names_menu'].currentText(),
            #     'inference_size': int(self.ui.gui_widgets['size_menu'].currentText()),
            #     'use_gpu': True if self.ui.gui_widgets['gpu_menu'].currentText() == 'GPU' else False
            # }

            # video_options = {
            #     'source': source_file,
            #     'output': "D:\Data\Videos_Bogotá\ouput",
            #     'view_image': True,
            #     'save_text': True if self.ui.gui_widgets['save_switch_on'].isChecked() else False,
            #     'frame_save': int(self.ui.gui_widgets['frame_save_text'].text_field.text()),
            #     'trail': int(self.ui.gui_widgets['trail_text'].text_field.text()),
            #     'class_filter': [0,1,2,3,5,7], # Based on coco.names
            #     'show_boxes': True,
            #     'show_trajectories': True,
            #     'save_video': True if self.ui.gui_widgets['save_switch_on'].isChecked() else False
            # }
            # # presentar video en Label
            # # detección solo en imágenes
            # # tomar frame del video y sacar frame procesado

            # yolor = YOLOR_DEEPSORT(yolor_options, video_options)
            # yolor.detect()







    # -------
    # Classes
    # -------
    def on_person_button_clicked(self) -> None:
        return None
    
    def on_bicycle_button_clicked(self) -> None:
        return None
    
    def on_car_button_clicked(self) -> None:
        return None
    
    def on_motorcycle_button_clicked(self) -> None:
        return None
    
    def on_bus_button_clicked(self) -> None:
        return None
    
    def on_truck_button_clicked(self) -> None:
        return None


    # -------------
    # Video Toolbar
    # -------------
    def on_slow_button_clicked(self) -> None:
        return None


    def on_backFrame_button_clicked(self) -> None:
        return None


    def on_reverse_button_clicked(self) -> None:
        return None


    def on_pause_button_clicked(self) -> None:
        return None


    def on_play_button_clicked(self) -> None:
        return None


    def on_frontFrame_button_clicked(self) -> None:
        return None


    def on_fast_button_clicked(self) -> None:
        return None


    def on_video_slider_sliderMoved(self):
        self.ui.gui_widgets['frame_value_textfield'].text_field.setText(str(self.ui.gui_widgets['video_slider'].value()))


    def on_video_slider_sliderReleased(self):
        # backend.set_PTZ(self.pan_edit.text(), self.tilt_edit.text(), self.zoom_edit.text(), 
        #                 self.ipaddress_combobox.currentText(), self.user_edit.text(), 
        #                 self.password_edit.text())
        return None


    def on_frame_value_textfield_returnPressed(self):
        self.ui.gui_widgets['video_slider'].setSliderPosition(int(self.ui.gui_widgets['frame_value_textfield'].text_field.text()))


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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
