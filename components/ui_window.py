from PySide6.QtWidgets import QWidget


class UI_Window(QWidget):
    """ Main Window """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = None,
        size: tuple[int, int] = (1300, 700),
        minimum_size: tuple[int, int] = (500, 300),
        maximum_size: tuple[int, int] = None,
        titles: tuple[str, str] = ('Aplicación','App'),
        language: str = 'es'
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Window top left corner position (x, y)
                Centered by default
            size (tuple[int, int]): Window width and height (width, height)
            minimum_size (tuple[int, int]): minimum window size when resized 
                (minimum_width, minimum_height)
            maximum_size (tuple[int, int]): maximum window size when resized
                (maximum_width, maximum_height)
            titles (tuple[str, str]): Window titles (title_spanish, title_english)
            language (str): App language
                Options: 'es' = Español, 'en' = English
        """
        super().__init__(parent)

        self.parent = parent
        if position is None:
            screen_x = int(self.parent.screen().availableGeometry().width() / 2 - (size[0] / 2))
            screen_y = int(self.parent.screen().availableGeometry().height() / 2 - (size[1] / 2))
            x, y = (screen_x, screen_y)
        else:
            x, y = (position[0],position[1])
        self.parent.move(x,y)
        self.parent.resize(size[0], size[1])
        self.parent.setMinimumSize(minimum_size[0], minimum_size[1])
        self.parent.setMaximumSize(maximum_size[0], maximum_size[1]) if maximum_size is not None else None
        self.titles = titles
        
        self.set_language(language)


    def set_language(self, language: str) -> None:
        """ Change language of title window """
        if language == 'es': self.parent.setWindowTitle(self.titles[0])
        elif language == 'en': self.parent.setWindowTitle(self.titles[1])