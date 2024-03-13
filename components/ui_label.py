from PySide6.QtWidgets import QLabel, QWidget, QFrame
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt

import qtawesome as qta
from themes.colors import light_colors, dark_colors


class UI_Label(QLabel):
    """ Label component """
    def __init__(
        self,
        parent: QWidget,
        texts: tuple[str, str],
        position: tuple[int, int] = (16, 16),
        width: int = 40,
        align: str = 'left',
        border_color: str = None,
        font_size: int = 9,
        language: str = 'es'
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            texts (tuple[str, str]): Label texts (text_spanish, text_english)
            position (tuple[int, int]): Label top left corner position (x, y)
            width (int): Label width
            align (str): Label text alignment
                Options: 'center', 'left', 'right'
            border_color (str): Label border color in hexadecimal format: '#RRGGBB'
            font_size (int): Label font size
            language (str): App language
                Options: 'es' = Español, 'en' = English
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        # self.resize(width, 40)
        self.setContentsMargins(0,0,0,0)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.texts = texts

        if font_size < 8: font_size = 8
        elif font_size > 24: font_size = 24
        self.setFont(QFont('Segoe Fluent Icons', font_size))

        alignment_dict = {
            'left': Qt.AlignmentFlag.AlignLeft,
            'center': Qt.AlignmentFlag.AlignHCenter,
            'right': Qt.AlignmentFlag.AlignRight
        }
        label_H_alignment = alignment_dict[align]
        self.setAlignment(label_H_alignment | Qt.AlignmentFlag.AlignBottom)
        
        if border_color is not None:
            self.setStyleSheet(f"UI_Label {{ border-width: 2px; border-color: {border_color} }}")

        self.set_language(language)
        
    def set_language(self, language: int) -> None:
        """ Change language of label text """
        if language == 'es':   self.setText(self.texts[0])
        elif language == 'en': self.setText(self.texts[1])
        


class UI_IconLabel(QLabel):
    """ Icon Label component """
    def __init__(
        self,
        parent: QWidget,
        icon_name: str,
        position: tuple[int, int] = (16, 16),
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Label top left corner position (x, y)
            icon_name (str): Icon name
            theme_color (str): App theme color name
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(32, 32)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.icon_name = icon_name
        
        self.set_icon(self.theme_style)
        
    def set_icon(self, style: bool) -> None:
        """ Update icon corresponding to the theme """
        h, s, l = light_colors['@text_active'] if style else dark_colors['@text_active']
        icon = qta.icon(f"mdi6.{self.icon_name}", color=QColor.fromHslF(h/360, s/100, l/100))
        self.setPixmap(icon.pixmap(24))


class UI_ColorLabel(QLabel):
    """ Color Label component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (16, 16),
        width: int = 32,
        color: str = '#FFFFFF'
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Label top left corner position (x, y)
            width (int): Color Label width
            color (str): Color Label indicator color in hexadecimal format: '#RRGGBB'
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(width, 32)

        self.set_color_label(color)

    def set_color_label(self, color: str) -> None:
        """ Apply custom background color to label indicator """
        self.setStyleSheet(f"UI_ColorLabel {{ background-color: {color} }}")


class UI_ImageLabel(QLabel):
    """ Image Label component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8,8),
        size: tuple[int, int] = (96,96),
        scaled_image: bool = True,
    ):
        """
        Parameters
        ----------
            position (tuple[int, int]): Image label top left corner position (x, y)
            size (tuple[int, int]): Image label size (width, height)
            scaled_image (bool): Scale image to fit to label
                Options: True: Fit, False: Original size
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(size[0], size[1])

        self.setScaledContents(scaled_image)
        self.setFrameStyle(QFrame.Shape.Box)