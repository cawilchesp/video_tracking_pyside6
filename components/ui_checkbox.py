from PySide6.QtWidgets import QCheckBox, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

import qtawesome as qta
from themes.colors import light_colors, dark_colors


class UI_CheckBox(QCheckBox):
    """ Check box component """
    def __init__(
        self,
        parent: QWidget,
        state_changed_signal: callable,
        position: tuple[int, int] = (8,8),
        width: int = 40,
        icon_name: str = None,
        texts: tuple[str, str] = None,
        tristate: bool = False,
        state: int = 0,
        enabled: bool = True,
        language: str = 'es'
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Check box top left corner position (x, y)
            width (int): Check box width
            icon_name (str): Icon name
            texts (tuple[str, str]): Check box texts (label_spanish, label_english)
            tristate (bool): Check box tristate option
                Options: True: On, False: Off
            state (bool): Check box toggle State of activation
                Options: True: On, False: Off
            enabled (bool): Check box enabled / disabled
            language (str): App language
                Options: 'es' = Español, 'en' = English
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(width, 40)
        self.setTristate(tristate)
        self.setEnabled(enabled)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.icon_name = icon_name
        self.texts = texts
        self.state = state

        self.set_language(language)
        self.set_icon(self.theme_style)
        self.setCheckState(Qt.CheckState(self.state))

        self.stateChanged.connect(state_changed_signal)

    def set_icon(self, state: bool) -> None:
        """ Set button state and corresponding icon """
        if self.icon_name is not None:
            h, s, l = light_colors['@text_active'] if state else dark_colors['@text_active']
            icon = qta.icon(f"mdi6.{self.icon_name}", color=QColor.fromHslF(h/360, s/100, l/100))
            self.setIcon(icon)
    
    def set_language(self, language: str) -> None:
        """ Change language of button text """
        if self.texts is not None:
            if language == 'es': self.setText(self.texts[0])
            elif language == 'en': self.setText(self.texts[1])