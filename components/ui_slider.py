from PySide6.QtWidgets import QSlider, QWidget
from PySide6.QtCore import Qt


class UI_Slider(QSlider):
    """ Slider component """
    def __init__(
        self,
        parent: QWidget,
        slider_moved_signal: callable,
        slider_released_signal: callable,
        position: tuple[int, int] = (8,8),
        length: int = 64,
        orientation: str = 'horizontal',
        range: tuple[int, int, int] = (0, 1, 100),
        value: int = 0,
        enabled: bool = True
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            slider_moved_signal (callable): Slider 'moved' method name
            slider_released_signal (callable): Slider 'released' method name
            position (tuple[int, int]): Slider top left corner position (x, y)
            length (int): Slider length
            orientation (str): Slider orientation
                Options: 'horizontal', 'vertical'
            range (tuple[int, int, int]): Slider range (min, step, max)
            value (int): Slider current value
            enabled (bool): Button enabled / disabled
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        if orientation == 'horizontal':
            self.resize(length, 40)
            self.setOrientation(Qt.Orientation.Horizontal)
        elif orientation == 'vertical':
            self.resize(40, length)
            self.setOrientation(Qt.Orientation.Vertical)

        self.setMinimum(range[0])
        self.setSingleStep(range[1])
        self.setMaximum(range[2])
        self.setValue(value)
        self.setEnabled(enabled)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color

        self.sliderMoved.connect(slider_moved_signal)
        self.sliderReleased.connect(slider_released_signal)