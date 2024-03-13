from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QWidget


class UI_NumberBox(QSpinBox):
    """ Number Box component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8, 8),
        width: int = 64,
        range: tuple[int, int, int] = (0, 1, 100),
        value: int = 0,
        enabled: bool = True,
        value_changed_signal: callable = None
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Number box top left corner position (x, y)
            width (int): Number box width
            range (tuple[int, int, int]): Number box range (min, step, max)
            value (int): Number box current value
            enabled (bool): Number box enabled / disabled
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(width, 40)
        self.setEnabled(enabled)

        self.setMinimum(range[0])
        self.setSingleStep(range[1])
        self.setMaximum(range[2])
        self.setValue(value)

        self.valueChanged.connect(value_changed_signal)


class UI_FloatBox(QDoubleSpinBox):
    """ Float Box component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8, 8),
        width: int = 64,
        range: tuple[float, float, float] = (0, 0.1, 1),
        value: float = 0.0,
        enabled: bool = True,
        value_changed_signal: callable = None
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Float box top left corner position (x, y)
            width (int): Float box width
            range (tuple[float, float, float]): Float box range (min, step, max)
            value (float): Float box current value
            enabled (bool): Float box enabled / disabled
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(width, 40)
        self.setEnabled(enabled)

        self.setMinimum(range[0])
        self.setSingleStep(range[1])
        self.setMaximum(range[2])
        self.setValue(value)

        self.valueChanged.connect(value_changed_signal)