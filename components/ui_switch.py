from PySide6.QtWidgets import QFrame, QToolButton, QWidget
from PySide6.QtGui import QColor, QIcon

import qtawesome as qta
from themes.colors import light_colors, dark_colors

class UI_Switch(QFrame):
    """
    PySide6 Switch component
    """
    def __init__(self,
        parent: QWidget,
        clicked_signal: callable,
        position: tuple[int, int] = (8,8),
        state: bool = False,
        enabled: bool = True,
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            clicked_signal (callable): Button 'clicked' method name
            position (tuple[int, int]): Button top left corner position (x, y)
            state (bool): State of activation
                Options: True: On, False: Off
            enabled (bool): Button enabled / disabled
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(40, 20)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.state = state

        self.left_switch = QToolButton(self)
        self.left_switch.setGeometry(0, 0, 20, 20)
        self.left_switch.setCheckable(True)
        self.left_switch.setEnabled(enabled)

        self.right_switch = QToolButton(self)
        self.right_switch.setGeometry(20, 0, 20, 20)
        self.right_switch.setCheckable(True)
        self.right_switch.setEnabled(enabled)

        self.left_switch.setProperty('side', 'left')
        self.right_switch.setProperty('side', 'right')
        self.set_state(self.theme_style, self.state)

        self.left_switch.clicked.connect(clicked_signal)
        self.right_switch.clicked.connect(clicked_signal)
        
    def set_state(self, style: bool, state: bool) -> None:
        """ Set button state and corresponding icon """
        self.left_switch.setChecked(state)
        self.right_switch.setChecked(state)

        switch_states = {
            False: (light_colors['@text_active'], dark_colors['@text_active']),
            True: (light_colors['@background_full'], dark_colors['@background_full']),
        }
        h, s, l = switch_states[self.state][0] if style else switch_states[self.state][1]
        icon = qta.icon('mdi6.circle', color=QColor.fromHslF(h/360, s/100, l/100))
        if state:
            self.left_switch.setIcon(QIcon("icons/none.png"))
            self.right_switch.setIcon(icon)
        else:
            self.left_switch.setIcon(icon)
            self.right_switch.setIcon(QIcon("icons/none.png"))