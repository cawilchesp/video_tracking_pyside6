from PySide6.QtWidgets import QWidget

from components.md3_window import MD3Window
from components.md3_card import MD3Card
from components.md3_menu import MD3Menu
from components.md3_iconbutton import MD3IconButton
from components.md3_chip import MD3Chip
from components.md3_label import MD3Label
from components.md3_textfield import MD3TextField
from components.md3_slider import MD3Slider
from components.md3_imagelabel import MD3ImageLabel
from components.md3_segmentedbutton import MD3SegmentedButton

import yaml


class UI(QWidget):
    def __init__(self, parent):
        super(UI, self).__init__(parent)

        # --------
        # Settings
        # --------
        with open('settings.yaml', 'r') as file:
            self.config = yaml.safe_load(file)

        self.default_folder = self.config['FOLDER']
        self.language_value = int(self.config['LANGUAGE'])
        self.theme_style = self.config['THEME_STYLE']
        self.theme_color = self.config['THEME_COLOR']

        # ---------
        # Variables
        # ---------
        self.gui_widgets = {}

        # -----------
        # Main Window
        # -----------
        (width, height) = (1300, 700)
        self.gui_widgets['main_window'] = MD3Window( {
            'parent': parent,
            'size': (width, height),
            'minimum_size': (width, height),
            'labels': ('Seguidor de Objetos en Video', 'Video Object Tracker'),
            'language': self.language_value } )

        # ----------
        # Card Title
        # ----------
        self.gui_widgets['title_bar_card'] = MD3Card(parent, {
            'position': (8, 8),
            'type': 'outlined',
            'language': self.language_value } )


        # # # Espacio para título de la aplicación, logo, etc.

        
        self.gui_widgets['language_menu'] = MD3Menu(self.gui_widgets['title_bar_card'], {
            'width': 72,
            'type': 'outlined',
            'options': {0: ('ESP', 'SPA'), 1: ('ING', 'ENG')},
            'set': self.language_value,
            'language': self.language_value,
            'index_changed': parent.on_language_changed } )

        self.gui_widgets['light_theme_button'] = MD3SegmentedButton(self.gui_widgets['title_bar_card'], {
            'width': 40,
            'icon': 'light_mode',
            'check_icon': False,
            'location': 'left',
            'state': self.theme_style,
            'theme_color': self.theme_color,
            'language': self.language_value,
            'clicked': parent.on_light_theme_clicked } )

        self.gui_widgets['dark_theme_button'] = MD3SegmentedButton(self.gui_widgets['title_bar_card'], {
            'width': 40,
            'icon': 'dark_mode',
            'check_icon': False,
            'location': 'right',
            'state': not self.theme_style,
            'theme_color': self.theme_color,
            'language': self.language_value,
            'clicked': parent.on_dark_theme_clicked } )
        
        self.gui_widgets['about_button'] = MD3IconButton(self.gui_widgets['title_bar_card'], {
            'type': 'filled',
            'icon': 'mail',
            'theme_color': self.theme_color,
            'clicked': parent.on_about_button_clicked } )

        # -----------
        # Card Source
        # -----------
        self.gui_widgets['source_card'] = MD3Card(parent, {
            'position': (8, 64),
            'size': (180, 88),
            'type': 'outlined',
            'titles': ('Origen del Video', 'Video Source'),
            'language': self.language_value } )
        
        self.gui_widgets['source_add_button'] = MD3IconButton(self.gui_widgets['source_card'], {
            'position': (140, 48),
            'type': 'filled',
            'icon': 'new',
            'theme_color': self.theme_color,
            'clicked': parent.on_source_add_button_clicked } )

        # ----------------
        # Card Information
        # ----------------
        self.gui_widgets['info_card'] = MD3Card(parent, {
            'position': (8, 160),
            'size': (180, 176),
            'type': 'outlined',
            'titles': ('Información', 'Information'),
            'language': self.language_value } )

        self.gui_widgets['source_icon'] = MD3Label(self.gui_widgets['info_card'], {
            'position': (8, 48),
            'type': 'icon',
            'icon': 'cam',
            'theme_color': self.theme_color } )
        
        self.gui_widgets['filename_value'] = MD3Label(self.gui_widgets['info_card'], {
            'position': (48, 56), 
            'width': 124,
            'type': 'subtitle',
            'align': 'left',
            'labels': ('Nombre del archivo', 'File Name'),
            'language': self.language_value } )

        self.gui_widgets['size_icon'] = MD3Label(self.gui_widgets['info_card'], {
            'position': (8, 80),
            'type': 'icon',
            'icon': 'size',
            'theme_color': self.theme_color } )

        self.gui_widgets['size_value'] = MD3Label(self.gui_widgets['info_card'], {
            'position': (48, 88),
            'width': 124,
            'type': 'subtitle',
            'align': 'left',
            'labels': ('Ancho X Alto', 'Width X Height'),
            'language': self.language_value } )
        
        self.gui_widgets['total_frames_icon'] = MD3Label(self.gui_widgets['info_card'], {
            'position': (8, 112),
            'type': 'icon',
            'icon': 'number',
            'theme_color': self.theme_color } )

        self.gui_widgets['total_frames_value'] = MD3Label(self.gui_widgets['info_card'], {
            'position': (48, 120),
            'width': 124,
            'type': 'subtitle',
            'align': 'left',
            'labels': ('Total de Cuadros', 'Total Frames'),
            'language': self.language_value } )

        self.gui_widgets['fps_icon'] = MD3Label(self.gui_widgets['info_card'], {
            'position': (8, 144),
            'type': 'icon',
            'icon': 'fps',
            'theme_color': self.theme_color } )

        self.gui_widgets['fps_value'] = MD3Label(self.gui_widgets['info_card'], {
            'position': (48, 152),
            'width': 124,
            'type': 'subtitle',
            'align': 'left',
            'labels': ('CPS', 'FPS'),
            'language': self.language_value } )

        # ------------
        # Card Classes
        # ------------
        self.gui_widgets['classes_card'] = MD3Card(parent, {
            'position': (8, 344), 
            'size': (180, 288),
            'type': 'outlined',
            'titles': ('Clases', 'Classes'),
            'language': self.language_value } )
        
        self.gui_widgets['person_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
            'position': (8, 48),
            'width': 120,
            'labels': ('Persona', 'Person'),
            'icon': 'person',
            'state': False,
            'theme_color': self.theme_color,
            'language': self.language_value,
            'clicked': parent.on_person_chip_clicked } )
        
        self.gui_widgets['bicycle_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
            'position': (8, 88),
            'width': 120,
            'labels': ('Bicicleta', 'Bicycle'),
            'icon': 'bicycle',
            'state': False,
            'theme_color': self.theme_color,
            'language': self.language_value,
            'clicked': parent.on_bicycle_chip_clicked } )

        self.gui_widgets['car_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
            'position': (8, 128),
            'width': 120,
            'labels': ('Carro', 'Car'),
            'icon': 'car',
            'state': False,
            'theme_color': self.theme_color,
            'language': self.language_value,
            'clicked': parent.on_car_chip_clicked } )
        
        self.gui_widgets['motorcycle_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
            'position': (8, 168),
            'width': 120,
            'labels': ('Motocicleta', 'Motorcycle'),
            'icon': 'motorcycle',
            'state': False,
            'theme_color': self.theme_color,
            'language': self.language_value,
            'clicked': parent.on_motorcycle_chip_clicked } )

        self.gui_widgets['bus_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
            'position': (8, 208),
            'width': 120,
            'labels': ('Bus', 'Bus'),
            'icon': 'bus',
            'state': False,
            'theme_color': self.theme_color,
            'language': self.language_value,
            'clicked': parent.on_bus_chip_clicked } )
        
        self.gui_widgets['truck_chip'] = MD3Chip(self.gui_widgets['classes_card'], {
            'position': (8, 248),
            'width': 120,
            'labels': ('Camión', 'Truck'),
            'icon': 'truck',
            'state': False,
            'theme_color': self.theme_color,
            'language': self.language_value,
            'clicked': parent.on_truck_chip_clicked } )

        # ------------------
        # Card Video Toolbar
        # ------------------
        self.gui_widgets['video_toolbar_card'] = MD3Card(parent, {
            'position': (196, 64),
            'type': 'outlined',
            'language': self.language_value } )

        self.gui_widgets['backFrame_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'position': (8, 20),
            'type': 'filled',
            'icon': 'step_backward', 
            'enabled': True,
            'theme_color': self.theme_color,
            'clicked': parent.on_backFrame_button_clicked } )

        self.gui_widgets['reverse_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'position': (48, 20),
            'type': 'filled',
            'icon': 'reverse', 
            'enabled': True,
            'theme_color': self.theme_color,
            'clicked': parent.on_reverse_button_clicked } )

        self.gui_widgets['pause_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'position': (88, 20),
            'type': 'filled',
            'icon': 'pause', 
            'enabled': True,
            'theme_color': self.theme_color,
            'clicked': parent.on_pause_button_clicked } )

        self.gui_widgets['play_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'position': (128, 20),
            'type': 'filled',
            'icon': 'play', 
            'enabled': True,
            'theme_color': self.theme_color,
            'clicked': parent.on_play_button_clicked } )

        self.gui_widgets['frontFrame_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'position': (168, 20),
            'type': 'filled',
            'icon': 'step_forward', 
            'enabled': True,
            'theme_color': self.theme_color,
            'clicked': parent.on_frontFrame_button_clicked } )

        self.gui_widgets['video_slider'] = MD3Slider(self.gui_widgets['video_toolbar_card'], {
            'position': (208, 20),
            'range': (0, 1, 10),
            'value': 0,
            'enabled': False,
            'slider_moved': parent.on_video_slider_sliderMoved,
            'slider_released': parent.on_video_slider_sliderReleased } )

        self.gui_widgets['frame_value_textfield'] = MD3TextField(self.gui_widgets['video_toolbar_card'], {
            'width': 100,
            'type': 'outlined',
            'labels': ('Cuadro', 'Frame'),
            'input': 'integer',
            'language': self.language_value,
            'return_pressed': parent.on_frame_value_textfield_returnPressed } )

        # ----------------
        # Card Video Image
        # ----------------
        self.gui_widgets['video_output_card'] = MD3Card(parent, {
            'position': (196, 140),
            'type': 'outlined',
            'titles': ('Salida del Video','Video Output'),
            'language': self.language_value } )
        
        self.gui_widgets['video_label'] = MD3ImageLabel(self.gui_widgets['video_output_card'], {
            'position': (8, 48),
            'scaled_image': True } )