from PySide6.QtWidgets import QFrame, QWidget


class UI_Divider(QFrame):
    """ Divider component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8,8),
        length: int = 32,
        orientation: str = 'horizontal',
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Divider top left corner position (x, y)
            length (int): Divider length
            orientation (str): Divider orientation
                Options: 'horizontal', 'vertical'
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        if orientation == 'horizontal':
            self.resize(length, 1)
            self.setFrameShape(QFrame.Shape.HLine)
        elif orientation == 'vertical':
            self.resize(1, length)
            self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color