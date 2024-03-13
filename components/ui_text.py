from PySide6.QtWidgets import QLineEdit, QWidget
from PySide6.QtGui import QFont, QIcon, QRegularExpressionValidator, QColor
from PySide6.QtCore import QRegularExpression

import qtawesome as qta
from themes.colors import light_colors, dark_colors


class UI_TextBox(QLineEdit):
    """ Text Box component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8, 8),
        width: int = 64,
        placeholder_texts: tuple[str, str] = None,
        input: str = None,
        max_length: int = 32767,
        enabled: bool = True,
        language: str = 'es',
        text_edited_signal: callable = None,
        return_pressed_signal: callable = None
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Text box top left corner position (x, y)
            width (int): Text box width
            placeholder_texts (tuple[str, str]): Text box placeholder texts (text_spanish, text_english)
            input (str): Characters allowed
                Options:
                    'alphabet': letters and accents
                    'numeric': numbers
                    'alphanumeric': letters and numbers
            max_length (int): Number of characters allowed
            enabled (bool): Text box enabled / disabled
            language (str): App language
                Options: 'es' = Español, 'en' = English
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(width, 40)
        self.setClearButtonEnabled(True)
        self.setMaxLength(max_length)
        self.setFont(QFont('Segoe Fluent Icons', 10))
        self.setEnabled(enabled)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.placeholder_texts = placeholder_texts

        patterns_dict = {
            'alphabet': r"[\p{L}\s]+",
            'numeric': r"[+-]?\d+",
            'alphanumeric': r"[\p{L}\s\d]+"
        }
        if input is not None:
            input_pattern = patterns_dict[input]
            reg_exp = QRegularExpressionValidator(QRegularExpression(input_pattern))
            self.setValidator(reg_exp)

        self.set_language(language) if self.placeholder_texts is not None else None

        self.textEdited.connect(text_edited_signal)
        self.returnPressed.connect(return_pressed_signal)

    def set_language(self, language: str) -> None:
        """ Change language of button label """
        if language == 'es':   self.setPlaceholderText(self.placeholder_texts[0])
        elif language == 'en': self.setPlaceholderText(self.placeholder_texts[1])


class UI_PasswordBox(QLineEdit):
    """ Password Box component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8, 8),
        width: int = 64,
        max_length: int = 32767,
        enabled: bool = True,
        language: str = 'es'
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Password box top left corner position (x, y)
            width (int): Password box width
            max_length (int): Number of characters allowed
            enabled (bool): Password box enabled / disabled
            language (str): App language
                Options: 'es' = Español, 'en' = English
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(width, 40)
        self.setClearButtonEnabled(True)
        self.setMaxLength(max_length)
        self.setEnabled(enabled)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.placeholder_texts = ('Ingrese la contraseña', 'Enter your password')

        self.password_visible = False
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self.toggle_password = self.addAction(QIcon('icons/none.png'), QLineEdit.ActionPosition.TrailingPosition)
        self.toggle_password.triggered.connect(self.password_action)
        self.set_icon(self.theme_style)

        self.set_language(language) if self.placeholder_texts is not None else None

    def set_icon(self, style: bool) -> None:
        """ Change button icon """
        h, s, l = light_colors['@text_active'] if style else dark_colors['@text_active']
        self.visible_icon = qta.icon('mdi6.eye-outline', color=QColor.fromHslF(h/360, s/100, l/100))
        self.hidden_icon = qta.icon('mdi6.eye-off-outline', color=QColor.fromHslF(h/360, s/100, l/100))
        if self.password_visible:
            self.toggle_password.setIcon(self.visible_icon)
        else:
            self.toggle_password.setIcon(self.hidden_icon)

    def password_action(self) -> None:
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password.setIcon(self.visible_icon)
        else:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password.setIcon(self.hidden_icon)

    def set_language(self, language: str) -> None:
        """ Change language of button label """
        if language == 'es':   self.setPlaceholderText(self.placeholder_texts[0])
        elif language == 'en': self.setPlaceholderText(self.placeholder_texts[1])


class UI_EmailBox(QLineEdit):
    """ Email Box component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8, 8),
        width: int = 64,
        max_length: int = 32767,
        enabled: bool = True,
        language: str = 'es'
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Text box top left corner position (x, y)
            width (int): Text box width
            max_length (int): Number of characters allowed
            enabled (bool): Text box enabled / disabled
            language (str): App language
                Options: 'es' = Español, 'en' = English
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(width, 40)
        self.setClearButtonEnabled(True)
        self.setMaxLength(max_length)
        self.setEnabled(enabled)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.placeholder_texts = ('Correo electrónico', 'E-mail')

        input_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        reg_exp = QRegularExpressionValidator(QRegularExpression(input_pattern))
        self.setValidator(reg_exp)

        self.set_language(language) if self.placeholder_texts is not None else None

    def set_language(self, language: str) -> None:
        """ Change language of button label """
        if language == 'es':   self.setPlaceholderText(self.placeholder_texts[0])
        elif language == 'en': self.setPlaceholderText(self.placeholder_texts[1])


class UI_IpAddressBox(QLineEdit):
    """ IP Address Box component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8, 8),
        width: int = 64,
        max_length: int = 32767,
        enabled: bool = True,
        language: str = 'es'
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Text box top left corner position (x, y)
            width (int): Text box width
            max_length (int): Number of characters allowed
            enabled (bool): Text box enabled / disabled
            language (str): App language
                Options: 'es' = Español, 'en' = English
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(width, 40)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.setClearButtonEnabled(True)
        self.setMaxLength(max_length)
        self.setEnabled(enabled)
        self.setInputMask('000.000.000.000')
        self.setText('0.0.0.0')

        input_pattern = r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        reg_exp = QRegularExpressionValidator(QRegularExpression(input_pattern))
        self.setValidator(reg_exp)