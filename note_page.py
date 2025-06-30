from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from datetime import datetime
import json
from uuid import uuid4
# from markdown_page import MarkdownContainer
from note_area import NoteArea


class NotePage(QFrame):

    backButton = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.top_bar = TopBar()
        self.top_bar.backButton.connect(self.back)
        self.main_layout.addWidget(self.top_bar)

        self.current_file_path = ""
        self.current_file = {}

        self.note_container = None
        self.bottom_bar = BottomBar("file.txt", "directory")
        self.main_layout.addWidget(self.bottom_bar)

    def back(self):
        if self.note_container:
            self.write_file()

        self.backButton.emit()

    def write_file(self):
        if self.note_container:
            current = self.note_container.input.toPlainText()
            with open(self.current_file_path, "r") as f:
                prev_file = f

            with open(self.current_file_path, "w") as f:
                f.write(self.note_container.input.toPlainText())

            # update the file
            if current != prev_file:
                settings = self.load_settings()
                for i, note in enumerate(settings["notes"]):
                    if note["uuid"] == self.current_file['uuid']:
                        current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                        self.update_bottom_bar("action", f"Saved {current_date}")
                        note["edited"] = current_date
                        settings["notes"][i] = note
                        with open(f"files/settings.json", "w") as f:
                            f.write(json.dumps(settings, indent=4))


    def load_settings(self) -> dict:
        with open("files/settings.json", "r") as f:
            return json.load(f)

    def loadNote(self, uuid):
        if self.note_container:
            self.main_layout.removeWidget(self.note_container)
            self.note_container.deleteLater()

        settings = self.load_settings()
        notes = settings["notes"]
        for note in notes:
            if note["uuid"] == uuid:

                self.current_file_path = f"{settings['base_path']}{note['file']}"
                self.current_file = note

                self.note_container = NoteArea(settings, uuid)
                self.note_container.updateBottomBar.connect(self.update_bottom_bar)
                self.note_container.saved.connect(self.write_file)

                if note['type'] != "plain":
                    self.note_container.swap_plaintext_markdown()
                    self.note_container.input.setText(
                        self.note_container.input.toPlainText()
                    )

                self.main_layout.addWidget(self.note_container)

                self.update_bottom_bar("file", f"{note['file']}")
                dir = settings["base_path"].split("/")[-2]
                self.update_bottom_bar("directory", f"{dir}")
                self.update_bottom_bar(
                    "action",
                    f"Last Change {
                    QDateTime(*[int(dt) for dt in note['edited'].split("-")]).toString()
                }",
                )
                self.update_bottom_bar("cursor", "11")

        # reposition the bottom bar to be actually at the bottom
        self.main_layout.removeWidget(self.bottom_bar)
        self.main_layout.addWidget(self.bottom_bar)

    def update_bottom_bar(self, name, value):
        match name:
            case "cursor":
                self.bottom_bar.position_label.setText(f"{value[0]}:{value[1]}")
            case "action":
                self.bottom_bar.last_change_label.setText(value)
            case "file":
                self.bottom_bar.file_label.setText(value)
            case "directory":
                self.bottom_bar.path_label.setText(value)


class TopBar(QFrame):

    backButton = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setFixedHeight(64)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.setObjectName("top-bar")
        self.setStyleSheet(
            """
        #top-bar{
            background-color: #303030;
            border-bottom: 1px solid white;
            border-radius: 0px;
        }
        QPushButton{
            border: none;
        }
        """
        )

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignHCenter
        )

        self.back_button = self.IconButton(
            QIcon("/home/zach/Desktop/icons/light_arrow_back.svg")
        )
        self.back_button.clicked.connect(self.backButton.emit)
        self.main_layout.addWidget(self.back_button)

    class IconButton(QPushButton):
        def __init__(self, ico: QIcon, *args, **kwargs):
            super().__init__(*args, *kwargs)

            self.setFixedSize(63, 63)
            self.setIcon(ico)
            self.setIconSize(QSize(32, 32))

        def enterEvent(self, event: QEnterEvent, /) -> None:
            self.setStyleSheet("background-color: #404040; border: none;")
            return super().enterEvent(event)

        def leaveEvent(self, event: QEvent, /) -> None:
            self.setStyleSheet("background-color: #303030; border: none;")
            return super().leaveEvent(event)


class BottomBar(QFrame):
    def __init__(self, file, path, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.file = file
        self.path = path

        self.setObjectName("bottom-bar")
        self.setStyleSheet(
            """
            #bottom-bar{
                border-top: 1px solid white;
            }
            *{
                background-color: #303030;
                color: white;
                border: none;
            }
            """
        )
        self.setFixedHeight(32)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # LEFT SIDE
        self.file_label = QLabel(f"{self.file}")
        self.path_label = QLabel(f"{self.path}")

        # RIGHT SIDE
        self.position_label = QLabel(f"12:34")
        self.last_change_label = QLabel(f"Saved at 12:35")

        self.main_layout.addWidget(self.file_label)

        self.main_layout.addSpacerItem(
            QSpacerItem(
                0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
        )

        self.main_layout.addWidget(self.path_label)
        self.main_layout.addWidget(self.position_label)
        self.main_layout.addWidget(self.last_change_label)
