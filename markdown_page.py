from rich.traceback import install
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import qdarktheme
import sys

install()

class MarkdownContainer(QFrame):
    def __init__(self, settings, note, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.settings = settings
        self.note = note

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
          Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.input_area = Input()
        self.markdown_viewer = MarkdownViewer()
        self.input_area.input.textChanged.connect(self.set_new_markdown)

        self.input = self.input_area.input
        self.load_file()

        self.main_layout.addWidget(self.input_area)
        self.main_layout.addWidget(self.markdown_viewer)

    def load_file(self):
        with open(f"{self.settings['base_path']}{self.note['file']}", "r") as f:
            self.input.setPlainText(f.read())

    def set_new_markdown(self):
        md = self.input_area.input.toPlainText()
        self.markdown_viewer.setMarkdown(md)

class Input(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.setStyleSheet(
            """
            QTextEdit{
                background-color: #1e1e1e;
                color: white;
            }
            """
        )
        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(  Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.current_line_count = -1
        self.input = QTextEdit()
        self.input.setFont(QFont("Jetbrains Mono", 12))
        self.input.textChanged.connect(self.update_line_numbers)
        self.input.verticalScrollBar().valueChanged.connect(self.match_scrollbars)

        tab_length = 15
        self.input.setTabStopDistance(
            QFontMetricsF(self.input.font()).horizontalAdvance(" " * tab_length)
        )

        self.sa = QScrollArea()
        self.sa.setWidgetResizable(True)
        self.sa.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.sa.setMinimumWidth(25)
        self.sa.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.sa.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.line_number_widget = QFrame()
        self.line_number_layout = QVBoxLayout(self.line_number_widget)

        self.line_number_widget.setLayout(self.line_number_layout)
        self.line_number_layout.setContentsMargins(1, 0, 1, 0)
        self.line_number_layout.setSpacing(0)
        self.line_number_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.sa.setWidget(self.line_number_widget)


        self.main_layout.addWidget(self.sa)
        self.main_layout.addWidget(self.input)

        self.main_layout.setStretch(0, 5)
        self.main_layout.setStretch(1, 95)

    def match_scrollbars(self, value):
        self.sa.verticalScrollBar().setValue(value)

    def update_line_numbers(self):
        numbers = self.input.document().blockCount()
        if self.current_line_count != numbers:

            while (child := self.line_number_layout.takeAt(0)) != None:
                if child.widget() and isinstance(child.widget(), QLabel):
                    child.widget().deleteLater()

            self.line_number_layout.addSpacerItem(
                QSpacerItem(0, 5)
            )

            for i in range(numbers):
                l = QLabel(f"{i + 1}")
                l.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.line_number_layout.addWidget(l)

class MarkdownViewer(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.setReadOnly(True)
        self.setStyleSheet(
            """
            QTextEdit{
                background-color: #1e1e1e;
                color: white;
            }
            """
        )
