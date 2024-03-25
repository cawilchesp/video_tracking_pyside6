from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap

from components.ui_button import UI_Button, UI_ThemeButton, UI_ToggleButton, UI_DropDownButton
from components.ui_checkbox import UI_CheckBox
from components.ui_radiobutton import UI_RadioButton
from components.ui_switch import UI_Switch
from components.ui_text import UI_PasswordBox
from components.ui_label import UI_IconLabel
from components.ui_datetimepicker import UI_CalendarView
from components.ui_combobox import UI_ComboBox

from ultralytics import YOLO
import supervision as sv

from themes.colors import dark_colors, light_colors, theme_colors, icons

import sys
import pathlib
import yaml
from typing import Union
from collections import deque

import cv2

from main_ui import Main_UI
from dialogs.about_app import AboutApp

from tools.annotators import box_annotations, mask_annotations, track_annotations
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
        self.settings_file = 'settings.yaml'
        with open(self.settings_file, 'r') as file:
            self.config = yaml.safe_load(file)

        self.default_folder = self.config['FOLDER']
        self.language_value = self.config['LANGUAGE']
        self.theme_style = self.config['THEME_STYLE']
        self.theme_color = self.config['THEME_COLOR']

        # ---------
        # Variables
        # ---------
        self.weights_options = ['yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']
        self.device_options = ['0', 'cpu']

        self.cap = None
        self.video_width = None
        self.video_height = None
        self.video_total_frames = None
        self.video_fps = None
        self.aspect_ratio = 1.0

        self.timer_play = None
        self.timer_reverse = None

        self.time_step = 0
        self.frame_number = 0

        self.class_options = {
            'person': [False, 0],
            'bicycle': [False, 1],
            'car': [False, 2],
            'motorcycle': [False, 3],
            'bus': [False, 5],
            'truck': [False, 7]
        }

        # object tracks
        self.track_deque = {}

        # Detector and Tracker
        self.yolov8_model = None
        self.byte_tracker = None

        # ----------------
        # Generación de UI
        # ----------------
        self.ui = Main_UI(self)

        # -----------
        # Apply Theme
        # -----------
        with open('themes/style.qss', 'r') as qss_file:
            style_qss = qss_file.read()
        
        style_colors = light_colors if self.theme_style else dark_colors
        for color_name, color_value in style_colors.items():
            style_qss = style_qss.replace(color_name, f"hsl({color_value[0]}, {color_value[1]}%, {color_value[2]}%)")
        
        for color_name, color_value in theme_colors[self.theme_color].items():
            style_qss = style_qss.replace(color_name, f"hsl({color_value[0]}, {color_value[1]}%, {color_value[2]}%)")

        for icon_name, icon_value in icons[self.theme_style].items():
            style_qss = style_qss.replace(icon_name, icon_value)

        self.setStyleSheet(style_qss)

        if self.language_value == 'es':
            self.ui.gui_widgets['language_combobox'].setCurrentIndex(0)
        elif self.language_value == 'en':
            self.ui.gui_widgets['language_combobox'].setCurrentIndex(1)

    # ---------
    # Functions
    # ---------
    def on_language_changed(self, index: int) -> None:
        """ Menu control to change language of component texts
        
        Parameters
        ----------
        index: int
            Index of language menu control
        
        Returns
        -------
        None
        """
        if index == 0: self.language_value = 'es'
        elif index == 1: self.language_value = 'en'

        for key in self.ui.gui_widgets.keys():
            if key != 'language_combobox':
                if hasattr(self.ui.gui_widgets[key], 'set_language'):
                    self.ui.gui_widgets[key].set_language(self.language_value)
                if isinstance(self.ui.gui_widgets[key], UI_ComboBox):
                    self.ui.gui_widgets[key].setCurrentIndex(-1)
            if isinstance(self.ui.gui_widgets[key], UI_DropDownButton):
                for action in self.ui.gui_widgets[key].menu().actions():
                    self.ui.gui_widgets[key].menu().removeAction(action)
                self.ui.gui_widgets[key].set_actions_menu(self.theme_style, self.language_value)
        
        self.config['LANGUAGE'] = self.language_value
        with open(self.settings_file, 'w') as file:
            yaml.dump(self.config, file)


    def on_theme_clicked(self) -> None:
        """ Theme toggle control """
        state = not self.theme_style
        style_colors = light_colors if state else dark_colors

        with open('themes/style.qss', 'r') as qss_file:
            style_qss = qss_file.read()
        
        for color_name, color_value in style_colors.items():
            style_qss = style_qss.replace(color_name, f"hsl({color_value[0]}, {color_value[1]}%, {color_value[2]}%)")
        
        for color_name, color_value in theme_colors[self.theme_color].items():
            style_qss = style_qss.replace(color_name, f"hsl({color_value[0]}, {color_value[1]}%, {color_value[2]}%)")

        for icon_name, icon_value in icons[state].items():
            style_qss = style_qss.replace(icon_name, icon_value)

        self.setStyleSheet(style_qss)

        for key in self.ui.gui_widgets.keys():
            if isinstance(self.ui.gui_widgets[key], Union[UI_Button, UI_ThemeButton, UI_ToggleButton, UI_CheckBox, UI_RadioButton, UI_PasswordBox, UI_IconLabel]):
                self.ui.gui_widgets[key].set_icon(state)
            if isinstance(self.ui.gui_widgets[key], UI_DropDownButton):
                self.ui.gui_widgets[key].set_icon(state)
                for action in self.ui.gui_widgets[key].menu().actions():
                    self.ui.gui_widgets[key].menu().removeAction(action)
                self.ui.gui_widgets[key].set_actions_menu(state, self.language_value)
            if isinstance(self.ui.gui_widgets[key], UI_CalendarView):
                self.ui.gui_widgets[key].set_header(state)
            if isinstance(self.ui.gui_widgets[key], UI_Switch):
                self.ui.gui_widgets[key].set_state(state, self.ui.gui_widgets[key].state)

        # Save settings
        self.theme_style = state
        self.config['THEME_STYLE'] = state
        with open(self.settings_file, 'w') as file:
            yaml.dump(self.config, file)


    def on_about_button_clicked(self) -> None:
        """ About app button to open about app window dialog """
        self.about_app = AboutApp()
        self.about_app.exec()


    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        """ Resize event to control size and position of app components """
        width = self.geometry().width()
        height = self.geometry().height()

        self.ui.gui_widgets['options_divider'].move(16, height - 56)
        self.ui.gui_widgets['language_combobox'].move(12, height - 52)
        self.ui.gui_widgets['theme_button'].move(120, height - 52)
        self.ui.gui_widgets['about_button'].move(160, height - 52)

        self.ui.gui_widgets['video_toolbar_card'].resize(width - 220, 48)
        self.ui.gui_widgets['video_slider'].resize(self.ui.gui_widgets['video_toolbar_card'].width() - 236, 40)
        # self.ui.gui_widgets['frame_value_textfield'].move(self.ui.gui_widgets['video_toolbar_card'].width() - 108, 8)

        # self.ui.gui_widgets['video_output_card'].resize(width - 204, height - 92)

        # frame_width = (self.ui.gui_widgets['video_output_card'].height() - 56) * self.aspect_ratio
        # frame_height = self.ui.gui_widgets['video_output_card'].height() - 56
        # if frame_width > self.ui.gui_widgets['video_output_card'].width() - 16:
        #     frame_width = self.ui.gui_widgets['video_output_card'].width() - 16
        #     frame_height = frame_width / self.aspect_ratio
        # self.ui.gui_widgets['video_label'].resize(frame_width, frame_height)

        return super().resizeEvent(a0)
    

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.timer_play is not None and self.timer_reverse is not None and self.cap is not None:
            self.timer_play.stop() if self.timer_play.isActive() else self.timer_reverse.stop()
            if self.cap.isOpened():
                self.cap.release()

        return super().closeEvent(a0)


    # ------
    # Source
    # ------
    def on_source_add_button_clicked(self) -> None:
        source_file = QtWidgets.QFileDialog.getOpenFileName(
            None,
            'Seleccione el archivo de video',
            self.default_folder,
            'Archivos de Video (*.mp4 *.avi *.mov)'
        )[0]
        
        if source_file is not None:
            # Save folder in settings
            self.config['FOLDER'] = str(pathlib.Path(source_file).parent)
            with open(self.settings_file, 'w') as file:
                yaml.dump(self.config, file)

            # YOLOv8 Initialization
            self.yolov8_model = YOLO('weights/yolov8m.pt')

            # Initialize Byte Tracker
            self.byte_tracker = sv.ByteTrack()

            # Open video
            self.cap = cv2.VideoCapture(source_file)
            if self.cap.isOpened():
                _, image = self.cap.read()

                # Video properties
                self.video_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                self.video_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                self.video_total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.video_fps = float(self.cap.get(cv2.CAP_PROP_FPS))
                
                self.aspect_ratio = float(self.video_width / self.video_height)
                self.time_step = int(1000 / self.video_fps)

                # Timers
                self.timer_play = QTimer()
                self.timer_play.timeout.connect(self.play_forward)
                self.timer_reverse = QTimer()
                self.timer_reverse.timeout.connect(self.play_backward)

                # Write results in GUI
                self.ui.gui_widgets['source_icon'].set_icon_label('file_video', self.theme_color)
                self.ui.gui_widgets['filename_value'].setText(f"{pathlib.Path(source_file).name}")
                self.ui.gui_widgets['size_value'].setText(f"{int(self.video_width)} X {int(self.video_height)}")
                self.ui.gui_widgets['total_frames_value'].setText(f"{self.video_total_frames}")
                self.ui.gui_widgets['fps_value'].setText(f"{self.video_fps:.2f}")

                self.ui.gui_widgets['video_slider'].setEnabled(True)
                self.ui.gui_widgets['video_slider'].setMaximum(self.video_total_frames)

                # Showing first frame
                self.ui.gui_widgets['video_label'].setPixmap(self.convert_cv_qt(image))
                self.ui.gui_widgets['frame_value_textfield'].text_field.setText(f"{self.frame_number}")
                
                # Frame aspect ratio
                self.ui.gui_widgets['video_label'].resize((self.ui.gui_widgets['video_output_card'].height() - 56) * self.aspect_ratio, self.ui.gui_widgets['video_output_card'].height() - 56)
            else:
                print('Error opening video stream or file')

    # -----
    # Model
    # -----
    def model_activated(self, index: int) -> None:
        self.model_weights = self.weights_options[index]

    def size_valueChanged(self) -> None:
        self.model_size = self.ui.gui_widgets['size_numberbox'].value()

    def confidence_valueChanged(self) -> None:
        self.model_confidence = self.ui.gui_widgets['confidence_floatbox'].value()
        
    def device_activated(self, index: int) -> None:
        self.model_device = self.device_options[index]

    def model_start_button_clicked(self) -> None:
        print('start')
    
    def model_stop_button_clicked(self) -> None:
        print('stop')

    # Botón INICIAR INFERENCIA
        # Es en este momento en que se carga el modelo de detección 
        # y de seguimiento
        # Se deben bloquear las opciones de Model Card al iniciar la inferencia
        
        # Botón DETENER INFERENCIA
        # Reactiva las opciones de Model Card
        # Reinicia la carga del modelo de detección

    # -------
    # Classes
    # -------
    def person_chip_clicked(self, state: bool) -> None:
        self.class_options['person'][0] = state
        self.ui.gui_widgets['person_chip'].set_state(state, self.theme_color)

    def bicycle_chip_clicked(self, state: bool) -> None:
        self.class_options['bicycle'][0] = state
        self.ui.gui_widgets['bicycle_chip'].set_state(state, self.theme_color)
    
    def car_chip_clicked(self, state: bool) -> None:
        self.class_options['car'][0] = state
        self.ui.gui_widgets['car_chip'].set_state(state, self.theme_color)

    def motorcycle_chip_clicked(self, state: bool) -> None:
        self.class_options['motorcycle'][0] = state
        self.ui.gui_widgets['motorcycle_chip'].set_state(state, self.theme_color)
 
    def bus_chip_clicked(self, state: bool) -> None:
        self.class_options['bus'][0] = state
        self.ui.gui_widgets['bus_chip'].set_state(state, self.theme_color)

    def truck_chip_clicked(self, state: bool) -> None:
        self.class_options['truck'][0] = state
        self.ui.gui_widgets['truck_chip'].set_state(state, self.theme_color)

    # -------------
    # Video Toolbar
    # -------------
    def backFrame_button_clicked(self) -> None:
        if self.timer_play.isActive(): self.timer_play.stop()
        if self.timer_reverse.isActive(): self.timer_reverse.stop()
        self.play_backward()


    def reverse_button_clicked(self) -> None:
        if self.timer_play.isActive(): self.timer_play.stop()
        self.timer_reverse.start(self.time_step)


    def pause_button_clicked(self) -> None:
        self.timer_play.stop() if self.timer_play.isActive() else self.timer_reverse.stop()


    def play_button_clicked(self) -> None:
        if self.timer_reverse.isActive(): self.timer_reverse.stop()
        self.timer_play.start(self.time_step)


    def frontFrame_button_clicked(self) -> None:
        if self.timer_play.isActive(): self.timer_play.stop()
        if self.timer_reverse.isActive(): self.timer_reverse.stop()
        self.play_forward()


    def video_slider_sliderMoved(self) -> None:
        self.frame_number = self.ui.gui_widgets['video_slider'].value()
        self.ui.gui_widgets['frame_value_textfield'].text_field.setText(f"{self.frame_number}")
        

    def video_slider_sliderReleased(self) -> None:
        self.draw_frame()


    def frame_value_textfield_returnPressed(self) -> None:
        self.frame_number = int(self.ui.gui_widgets['frame_value_textfield'].text_field.text())
        self.ui.gui_widgets['video_slider'].setSliderPosition(self.frame_number)
        self.draw_frame()


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


    def draw_frame(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)
        _, image = self.cap.read()
        annotated_image = image.copy()
        
        class_filter = [ value[1] for value in self.class_options.values() if value[0] ]
        
        # Run YOLOv8 inference
        results = self.yolov8_model(
            source=image,
            imgsz=640,
            conf=0.5,
            device=0,
            agnostic_nms=True,
            classes=class_filter,
            retina_masks=True,
            verbose=False
        )[0]

        detections = sv.Detections.from_ultralytics(results)

        tracks = self.byte_tracker.update_with_detections(detections)

        for track in tracks:
            if track[4] not in self.track_deque:
                self.track_deque[track[4]] = deque(maxlen=64)

        # Draw labels
        labels = [f"{results.names[class_id]} - {tracker_id}" for _, _, _, class_id, tracker_id in tracks]

        # Draw boxes
        annotated_image = box_annotations(annotated_image, tracks, labels)

        # Draw masks
        if detections.mask is not None:
            annotated_image = mask_annotations(annotated_image, detections)
        
        # Draw tracks
        annotated_image = track_annotations(annotated_image, tracks, self.track_deque, 'centroid')

        qt_image = self.convert_cv_qt(annotated_image)
        self.ui.gui_widgets['video_label'].setPixmap(qt_image)


    def play_forward(self):
        if (self.frame_number <= self.video_total_frames):
            self.frame_number += 1
            self.draw_frame()

            self.ui.gui_widgets['video_slider'].setValue(self.frame_number)
            self.ui.gui_widgets['frame_value_textfield'].text_field.setText(f"{self.frame_number}")


    def play_backward(self):
        if (self.frame_number > 0):
            self.frame_number -= 1
            self.draw_frame()

            self.ui.gui_widgets['video_slider'].setValue(self.frame_number)
            self.ui.gui_widgets['frame_value_textfield'].text_field.setText(f"{self.frame_number}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
