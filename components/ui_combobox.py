from PySide6.QtWidgets import QComboBox, QWidget
from PySide6.QtCore import Qt


class UI_ComboBox(QComboBox):
    """ Combo box component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8,8),
        width: int = 40,
        texts: tuple[str, str] = None,
        options: dict = None,
        set: int = -1,
        editable: bool = False,
        enabled: bool = True,
        language: str = 'es',
        index_changed_signal: callable = None,
        text_changed_signal: callable = None,
        activated_signal: callable = None,
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Combo box top left corner position (x, y)
            width (int): Combo box width
            texts (tuple[str, str]): Combo box labels (label_spanish, label_english)
            options (dict): Combo box options with translations
                options = {
                    0: ('spanish_1', 'english_1'),
                    1: ('spanish_2', 'english_2')
                }
            set (int): Selected option starting at 0
                -1: No option selected
            editable (bool): Combo box is editable or not 
            enabled (bool): Combo box enabled / disabled
            language (str): App language
                Options: 'es' = Español, 'en' = English
            index_changed_signal (callable): Combo box 'index changed' method name
            text_changed_signal (callable): Combo box 'text changed' method name
            activated_signal (callable): Combo box 'activated' method name
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(width, 40)
        self.setEnabled(enabled)
        self.view().window().setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.texts = texts
        self.options = options

        self.setMaxVisibleItems(5)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setEditable(editable)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.set_language(language)
        self.setCurrentIndex(set)
        
        self.currentIndexChanged.connect(index_changed_signal)
        self.currentTextChanged.connect(text_changed_signal)
        self.activated.connect(activated_signal)

    def set_language(self, language: str) -> None:
        """ Change language of options text """
        if self.texts is not None:
            if language == 'es':   self.setPlaceholderText(self.texts[0])
            elif language == 'en': self.setPlaceholderText(self.texts[1])

        self.clear()
        for key, value in self.options.items():
            self.addItem('')
            if language == 'es':   self.setItemText(key, value[0])
            elif language == 'en': self.setItemText(key, value[1])