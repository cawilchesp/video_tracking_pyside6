"""
PySide6 Icon Button component adapted to follow Material Design 3 guidelines

"""
from PySide6.QtWidgets import QToolButton
from PySide6.QtCore import Qt

from icon_color import icon_color

# -----------
# Icon Button
# -----------
class MD3IconButton(QToolButton):
    def __init__(self, parent, attributes: dict) -> None:
        """ Material Design 3 Component: Icon Button

        Parameters
        ----------
        attributes: dict
            position: tuple
                Icon button top left corner position
                (x, y)
            type: str
                Icon button type
                'filled', 'tonal', 'outlined', 'standard'
            icon: str
                Icon name
            enabled: bool
                Icon button enabled / disabled
            theme_color: str
                App theme color name
            clicked: def
                Icon button 'clicked' method name
        
        Returns
        -------
        None
        """
        super(MD3IconButton, self).__init__(parent)

        self.parent = parent
        self.attributes = attributes
        x, y = attributes['position'] if 'position' in attributes else (8,8)
        self.setGeometry(x, y, 32, 32)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setAutoRaise(True)
        self.setEnabled(attributes['enabled']) if 'enabled' in attributes else True

        self.set_icon(attributes['theme_color'], attributes['icon'])
        self.setProperty(attributes['type'], True)

        self.clicked.connect(attributes['clicked'])

    
    def set_icon(self, color_name: str, icon_name: str):
        if self.attributes['type'] in ['filled', 'tonal']:
            color = 'black'
        elif self.attributes['type'] in ['outlined', 'standard']:
            color = color_name
        colorized_icon = icon_color(color, icon_name)
        self.setIcon(colorized_icon)