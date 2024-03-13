from PySide6.QtWidgets import QWidget
from PySide6.QtCharts import QChartView, QChart, QValueAxis
from PySide6.QtCore import Qt, QMargins

import qtawesome as qta
from themes.colors import light_colors, dark_colors

from icecream import ic

class UI_Chart(QChartView):
    """ Chart component """
    def __init__(
        self,
        parent: QWidget,
        position: tuple[int, int] = (8,8),
        size: tuple[int, int] = (200,200),
        texts: tuple[str, str] = None,
        language: str = 'es'
    ):
        """
        Parameters
        ----------
            parent (QWidget): UI Parent object
            position (tuple[int, int]): Chart top left corner position (x, y)
            size (tuple[int, int]): Chart size (w, h)
            texts (tuple[str, str]): Chart title texts (text_spanish, text_english)
            language (str): App language
                Options: 'es' = Español, 'en' = English
        """
        super().__init__(parent)

        self.parent = parent
        self.move(position[0], position[1])
        self.resize(size[0], size[1])
        self.theme_style = self.parent.theme_style
        self.theme_color = self.parent.theme_color
        self.texts = texts
        
        self.chart_plot = QChart()
        self.chart_plot.setBackgroundVisible(False)
        self.chart_plot.legend().setVisible(False)
        self.chart_plot.setMargins(QMargins(0, 0, 0, 0))
        self.setChart(self.chart_plot)


        self.set_language(language)

    def set_language(self, language: str) -> None:
        """ Change language of button text """
        if self.texts is not None:
            if language == 'es': self.chart_plot.setTitle(self.texts[0])
            elif language == 'en': self.chart_plot.setTitle(self.texts[1])
