"""
Main

This file contains main UI class and methods to control components operations.
"""

from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QPixmap

from ultralytics import YOLO
import supervision as sv

import sys
import pathlib
import cv2
import numpy as np

from main_ui import UI

from dialogs.about_app import AboutApp

from tools.print_info import print_video_info, step_message
from tools.annotators import box_annotations, mask_annotations
from tools.write_csv import csv_detections_list, write_csv


# For debugging
from icecream import ic


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

        # ---------
        # Variables
        # ---------
        self.cap = None
        self.source_properties = None

        self.timer_play = None
        self.timer_reverse = None

        self.time_step = 0
        self.frame_number = 0
        self.speed_multiplier = 1

        self.class_options = {
            'person': [False, 0],
            'bicycle': [False, 1],
            'car': [False, 2],
            'motorcycle': [False, 3],
            'bus': [False, 5],
            'truck': [False, 7]
        }

        # ---------------------
        # YOLOv8 Initialization
        # ---------------------
        self.model = YOLO('weights/yolov8m.pt')


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
            self.cap = cv2.VideoCapture(source_file)
            self.source_properties = self.open_video()
            self.time_step = int(1000 / self.source_properties['fps'])

            self.ui.gui_widgets['size_value'].setText(f"{self.source_properties['width']} X {self.source_properties['height']}")
            self.ui.gui_widgets['total_frames_value'].setText(f"{self.source_properties['total_frames']}")
            self.ui.gui_widgets['fps_value'].setText(f"{self.source_properties['fps']:.2f}")

            self.ui.gui_widgets['video_slider'].setEnabled(True)
            self.ui.gui_widgets['video_slider'].setMaximum(self.source_properties['total_frames'])

            # Presentación del frame 0
            self.ui.gui_widgets['video_label'].setPixmap(self.source_properties['first_frame'])
            self.ui.gui_widgets['frame_value_textfield'].text_field.setText(f"{self.frame_number}")

            # Timers
            self.timer_play = QTimer()
            self.timer_play.timeout.connect(self.play_forward)
            self.timer_reverse = QTimer()
            self.timer_reverse.timeout.connect(self.play_backward)

    # -------
    # Classes
    # -------
    def on_person_switch_clicked(self, state: bool) -> None:
        self.class_options['person'][0] = state
        self.ui.gui_widgets['person_on_switch'].setState(state, self.theme_value)
        self.ui.gui_widgets['person_off_switch'].setState(state, self.theme_value)

    def on_bicycle_switch_clicked(self, state: bool) -> None:
        self.class_options['bicycle'][0] = state
        self.ui.gui_widgets['bicycle_on_switch'].setState(state, self.theme_value)
        self.ui.gui_widgets['bicycle_off_switch'].setState(state, self.theme_value)
    
    def on_car_switch_clicked(self, state: bool) -> None:
        self.class_options['car'][0] = state
        self.ui.gui_widgets['car_on_switch'].setState(state, self.theme_value)
        self.ui.gui_widgets['car_off_switch'].setState(state, self.theme_value)

    def on_motorcycle_switch_clicked(self, state: bool) -> None:
        self.class_options['motorcycle'][0] = state
        self.ui.gui_widgets['motorcycle_on_switch'].setState(state, self.theme_value)
        self.ui.gui_widgets['motorcycle_off_switch'].setState(state, self.theme_value)
 
    def on_bus_switch_clicked(self, state: bool) -> None:
        self.class_options['bus'][0] = state
        self.ui.gui_widgets['bus_on_switch'].setState(state, self.theme_value)
        self.ui.gui_widgets['bus_off_switch'].setState(state, self.theme_value)

    def on_truck_switch_clicked(self, state: bool) -> None:
        self.class_options['truck'][0] = state
        self.ui.gui_widgets['truck_on_switch'].setState(state, self.theme_value)
        self.ui.gui_widgets['truck_off_switch'].setState(state, self.theme_value)

    # -------------
    # Video Toolbar
    # -------------
    def on_slow_button_clicked(self) -> None:
        return None


    def on_backFrame_button_clicked(self) -> None:
        return None


    def on_reverse_button_clicked(self) -> None:
        if self.timer_play.isActive():
            self.timer_play.stop()
        self.timer_reverse.start(self.time_step)


    def on_pause_button_clicked(self) -> None:
        if self.timer_play.isActive():
            self.timer_play.stop()
        else:
            self.timer_reverse.stop()


    def on_play_button_clicked(self) -> None:
        if self.timer_reverse.isActive():
            self.timer_reverse.stop()
        self.timer_play.start(self.time_step)


    def on_frontFrame_button_clicked(self) -> None:
        return None


    def on_fast_button_clicked(self) -> None:
        return None


    def on_video_slider_sliderMoved(self) -> None:
        self.ui.gui_widgets['frame_value_textfield'].text_field.setText(str(self.ui.gui_widgets['video_slider'].value()))


    def on_video_slider_sliderReleased(self) -> None:
        return None


    def on_frame_value_textfield_returnPressed(self) -> None:
        self.ui.gui_widgets['video_slider'].setSliderPosition(int(self.ui.gui_widgets['frame_value_textfield'].text_field.text()))







    # ---------
    # Functions
    # ---------
    def convert_cv_qt(self, cv_img):
            """Convert from an opencv image to QPixmap"""
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
            return QPixmap.fromImage(convert_to_qt_format)


    def open_video(self) -> dict:
        if not self.cap.isOpened():
            print('Error opening video stream or file')
            return 0

        _, image = self.cap.read()

        video_properties = {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'total_frames': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': float(self.cap.get(cv2.CAP_PROP_FPS)),
            'first_frame': self.convert_cv_qt(image)
        }

        return video_properties


    def draw_frame(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)
        _, image = self.cap.read()
        annotated_image = image.copy()
        
        class_filter = [ value[1] for value in self.class_options.values() if value[0] ]
        
        # Run YOLOv8 inference
        results = self.model(
            source=image,
            imgsz=640,
            conf=0.5,
            device=0,
            agnostic_nms=True,
            classes=class_filter,
            # retina_masks=True,
            verbose=False
        )[0]

        detections = sv.Detections.from_ultralytics(results)

        # Visualization
        labels = [f"{results.names[class_id]} - {score:.2f}" for _, _, score, class_id, _ in detections]

        # Draw boxes
        annotated_image = box_annotations(annotated_image, detections, labels)

        qt_image = self.convert_cv_qt(annotated_image)
        self.ui.gui_widgets['video_label'].setPixmap(qt_image)


    def play_forward(self):
        if (self.frame_number <= self.source_properties['total_frames']):
            self.frame_number = self.frame_number + self.speed_multiplier
            self.draw_frame()

            self.ui.gui_widgets['video_slider'].setValue(self.frame_number)
            self.ui.gui_widgets['frame_value_textfield'].text_field.setText(f"{self.frame_number}")


    def play_backward(self):
        if (self.frame_number > 0):
            self.frame_number = self.frame_number - self.speed_multiplier
            self.draw_frame()

            self.ui.gui_widgets['video_slider'].setValue(self.frame_number)
            self.ui.gui_widgets['frame_value_textfield'].text_field.setText(f"{self.frame_number}")


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
