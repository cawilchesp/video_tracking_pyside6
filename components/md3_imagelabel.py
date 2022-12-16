"""
PyQt Video label component adapted to follow Material Design 3 guidelines


"""

from PyQt6 import QtGui, QtWidgets, QtCore
from PyQt6.QtCore import Qt

import sys


light = {
    'background': '#3785F5',
    'on_background': '#000000',
    'surface': '#FFFFFF',
    'on_surface': '#000000',
    'primary': '#3785F5',
    'on_primary': '#000000',
    'secondary': '#7FB0F5',
    'on_secondary': '#000000',
    'disable': '#B2B2B2',
    'on_disable': '#000000',
    'error': '#B3261E',
    'on_error': '#FFB4AB'
}

dark = {
    'background': '#3B4253',
    'on_background': '#E5E9F0',
    'surface': '#2E3441',
    'on_surface': '#E5E9F0',
    'primary': '#7FB0F5',
    'on_primary': '#000000',
    'secondary': '#3785F5',
    'on_secondary': '#000000',
    'disable': '#B2B2B2',
    'on_disable': '#000000',
    'error': 'B3261E',
    'on_error': '#FFB4AB'
}

current_path = sys.path[0].replace("\\","/")
images_path = f'{current_path}/icons'

# ------
# Labels
# ------
class MD3ImageLabel(QtWidgets.QLabel):
    def __init__(self, parent, attributes: dict) -> None:
        """ Material Design 3 Component: Label

        Parameters
        ----------
        attributes: dict
            name: str
                Widget name
            position: tuple
                Card position
                (x, y) -> x, y: upper left corner
            width: tuple
                Card width
            theme: bool
                App theme ('item', 'value', 'icon', 'field')
                True: Light theme, False: Dark theme
        
        Returns
        -------
        None
        """
        super(MD3ImageLabel, self).__init__(parent)

        self.attributes = attributes

        self.name = attributes['name']
        self.setObjectName(self.name)

        x, y = attributes['position'] if 'position' in attributes else (8,8)
        w = attributes['width'] if 'width' in attributes else 32
        self.setGeometry(x, y, w, 32)
        
        self.setFrameStyle(QtWidgets.QFrame.Shape.Box)

        self.apply_styleSheet(attributes['theme'])
    

    def apply_styleSheet(self, theme: bool) -> None:
        """ Apply theme style sheet to component """
        if 'icon' in self.attributes:
            if theme: self.setPixmap(QtGui.QIcon(f'{images_path}/{self.attributes["icon"]}_L.png').pixmap(24))
            else: self.setPixmap(QtGui.QIcon(f'{images_path}/{self.attributes["icon"]}_D.png').pixmap(24))

        if theme:
            background_color = light["surface"]
            color = light["on_surface"]
        else:
            background_color = dark["surface"]
            color = dark["on_surface"]
        
        self.setStyleSheet(f'QLabel#{self.name} {{ '
                f'border: 1px solid {color};'
                f'background-color: {background_color};'
                f'}}' )


    def language_text(self, language: int) -> None:
        """ Change language of title text """
        return 0
