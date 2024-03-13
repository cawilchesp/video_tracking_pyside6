from PySide6.QtWidgets import QDialog

from dialogs.about_app_ui import AboutAppUI
from themes.colors import dark_colors, light_colors, theme_colors, icons

import yaml


# ----------------
# About App Dialog
# ----------------
class AboutApp(QDialog):
    def __init__(self):
        """ About Me Dialog """
        super().__init__()

        # --------
        # Settings
        # --------
        with open('settings.yaml', 'r') as file:
            self.config = yaml.safe_load(file)

        self.theme_style = self.config['THEME_STYLE']
        self.theme_color = self.config['THEME_COLOR']

        # ----------------
        # Generación de UI
        # ----------------
        self.ui = AboutAppUI(self)

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


    def on_ok_button_clicked(self):
        """ Close dialog """
        self.close()