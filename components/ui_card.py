from PySide6.QtWidgets import QFrame, QWidget


class UI_Card(QFrame):
    """ Card component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (16, 16),
        size: tuple[int, int] = (96, 96)
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Card top left corner position (x, y)
            size (tuple[int, int]): Card size (width, height)
            language (str): App language
                Options: 'es' = Español, 'en' = English
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(size[0], size[1])
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color