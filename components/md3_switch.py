"""
PySide6 Icon Button component adapted to follow Material Design 3 guidelines

"""
from PySide6.QtWidgets import QToolButton
from PySide6.QtCore import Qt, QSize

from icon_color import icon_color

# ------
# Switch
# ------
class MD3Switch(QToolButton):
    def __init__(self, parent, attributes: dict) -> None:
        """ Material Design 3 Component: Switch

        Parameters
        ----------
        attributes: dict
            position: tuple
                Button top left corner position
                (x, y)
            side: str
                Switch button side
                'left', 'right'
            state: bool
                State of activation
                True: On, False: Off
            enabled: bool
                Switch enabled / disabled
            theme_color: str
                App theme color name
            clicked: def
                Switch 'clicked' method name
        
        Returns
        -------
        None
        """
        super(MD3Switch, self).__init__(parent)

        self.attributes = attributes
        self.parent = parent

        x, y = attributes['position'] if 'position' in attributes else (0, 0)
        self.setGeometry(x, y, 26, 32)

        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setCheckable(True)
        self.setEnabled(attributes['enabled']) if 'enabled' in attributes else True

        self.setProperty(attributes['side'], True)
        self.set_state(attributes['state'], attributes['theme_color'])

        self.clicked.connect(attributes['clicked'])
        

    def set_state(self, state: bool, color_name: str) -> None:
        """ Set button state and corresponding icon """
        
        self.setChecked(state)
        icon_state = {
            True: { 'left': 'none', 'right': 'circle_checked' },
            False: { 'left': 'circle', 'right': 'none' }
        }
        icon_name = icon_state[state][self.attributes['side']]
        color = 'black' if state else color_name
        colorized_icon = icon_color(color, icon_name)
        self.setIcon(colorized_icon)
        self.setIconSize(QSize(16,16))