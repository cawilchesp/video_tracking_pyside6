from PyQt6 import QtGui, QtWidgets, QtCore
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QSettings, Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

from components.md3_window import MD3Window
from components.md3_card import MD3Card
from components.md3_menu import MD3Menu
from components.md3_iconbutton import MD3IconButton
from components.md3_switch import MD3Switch
from components.md3_label import MD3Label
from components.md3_textfield import MD3TextField
from components.mpl_canvas import MPLCanvas

import sys


class UI(QWidget):
    def __init__(self, parent):
        super(UI, self).__init__(parent)

        # --------
        # Settings
        # --------
        self.settings = QSettings(f'{sys.path[0]}/settings.ini', QSettings.Format.IniFormat)
        self.language_value = int(self.settings.value('language'))
        self.theme_value = eval(self.settings.value('theme'))

        self.regExp1 = QRegularExpressionValidator(QRegularExpression('[0-9]{1,7}'), self)

        self.idioma_dict = {0: ('ESP', 'SPA'), 1: ('ING', 'ENG')}

        self.source_options = {
            0: ('Webcam', 'Webcam'),
            1: ('Cámara IP', 'IP Camera'),
            2: ('Archivo de Video', 'Video File')
        }

        self.gui_widgets = {}

        # -----------
        # Main Window
        # -----------
        (width, height) = (1300, 700)
        self.gui_widgets['main_window'] = MD3Window( {
            'parent': parent, 
            'size': (width, height),
            'labels': ('Seguidor de Objetos en Video', 'Video Object Tracker'),
            'theme': self.theme_value, 
            'language': self.language_value } )

        # -----------
        # Card Título
        # -----------
        self.gui_widgets['titulo_card'] = MD3Card(parent, {
            'name': 'titulo_card',
            'position': (8, 8), 
            'size': (width-16, 48), 
            'theme': self.theme_value } )


        # Espacio para título de la aplicación, logo, etc.

        
        self.gui_widgets['idioma_menu'] = MD3Menu(self.gui_widgets['titulo_card'], {
            'name': 'idioma_menu',
            'size': (72, 32),
            'options': self.idioma_dict,
            'language': self.language_value,
            'theme': self.theme_value } )
        self.gui_widgets['idioma_menu'].setCurrentIndex(self.language_value)
        self.gui_widgets['idioma_menu'].currentIndexChanged.connect(parent.on_idioma_menu_currentIndexChanged)

        self.gui_widgets['tema_switch_light'] = MD3Switch(self.gui_widgets['titulo_card'], {
            'name': 'tema_switch_light',
            'side': 'left',
            'icons': ('light_mode_L.png', 'none.png'),
            'state': self.theme_value,
            'language': self.language_value,
            'theme': self.theme_value } )
        self.gui_widgets['tema_switch_light'].clicked.connect(parent.on_tema_switch_light_clicked)

        self.gui_widgets['tema_switch_dark'] = MD3Switch(self.gui_widgets['titulo_card'], {
            'name': 'tema_switch_dark',
            'side': 'right',
            'icons': ('dark_mode_L.png', 'none.png'),
            'state': not self.theme_value,
            'language': self.language_value,
            'theme': self.theme_value } )
        self.gui_widgets['tema_switch_dark'].clicked.connect(parent.on_tema_switch_dark_clicked)

        self.gui_widgets['database_button'] = MD3IconButton(self.gui_widgets['titulo_card'], {
            'name': 'database_button',
            'type': 'filled',
            'icon': 'database', 
            'theme': self.theme_value } )
        # self.database_button.clicked.connect(self.on_database_button_clicked)

        self.gui_widgets['manual_button'] = MD3IconButton(self.gui_widgets['titulo_card'], {
            'name': 'manual_button',
            'type': 'filled',
            'icon': 'help', 
            'theme': self.theme_value } )
        # self.manual_button.clicked.connect(self.on_manual_button_clicked)

        self.gui_widgets['about_button'] = MD3IconButton(self.gui_widgets['titulo_card'], {
            'name': 'about_button',
            'type': 'filled',
            'icon': 'mail', 
            'theme': self.theme_value } )
        self.gui_widgets['about_button'].clicked.connect(parent.on_about_button_clicked)

        self.gui_widgets['aboutQt_button'] = MD3IconButton(self.gui_widgets['titulo_card'], {
            'name': 'aboutQt_button',
            'type': 'filled',
            'icon': 'about_qt', 
            'theme': self.theme_value } )
        self.gui_widgets['aboutQt_button'].clicked.connect(parent.on_aboutQt_button_clicked)

        # -----------
        # Card Source
        # -----------
        self.gui_widgets['source_card'] = MD3Card(parent, { 
            'name': 'source_card',
            'position': (8, 64), 
            'size': (180, 128), 
            'theme': self.theme_value, 
            'labels': ('Origen del Video', 'Video Source'), 
            'language': self.language_value } )

        self.gui_widgets['source_menu'] = MD3Menu(self.gui_widgets['source_card'], {
            'name': 'source_menu',
            'position': (8, 48),
            'size': (164, 32),
            'options': self.source_options,
            'language': self.language_value,
            'theme': self.theme_value } )
        self.gui_widgets['source_menu'].textActivated.connect(parent.on_source_menu_textActivated)

        self.gui_widgets['source_add_button'] = MD3IconButton(self.gui_widgets['source_card'], {
            'name': 'source_add_button',
            'type': 'filled',
            'position': (140, 88),
            'icon': 'new', 
            'theme': self.theme_value } )
        self.gui_widgets['source_add_button'].setEnabled(False)
        self.gui_widgets['source_add_button'].clicked.connect(parent.on_source_add_button_clicked)

        # ----------------
        # Card Information
        # ----------------
        self.gui_widgets['info_card'] = MD3Card(parent, { 
            'name': 'info_card',
            'position': (8, 200), 
            'size': (180, 216), 
            'theme': self.theme_value, 
            'labels': ('Información', 'Information'), 
            'language': self.language_value } )

        self.gui_widgets['source_icon'] = MD3Label(self.gui_widgets['info_card'], {
            'name': 'id_icon', 
            'position': (8, 48),
            'type': 'icon',
            'icon': 'cam',
            'theme': self.theme_value } )

        self.gui_widgets['source_value'] = MD3Label(self.gui_widgets['info_card'], {
            'name': 'source_value',
            'position': (48, 56),
            'width': 124,
            'type': 'subtitle',
            'labels': ('Origen', 'Source'),
            'theme': self.theme_value,
            'language': self.language_value } )
        
        self.gui_widgets['filename_value'] = MD3Label(self.gui_widgets['info_card'], {
            'name': 'filename_value', 
            'position': (48, 88), 
            'width': 124,
            'type': 'subtitle',
            'labels': ('Nombre del archivo', 'File Name'),
            'theme': self.theme_value,
            'language': self.language_value } )

        self.gui_widgets['width_icon'] = MD3Label(self.gui_widgets['info_card'], {
            'name': 'width_icon', 
            'position': (8, 112),
            'type': 'icon',
            'icon': 'width',
            'theme': self.theme_value } )

        self.gui_widgets['width_value'] = MD3Label(self.gui_widgets['info_card'], {
            'name': 'width_value',
            'position': (48, 120),
            'width': 124,
            'type': 'subtitle',
            'labels': ('Ancho', 'Width'),
            'theme': self.theme_value,
            'language': self.language_value } )
        
        self.gui_widgets['height_icon'] = MD3Label(self.gui_widgets['info_card'], {
            'name': 'height_icon',
            'position': (8, 144),
            'type': 'icon',
            'icon': 'height',
            'theme': self.theme_value } )

        self.gui_widgets['height_value'] = MD3Label(self.gui_widgets['info_card'], {
            'name': 'height_value', 
            'position': (48, 152), 
            'width': 124,
            'type': 'subtitle',
            'labels': ('Alto', 'Height'),
            'theme': self.theme_value,
            'language': self.language_value } )

        self.gui_widgets['fps_icon'] = MD3Label(self.gui_widgets['info_card'], {
            'name': 'fps_icon', 
            'position': (8, 176),
            'type': 'icon',
            'icon': 'fps',
            'theme': self.theme_value } )

        self.gui_widgets['fps_value'] = MD3Label(self.gui_widgets['info_card'], {
            'name': 'fps_value', 
            'position': (48, 184), 
            'width': 124,
            'type': 'subtitle',
            'labels': ('CPS', 'FPS'),
            'theme': self.theme_value,
            'language': self.language_value } )

        # ------------
        # Card Classes
        # ------------
        self.gui_widgets['classes_card'] = MD3Card(parent, { 
            'name': 'classes_card',
            'position': (8, 424), 
            'size': (180, 128), 
            'theme': self.theme_value, 
            'labels': ('Anotaciones', 'Annotations'), 
            'language': self.language_value } )

        self.gui_widgets['classes_menu'] = MD3Menu(self.gui_widgets['classes_card'], {
            'name': 'classes_menu',
            'position': (8, 48),
            'size': (164, 32),
            'options': self.source_options,
            'language': self.language_value,
            'theme': self.theme_value } )
        self.gui_widgets['classes_menu'].textActivated.connect(parent.on_classes_menu_textActivated)

        self.gui_widgets['color_button'] = MD3IconButton(self.gui_widgets['classes_card'], {
            'name': 'color_button',
            'type': 'filled',
            'position': (140, 88),
            'icon': 'new', 
            'theme': self.theme_value } )
        self.gui_widgets['color_button'].setEnabled(False)
        self.gui_widgets['color_button'].clicked.connect(parent.on_color_button_clicked)

        # ------------------
        # Card Video Toolbar
        # ------------------
        self.gui_widgets['video_toolbar_card'] = MD3Card(parent, {
            'name': 'video_toolbar_card',
            'position': (196, 64), 
            'size': (width-204, 72),
            'theme': self.theme_value } )

        self.gui_widgets['slow_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'name': 'slow_button',
            'type': 'filled',
            'position': (8, 20),
            'icon': 'rewind', 
            'theme': self.theme_value } )
        self.gui_widgets['slow_button'].setEnabled(False)
        self.gui_widgets['slow_button'].clicked.connect(parent.on_slow_button_clicked)

        self.gui_widgets['backFrame_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'name': 'backFrame_button',
            'type': 'filled',
            'position': (48, 20),
            'icon': 'step_backward', 
            'theme': self.theme_value } )
        self.gui_widgets['backFrame_button'].setEnabled(False)
        self.gui_widgets['backFrame_button'].clicked.connect(parent.on_backFrame_button_clicked)

        self.gui_widgets['reverse_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'name': 'reverse_button',
            'type': 'filled',
            'position': (88, 20),
            'icon': 'reverse', 
            'theme': self.theme_value } )
        self.gui_widgets['reverse_button'].setEnabled(False)
        self.gui_widgets['reverse_button'].clicked.connect(parent.on_reverse_button_clicked)

        self.gui_widgets['pause_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'name': 'pause_button',
            'type': 'filled',
            'position': (128, 20),
            'icon': 'pause', 
            'theme': self.theme_value } )
        self.gui_widgets['pause_button'].setEnabled(False)
        self.gui_widgets['pause_button'].clicked.connect(parent.on_pause_button_clicked)

        self.gui_widgets['play_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'name': 'play_button',
            'type': 'filled',
            'position': (168, 20),
            'icon': 'play', 
            'theme': self.theme_value } )
        self.gui_widgets['play_button'].setEnabled(False)
        self.gui_widgets['play_button'].clicked.connect(parent.on_play_button_clicked)

        self.gui_widgets['frontFrame_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'name': 'frontFrame_button',
            'type': 'filled',
            'position': (208, 20),
            'icon': 'step_forward', 
            'theme': self.theme_value } )
        self.gui_widgets['frontFrame_button'].setEnabled(False)
        self.gui_widgets['frontFrame_button'].clicked.connect(parent.on_frontFrame_button_clicked)

        self.gui_widgets['fast_button'] = MD3IconButton(self.gui_widgets['video_toolbar_card'], {
            'name': 'fast_button',
            'type': 'filled',
            'position': (248, 20),
            'icon': 'fast_forward', 
            'theme': self.theme_value } )
        self.gui_widgets['fast_button'].setEnabled(False)
        self.gui_widgets['fast_button'].clicked.connect(parent.on_fast_button_clicked)







        self.gui_widgets['frame_value_text'] = MD3TextField(self.gui_widgets['video_toolbar_card'], {
            'name': 'frame_value_text',
            'position': (self.gui_widgets['video_toolbar_card'].width() - 108, 8),
            'width': 100,
            'labels': ('Cuadro', 'Frame'),
            'regular_expression': self.regExp1,
            'theme': self.theme_value,
            'language': self.language_value } )
        # self.gui_widgets['frame_value_text'].text_field.textEdited.connect(parent.on_frame_value_text_textEdited)


        # ----------------
        # Card Video Image
        # ----------------
        self.gui_widgets['video_output_card'] = MD3Card(parent, { 
            'name': 'video_output_card',
            'theme': self.theme_value, 
            'labels': ('Salida del Video','Video Output'), 
            'language': self.language_value } )
        
     
        



        
        # # ---------------
        # # Card Mesomorphy
        # # ---------------
        # self.gui_widgets['mesomorph_card'] = MD3Card(parent, { 
        #     'name': 'mesomorph_card',
        #     'size': (208, 468), 
        #     'theme': self.theme_value, 
        #     'labels': ('Mesomorfismo', 'Mesomorphy'),
        #     'language': self.language_value } )

        # self.gui_widgets['altura_meso_label'] = MD3Label(self.gui_widgets['mesomorph_card'], {
        #     'name': 'altura_meso_label',
        #     'position': (8, 48),
        #     'width': self.gui_widgets['mesomorph_card'].width() - 16,
        #     'type': 'subtitle',
        #     'labels': ('Altura (cm)', 'Height (cm)'),
        #     'theme': self.theme_value,
        #     'language': self.language_value } )

        # self.gui_widgets['altura_meso_value_label'] = MD3Label(self.gui_widgets['mesomorph_card'], {
        #     'name': 'altura_meso_value_label',
        #     'position': (8, 68),
        #     'width': self.gui_widgets['mesomorph_card'].width() - 16,
        #     'align': 'center',
        #     'type': 'value',
        #     'color': '255, 255, 255' if self.theme_value else '0, 0, 0',
        #     'theme': self.theme_value,
        #     'language': self.language_value } )

        # self.gui_widgets['humero_text'] = MD3TextField(self.gui_widgets['mesomorph_card'], {
        #     'name': 'humero_text',
        #     'position': (8, 108),
        #     'width': self.gui_widgets['mesomorph_card'].width() - 16,
        #     'labels': ('Diámetro Húmero (cm)', 'Humerus Diameter (cm)'),
        #     'regular_expression': self.regExp3,
        #     'theme': self.theme_value,
        #     'language': self.language_value } )
        # # self.gui_widgets['humero_text'].text_field.textEdited.connect(parent.on_humero_text_textEdited)

        # self.gui_widgets['femur_text'] = MD3TextField(self.gui_widgets['mesomorph_card'], {
        #     'name': 'femur_text',
        #     'position': (8, 168),
        #     'width': self.gui_widgets['mesomorph_card'].width() - 16,
        #     'labels': ('Diámetro Fémur (cm)', 'Femur Diameter (cm)'),
        #     'regular_expression': self.regExp3,
        #     'theme': self.theme_value,
        #     'language': self.language_value } )
        # # self.gui_widgets['femur_text'].text_field.textEdited.connect(parent.on_femur_text_textEdited)

        # self.gui_widgets['biceps_text'] = MD3TextField(self.gui_widgets['mesomorph_card'], {
        #     'name': 'biceps_text',
        #     'position': (8, 228),
        #     'width': self.gui_widgets['mesomorph_card'].width() - 16,
        #     'labels': ('Perímetro Bíceps (cm)', 'Biceps Perimeter (cm)'),
        #     'regular_expression': self.regExp3,
        #     'theme': self.theme_value,
        #     'language': self.language_value } )
        # # self.gui_widgets['biceps_text'].text_field.textEdited.connect(parent.on_biceps_text_textEdited)

        # self.gui_widgets['tricipital_text'] = MD3TextField(self.gui_widgets['mesomorph_card'], {
        #     'name': 'tricipital_text',
        #     'position': (8, 288),
        #     'width': self.gui_widgets['mesomorph_card'].width() - 16,
        #     'labels': ('Pliegue Tricipital (cm)', 'Tricipital Fold (cm)'),
        #     'regular_expression': self.regExp3,
        #     'theme': self.theme_value,
        #     'language': self.language_value } )
        # # self.gui_widgets['tricipital_text'].text_field.textEdited.connect(parent.on_tricipital_text_textEdited)

        # self.gui_widgets['pantorrilla_perimetro_text'] = MD3TextField(self.gui_widgets['mesomorph_card'], {
        #     'name': 'pantorrilla_perimetro_text',
        #     'position': (8, 348),
        #     'width': self.gui_widgets['mesomorph_card'].width() - 16,
        #     'labels': ('Perímetro Pantorrilla (cm)', 'Calf Perimeter (cm)'),
        #     'regular_expression': self.regExp3,
        #     'theme': self.theme_value,
        #     'language': self.language_value } )
        # # self.gui_widgets['pantorrilla_perimetro_text'].text_field.textEdited.connect(parent.on_pantorrilla_perimetro_text_textEdited)

        # self.gui_widgets['pantorrilla_pliegue_text'] = MD3TextField(self.gui_widgets['mesomorph_card'], {
        #     'name': 'pantorrilla_pliegue_text',
        #     'position': (8, 408),
        #     'width': self.gui_widgets['mesomorph_card'].width() - 16,
        #     'labels': ('Pliegue Pantorrilla (cm)', 'Calf Fold (cm)'),
        #     'regular_expression': self.regExp3,
        #     'theme': self.theme_value,
        #     'language': self.language_value } )
        # # self.gui_widgets['pantorrilla_pliegue_text'].text_field.textEdited.connect(parent.on_pantorrilla_pliegue_text_textEdited)

        
