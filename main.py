"""
Main

This file contains main UI class and methods to control components operations.
"""
from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap

from ultralytics import YOLO
import supervision as sv

import sys
import pathlib
import yaml
from collections import deque

import cv2

from main_ui import UI
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
        self.language_value = int(self.config['LANGUAGE'])
        self.theme_style = self.config['THEME_STYLE']
        self.theme_color = self.config['THEME_COLOR']

        # ---------
        # Variables
        # ---------
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

        # ---
        # GUI
        # ---
        self.ui = UI(self)
        theme_file = f"themes/{self.theme_color}_light_theme.qss" if self.theme_style else f"themes/{self.theme_color}_dark_theme.qss"
        with open(theme_file, "r") as theme_qss:
            self.setStyleSheet(theme_qss.read())


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
            if hasattr(self.ui.gui_widgets[key], 'set_language'):
                self.ui.gui_widgets[key].set_language(index)
        
        self.language_value = index
        self.config['LANGUAGE'] = index
        with open(self.settings_file, 'w') as file:
            yaml.dump(self.config, file)


    def on_theme_clicked(self) -> None:
        """ Dark theme segmented control to change components stylesheet
        
        """
        state = not self.theme_style
        theme = 'light' if state else 'dark'
        theme_qss_file = f"themes/{self.theme_color}_{theme}_theme.qss"
        with open(theme_qss_file, "r") as theme_qss:
            self.setStyleSheet(theme_qss.read())
        self.ui.gui_widgets['theme_button'].set_state(state, self.theme_color)

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

        self.ui.gui_widgets['options_divider'].move(8, height - 49)
        self.ui.gui_widgets['language_menu'].move(8, height - 40)
        self.ui.gui_widgets['theme_button'].move(88, height - 40)
        self.ui.gui_widgets['about_button'].move(128, height - 40)

        self.ui.gui_widgets['video_toolbar_card'].resize(width - 204, 68)
        self.ui.gui_widgets['video_slider'].resize(self.ui.gui_widgets['video_toolbar_card'].width() - 324, 32)
        self.ui.gui_widgets['frame_value_textfield'].move(self.ui.gui_widgets['video_toolbar_card'].width() - 108, 8)

        self.ui.gui_widgets['video_output_card'].resize(width - 204, height - 92)

        frame_width = (self.ui.gui_widgets['video_output_card'].height() - 56) * self.aspect_ratio
        frame_height = self.ui.gui_widgets['video_output_card'].height() - 56
        if frame_width > self.ui.gui_widgets['video_output_card'].width() - 16:
            frame_width = self.ui.gui_widgets['video_output_card'].width() - 16
            frame_height = frame_width / self.aspect_ratio
        self.ui.gui_widgets['video_label'].resize(frame_width, frame_height)

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


    # -------
    # Classes
    # -------
    def on_person_chip_clicked(self, state: bool) -> None:
        self.class_options['person'][0] = state
        self.ui.gui_widgets['person_chip'].set_state(state, self.theme_color)

    def on_bicycle_chip_clicked(self, state: bool) -> None:
        self.class_options['bicycle'][0] = state
        self.ui.gui_widgets['bicycle_chip'].set_state(state, self.theme_color)
    
    def on_car_chip_clicked(self, state: bool) -> None:
        self.class_options['car'][0] = state
        self.ui.gui_widgets['car_chip'].set_state(state, self.theme_color)

    def on_motorcycle_chip_clicked(self, state: bool) -> None:
        self.class_options['motorcycle'][0] = state
        self.ui.gui_widgets['motorcycle_chip'].set_state(state, self.theme_color)
 
    def on_bus_chip_clicked(self, state: bool) -> None:
        self.class_options['bus'][0] = state
        self.ui.gui_widgets['bus_chip'].set_state(state, self.theme_color)

    def on_truck_chip_clicked(self, state: bool) -> None:
        self.class_options['truck'][0] = state
        self.ui.gui_widgets['truck_chip'].set_state(state, self.theme_color)

    # -------------
    # Video Toolbar
    # -------------
    def on_backFrame_button_clicked(self) -> None:
        if self.timer_play.isActive(): self.timer_play.stop()
        if self.timer_reverse.isActive(): self.timer_reverse.stop()
        self.play_backward()


    def on_reverse_button_clicked(self) -> None:
        if self.timer_play.isActive(): self.timer_play.stop()
        self.timer_reverse.start(self.time_step)


    def on_pause_button_clicked(self) -> None:
        self.timer_play.stop() if self.timer_play.isActive() else self.timer_reverse.stop()


    def on_play_button_clicked(self) -> None:
        if self.timer_reverse.isActive(): self.timer_reverse.stop()
        self.timer_play.start(self.time_step)


    def on_frontFrame_button_clicked(self) -> None:
        if self.timer_play.isActive(): self.timer_play.stop()
        if self.timer_reverse.isActive(): self.timer_reverse.stop()
        self.play_forward()


    def on_video_slider_sliderMoved(self) -> None:
        self.frame_number = self.ui.gui_widgets['video_slider'].value()
        self.ui.gui_widgets['frame_value_textfield'].text_field.setText(f"{self.frame_number}")
        

    def on_video_slider_sliderReleased(self) -> None:
        self.draw_frame()


    def on_frame_value_textfield_returnPressed(self) -> None:
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
