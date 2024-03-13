from PySide6.QtWidgets import QDialog

from components.ui_window import UI_Window
from components.ui_card import UI_Card
from components.ui_label import UI_Label, UI_IconLabel
from components.ui_button import UI_Button

import yaml


class AboutAppUI(QDialog):
    def __init__(self, parent):
        """ About Me Dialog """
        super(AboutAppUI, self).__init__(parent)

        # --------
        # Settings
        # --------
        self.settings_file = 'settings.yaml'
        with open(self.settings_file, 'r') as file:
            self.config = yaml.safe_load(file)

        self.language_value = self.config['LANGUAGE']
        self.theme_style = self.config['THEME_STYLE']
        self.theme_color = self.config['THEME_COLOR']

        self.aboutapp_widgets = {}

        # -------------
        # Dialog Window
        # -------------
        (width, height) = (320, 408)
        self.aboutapp_widgets['main_window'] = UI_Window(
            parent=parent, 
            size=(width, height),
            minimum_size=(width, height),
            maximum_size=(width, height),
            titles=('Acerca de...','About...'),
            language=self.language_value
        )

        # -----------
        # Card Dialog
        # -----------
        self.aboutapp_widgets['aboutapp_dialog_card'] = UI_Card(
            parent=parent,
            position=(16, 16),
            size=(width-32, height-32)
        )

        self.aboutapp_widgets['aboutapp_dialog_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(8, 8),
            width=width - 48,
            align='left',
            font_size=16,
            texts=('Extracción de Señales', 'Signal Extraction'),
            language=self.language_value
        )

        self.aboutapp_widgets['version_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(8, 48),
            width=width - 48,
            align='left',
            texts=('Versión: 1.0', 'Version: 1.0'),
            language=self.language_value
        )

        self.aboutapp_widgets['developed_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(8, 80),
            width=width - 48,
            align='left',
            texts=('Desarrollado por:', 'Developed by:'),
            language=self.language_value
        )
        
        self.aboutapp_widgets['name_icon'] = UI_IconLabel(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(8, 112),
            icon_name='account'
        )

        self.aboutapp_widgets['name_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(48, 112), 
            width=width - 88,
            align='left',
            texts=('Carlos Andrés Wilches Pérez', 'Carlos Andrés Wilches Pérez'),
            language=self.language_value
        )

        self.aboutapp_widgets['profession_icon'] = UI_IconLabel(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(8, 144),
            icon_name='school'
        )

        self.aboutapp_widgets['profession1_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(48, 144), 
            width=width - 88,
            align='left',
            texts=('Ingeniero Electrónico, BSc. MSc. PhD.', 'Electronic Engineer, BSc. MSc. PhD.'),
            language=self.language_value
        )

        self.aboutapp_widgets['profession_2_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(48, 176), 
            width=width - 88,
            align='left',
            texts=('Universidad Nacional de Colombia', 'Nacional University of Colombia'),
            language=self.language_value
        )

        self.aboutapp_widgets['profession_3_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(48, 208), 
            width=width - 88,
            align='left',
            texts=('Maestría en Ingeniería Electrónica', 'Master in Electronic Engineering'),
            language=self.language_value
        )

        self.aboutapp_widgets['profession_4_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(48, 240), 
            width=width - 88,
            align='left',
            texts=('Doctor en Ingeniería', 'Doctor in Engineering'),
            language=self.language_value
        )

        self.aboutapp_widgets['profession_5_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(48, 272), 
            width=width - 88,
            align='left',
            texts=('Pontificia Universidad Javeriana', 'Xaverian Pontifical University'),
            language=self.language_value
        )

        self.aboutapp_widgets['email_icon'] = UI_IconLabel(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(8, 304),
            icon_name='email',
        )

        self.aboutapp_widgets['email_label'] = UI_Label(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(48, 304), 
            width=width - 88,
            align='left',
            texts=('cawilchesp@outlook.com', 'cawilchesp@outlook.com'),
            language=self.language_value
        )

        # ---------
        # Button Ok
        # ---------
        self.aboutapp_widgets['ok_button'] = UI_Button(
            parent=self.aboutapp_widgets['aboutapp_dialog_card'],
            position=(width - 136, height - 76),
            width=100,
            type='accent',
            texts=('Aceptar', 'Ok'),
            language=self.language_value,
            clicked_signal=parent.on_ok_button_clicked
        )