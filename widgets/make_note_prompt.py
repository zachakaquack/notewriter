from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import datetime
from uuid import uuid4


class MakeNotePrompt(QFrame):

    accepted = Signal(dict)
    denied = Signal()
    closed = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFixedSize(500, 500)
        self.setStyleSheet(
            """
            *{
                color: white;
            }
            QFrame{
                background-color: #242424;
            }
            QLineEdit{
                background-color: #303030;
                color: white;
                border: 1px solid hsl(0, 0%, 50%);
                border-radius: 5px;
            }
            """
        )

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title_label = QLabel("Make Note", self)
        self.title_font = QFont("Jetbrains Mono", 20)
        self.title_label.setFont(self.title_font)
        self.main_layout.addWidget(self.title_label)

        self.label_font = QFont("Jetbrains Mono", 12)
        self.note_title_label = QLabel("Note Title", self)
        self.note_title_entry = QLineEdit("", self)

        for widget in [self.note_title_label, self.note_title_entry]:
            widget.setFont(self.label_font)
            self.main_layout.addWidget(widget)

        self.note_type_label = QLabel("Note Type")
        self.note_type_label.setFont(self.label_font)
        self.main_layout.addWidget(self.note_type_label)

        self.buttons_type_frame = QFrame()
        self.buttons_type_frame.setStyleSheet(
            """
            QRadioButton {
                color: white;
                padding: 4px;
            }

            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border-radius: 7px;
                border: 2px solid white;
                background-color: #1e1e1e;
            }

            QRadioButton::indicator:checked {
                background-color: white;
            }
            """
        )

        self.buttons_type_layout = QHBoxLayout(self.buttons_type_frame)
        self.buttons_type_frame.setLayout(self.buttons_type_layout)
        self.buttons_type_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_type_layout.setSpacing(10)
        self.buttons_type_layout.setAlignment(  Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.plain_button = QRadioButton("Plain")
        self.plain_button.setChecked(True)
        self.md_button = QRadioButton("Markdown")

        font = QFont("Jetbrains Mono", 12)
        for button in [self.plain_button, self.md_button]:
            button.setFont(font)
            self.buttons_type_layout.addWidget(button)

        self.main_layout.addWidget(self.buttons_type_frame)


        self.buttons_container = QFrame(self)

        self.buttons_container.setStyleSheet(
            """
            QPushButton{
                background-color: #303030;
                color: white;
                border: 1px solid hsl(0, 0%, 50%);
                border-radius: 5px;
                padding: 3px;
            }
            """
        )

        self.buttons_frame = QHBoxLayout(self.buttons_container)
        self.buttons_container.setLayout(self.buttons_frame)
        self.buttons_frame.setContentsMargins(5, 5, 5, 5)
        self.buttons_frame.setSpacing(5)
        self.buttons_frame.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        self.accept_button = self.Button("Create")
        self.deny_button = self.Button("Cancel")

        self.accept_button.clicked.connect(self.handle_accepted)
        self.deny_button.clicked.connect(self.handle_denied)

        for widget in [self.deny_button, self.accept_button]:
            widget.setFont(self.label_font)
            widget.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.buttons_frame.addWidget(widget)

        self.main_layout.addWidget(
            self.buttons_container, stretch=1, alignment=Qt.AlignmentFlag.AlignBottom
        )

    def handle_denied(self):
        self.denied.emit()
        self.close()

    def handle_accepted(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        title = self.note_title_entry.text()
        if not title:
            title = "No Title"

        if self.plain_button.isChecked():
            selected = "plain"
            extension = ".txt"
        else:
            selected = "markdown"
            extension = ".md"

        dictionary = {
            "title": f"{title}",
            "file": f"{title.replace(" ", "_")}{extension}",
            "uuid": f"{uuid4()}",
            "created": f"{current_date}",
            "edited": f"{current_date}",
            "type": selected
        }

        self.accepted.emit(dictionary)
        self.close()
        # return dictionary

    def closeEvent(self, event: QCloseEvent, /) -> None:
        self.closed.emit()
        return super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent, /) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.closed.emit()
            self.close()

        return super().keyPressEvent(event)

    class Button(QPushButton):
        def __init__(self, txt, *args, **kwargs):
            super().__init__(*args, *kwargs)
            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )

            self.set_stylesheet("303030")
            self.setText(txt)

        def set_stylesheet(self, color):
            self.setStyleSheet(
                f"""
                QPushButton{{
                    background-color: #{color};
                    color: white;
                }}
                """
            )

        def enterEvent(self, event: QEnterEvent, /) -> None:
            self.set_stylesheet("353535")
            return super().enterEvent(event)

        def leaveEvent(self, event: QEvent, /) -> None:
            self.set_stylesheet("303030")
            return super().leaveEvent(event)
