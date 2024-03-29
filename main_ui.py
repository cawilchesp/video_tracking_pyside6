from PySide6.QtWidgets import QWidget

from components.ui_window import UI_Window
from components.ui_card import UI_Card
from components.ui_label import UI_Label, UI_IconLabel
from components.ui_button import UI_Button, UI_ToggleButton, UI_ThemeButton
from components.ui_combobox import UI_ComboBox
from components.ui_radiobutton import UI_RadioButton
from components.ui_chart import UI_Chart
from components.ui_divider import UI_Divider
from components.ui_numberbox import UI_NumberBox, UI_FloatBox
from components.ui_slider import UI_Slider

import yaml


class Main_UI(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # --------
        # Settings
        # --------
        with open('settings.yaml', 'r') as file:
            self.config = yaml.safe_load(file)

        self.default_folder = self.config['FOLDER']
        self.language_value = self.config['LANGUAGE']
        self.theme_style = self.config['THEME_STYLE']
        self.theme_color = self.config['THEME_COLOR']

        # ---------
        # Variables
        # ---------
        self.gui_widgets = {}

        self.model_options = {
            0: ('YOLOv8 - medio', 'YOLOv8 - medium'),
            1: ('YOLOv8 - grande', 'YOLOv8 - large'),
            2: ('YOLOv8 - extragrande', 'YOLOv8 - extralarge') }
        
        self.device_options = {
            0: ('0', '0'),
            1: ('cpu', 'cpu')
        }

        # -----------
        # Main Window
        # -----------
        (width, height) = (1300, 700)
        self.gui_widgets['main_window'] = UI_Window(
            parent=parent,
            size=(width, height),
            minimum_size=(width, height),
            titles=('Seguidor de Objetos en Video', 'Video Object Tracker'),
            language=self.language_value )

        # -------
        # Options
        # -------
        self.gui_widgets['options_divider'] = UI_Divider(
            parent=parent,
            length=180,
            orientation='horizontal' )
        
        self.gui_widgets['language_combobox'] = UI_ComboBox(
            parent=parent,
            width=108,
            texts=('Idioma', 'Language'),
            options={0: ('ESP', 'SPA'), 1: ('ING', 'ENG')},
            set=-1,
            language=self.language_value,
            activated_signal=parent.on_language_changed )

        self.gui_widgets['theme_button'] = UI_ThemeButton(
            parent=parent,
            state=self.theme_style,
            clicked_signal=parent.on_theme_clicked )
        
        self.gui_widgets['about_button'] = UI_Button(
            parent=parent,
            type='accent',
            icon_name='mail',
            clicked_signal=parent.on_about_button_clicked )

        # -----------
        # Card Source
        # -----------
        self.gui_widgets['source_card'] = UI_Card(
            parent=parent,
            position=(16, 16),
            size=(180, 88) )
        
        self.gui_widgets['source_label'] = UI_Label(
            parent=self.gui_widgets['source_card'],
            position=(8, 8),
            width=self.gui_widgets['source_card'].width() - 16,
            align='left',
            font_size=16,
            texts=('Origen del Video', 'Video Source'),
            language=self.language_value )
        
        self.gui_widgets['source_add_button'] = UI_Button(
            parent=self.gui_widgets['source_card'],
            position=(136, 44),
            type='accent',
            icon_name='plus',
            clicked_signal=parent.on_source_add_button_clicked )

        # ----------------
        # Card Information
        # ----------------
        self.gui_widgets['info_card'] = UI_Card(
            parent=parent,
            position=(16, 112),
            size=(180, 184) )
        
        self.gui_widgets['info_label'] = UI_Label(
            parent=self.gui_widgets['info_card'],
            position=(8, 8),
            width=self.gui_widgets['info_card'].width() - 16,
            align='left',
            font_size=16,
            texts=('Información', 'Information'),
            language=self.language_value )
        
        self.gui_widgets['source_icon'] = UI_IconLabel(
            parent=self.gui_widgets['info_card'],
            position=(8, 48),
            icon_name='file-video' )
        
        self.gui_widgets['filename_value'] = UI_Label(
            parent=self.gui_widgets['info_card'],
            position=(48, 48),
            width=164,
            align='left',
            texts=('Nombre del archivo', 'File Name'),
            language=self.language_value )
        
        self.gui_widgets['size_value'] = UI_Label(
            parent=self.gui_widgets['info_card'],
            position=(48, 80),
            width=164,
            align='left',
            texts=('Ancho X Alto', 'Width X Height'),
            language=self.language_value )
        
        self.gui_widgets['total_value'] = UI_Label(
            parent=self.gui_widgets['info_card'],
            position=(48, 112),
            width=164,
            align='left',
            texts=('Total de Cuadros', 'Total Frames'),
            language=self.language_value )
        
        self.gui_widgets['fps_value'] = UI_Label(
            parent=self.gui_widgets['info_card'],
            position=(48, 144),
            width=164,
            align='left',
            texts=('CPS', 'FPS'),
            language=self.language_value )

        # ----------
        # Card Model
        # ----------
        self.gui_widgets['model_card'] = UI_Card(
            parent=parent,
            position=(16, 304),
            size=(180, 248) )
        
        self.gui_widgets['model_label'] = UI_Label(
            parent=self.gui_widgets['model_card'],
            position=(8, 8),
            width=self.gui_widgets['model_card'].width() - 16,
            align='left',
            font_size=16,
            texts=('Modelo', 'Model'),
            language=self.language_value )
        
        self.gui_widgets['model_menu'] = UI_ComboBox(
            parent=self.gui_widgets['model_card'],
            position=(4, 44),
            width=self.gui_widgets['model_card'].width() - 8,
            options=self.model_options,
            language=self.language_value,
            activated_signal=parent.model_activated )

        self.gui_widgets['size_numberbox'] = UI_NumberBox(
            parent=self.gui_widgets['model_card'],
            position=(4, 84),
            width=self.gui_widgets['model_card'].width() - 8,
            range=(640, 640, 3840),
            value=640,
            value_changed_signal=parent.size_valueChanged )
        
        self.gui_widgets['confidence_floatbox'] = UI_FloatBox(
            parent=self.gui_widgets['model_card'],
            position=(4, 124),
            width=self.gui_widgets['model_card'].width() - 8,
            range=(0.1, 0.1, 1.0),
            value=0.5,
            value_changed_signal=parent.confidence_valueChanged )
        
        self.gui_widgets['device_menu'] = UI_ComboBox(
            parent=self.gui_widgets['model_card'],
            position=(4, 164),
            width=self.gui_widgets['model_card'].width() - 8,
            options=self.device_options,
            language=self.language_value,
            activated_signal=parent.device_activated )
        
        self.gui_widgets['model_start_button'] = UI_Button(
            parent=self.gui_widgets['model_card'],
            position=(136, 204),
            type='accent',
            icon_name='play-circle-outline',
            clicked_signal=parent.model_start_button_clicked )

        self.gui_widgets['model_stop_button'] = UI_Button(
            parent=self.gui_widgets['model_card'],
            position=(96, 204),
            type='accent',
            icon_name='stop-circle-outline',
            clicked_signal=parent.model_stop_button_clicked )

        # ------------------
        # Card Video Toolbar
        # ------------------
        self.gui_widgets['video_toolbar_card'] = UI_Card(
            parent=parent,
            position=(204, 16) )

        self.gui_widgets['backFrame_button'] = UI_Button(
            parent=self.gui_widgets['video_toolbar_card'],
            position=(4, 4),
            type='accent',
            icon_name='step-backward',
            enabled=True,
            clicked_signal=parent.backFrame_button_clicked )

        self.gui_widgets['reverse_button'] = UI_Button(
            parent=self.gui_widgets['video_toolbar_card'],
            position=(44, 4),
            type='accent',
            # icon_name='reverse',
            enabled=True,
            clicked_signal=parent.reverse_button_clicked )

        self.gui_widgets['pause_button'] = UI_Button(
            self.gui_widgets['video_toolbar_card'],
            position=(84, 4),
            type='accent',
            icon_name='pause',
            enabled=True,
            clicked_signal=parent.pause_button_clicked )

        self.gui_widgets['play_button'] = UI_Button(
            parent=self.gui_widgets['video_toolbar_card'],
            position=(124, 4),
            type='accent',
            icon_name='play', 
            enabled=True,
            clicked_signal=parent.play_button_clicked )

        self.gui_widgets['frontFrame_button'] = UI_Button(
            parent=self.gui_widgets['video_toolbar_card'],
            position=(164, 4),
            type='accent',
            icon_name='step-forward', 
            enabled=True,
            clicked_signal=parent.frontFrame_button_clicked )

        self.gui_widgets['video_slider'] = UI_Slider(
            parent=self.gui_widgets['video_toolbar_card'],
            position=(208, 4),
            # enabled=False,
            slider_moved_signal=parent.video_slider_sliderMoved,
            slider_released_signal=parent.video_slider_sliderReleased )

        # self.gui_widgets['frame_value_textfield'] = MD3TextField(self.gui_widgets['video_toolbar_card'], {
        #     'width': 100,
        #     'type': 'outlined',
        #     'labels': ('Cuadro', 'Frame'),
        #     'input': 'integer',
        #     'language': self.language_value,
        #     'return_pressed': parent.on_frame_value_textfield_returnPressed } )

        # # ----------------
        # # Card Video Image
        # # ----------------
        # self.gui_widgets['video_output_card'] = MD3Card(parent, {
        #     'position': (196, 84),
        #     'type': 'outlined',
        #     'titles': ('Salida del Video','Video Output'),
        #     'language': self.language_value } )
        
        # self.gui_widgets['video_label'] = MD3ImageLabel(self.gui_widgets['video_output_card'], {
        #     'position': (8, 48),
        #     'scaled_image': True } )

        # ------------
        # Card Classes
        # ------------
        # self.gui_widgets['classes_card'] = MD3Card(parent, {
        #     'position': (8, 288), 
        #     'size': (180, 288),
        #     'type': 'outlined',
        #     'titles': ('Clases', 'Classes'),
        #     'language': self.language_value } )
        
        # self.gui_widgets['person_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
        #     'position': (8, 48),
        #     'width': 120,
        #     'labels': ('Persona', 'Person'),
        #     'icon': 'person',
        #     'state': False,
        #     'theme_color': self.theme_color,
        #     'language': self.language_value,
        #     'clicked': parent.on_person_chip_clicked } )
        
        # self.gui_widgets['bicycle_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
        #     'position': (8, 88),
        #     'width': 120,
        #     'labels': ('Bicicleta', 'Bicycle'),
        #     'icon': 'bicycle',
        #     'state': False,
        #     'theme_color': self.theme_color,
        #     'language': self.language_value,
        #     'clicked': parent.on_bicycle_chip_clicked } )

        # self.gui_widgets['car_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
        #     'position': (8, 128),
        #     'width': 120,
        #     'labels': ('Carro', 'Car'),
        #     'icon': 'car',
        #     'state': False,
        #     'theme_color': self.theme_color,
        #     'language': self.language_value,
        #     'clicked': parent.on_car_chip_clicked } )
        
        # self.gui_widgets['motorcycle_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
        #     'position': (8, 168),
        #     'width': 120,
        #     'labels': ('Motocicleta', 'Motorcycle'),
        #     'icon': 'motorcycle',
        #     'state': False,
        #     'theme_color': self.theme_color,
        #     'language': self.language_value,
        #     'clicked': parent.on_motorcycle_chip_clicked } )

        # self.gui_widgets['bus_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
        #     'position': (8, 208),
        #     'width': 120,
        #     'labels': ('Bus', 'Bus'),
        #     'icon': 'bus',
        #     'state': False,
        #     'theme_color': self.theme_color,
        #     'language': self.language_value,
        #     'clicked': parent.on_bus_chip_clicked } )
        
        # self.gui_widgets['truck_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
        #     'position': (8, 248),
        #     'width': 120,
        #     'labels': ('Camión', 'Truck'),
        #     'icon': 'truck',
        #     'state': False,
        #     'theme_color': self.theme_color,
        #     'language': self.language_value,
        #     'clicked': parent.on_truck_chip_clicked } )

        