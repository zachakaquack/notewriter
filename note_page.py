from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from datetime import datetime
import json
from uuid import uuid4


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

        self.note_container = None
        self.bottom_bar = BottomBar("file.txt", "directory")
        self.main_layout.addWidget(self.bottom_bar)

    def back(self):
        if self.note_container:
            self.note_container.write_file()

        self.backButton.emit()

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
                self.note_container = NoteContainer(
                    settings, f"{settings['base_path']}{note['file']}", uuid
                )
                self.note_container.updateBottomBar.connect(self.update_bottom_bar)
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


class NoteContainer(QFrame):

    updateBottomBar = Signal(str, object)
    # cursorPositionChanged = Signal(int, int)
    # actionChanged = Signal(str, object)

    # TODO: change note_title and file to just the json dict from config
    def __init__(self, data, file, uuid, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.data = data
        self.file = file
        self.uuid = uuid

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.input = Input()
        self.input.setStyleSheet(
            """
            background-color: #1e1e1e;
            color: white;
            """
        )
        self.input.updateBottomBar.connect(self.updateBottomBar)
        self.input.write.connect(self.write_file)

        self.main_layout.addWidget(self.input)
        with open(self.file, "r") as f:
            self.input.setText(f.read())

        self.load_font_size()

    def load_font_size(self):
        with open(f"{self.data['base_path']}settings.json", "r") as f:
            data = json.load(f)
            font_size = data["settings"]["font_size"]
            # font_size is equal to 20
            self.input.setFont(QFont("Jetbrains Mono", font_size))

    def write_file(self):
        current = self.input.toPlainText()
        with open(self.file, "r") as f:
            prev_file = f

        with open(self.file, "w") as f:
            f.write(self.input.toPlainText())

        # update the file
        if current != prev_file:
            with open(f"{self.data['base_path']}settings.json", "r") as f:
                settings = json.load(f)

            for i, note in enumerate(settings["notes"]):
                if note["uuid"] == self.uuid:
                    current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                    note["edited"] = current_date
                    settings["notes"][i] = note
                    with open(f"{self.data['base_path']}settings.json", "w") as f:
                        f.write(json.dumps(settings, indent=4))


class Input(QTextEdit):

    write = Signal()
    updateBottomBar = Signal(str, object)
    # cursorPositionChanged = Signal(int, int)
    # actionChanged = Signal(str, object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.textChanged.connect(self.update_text_position)

    def keyPressEvent(self, event: QKeyEvent, /) -> None:
        self.update_text_position()
        match event.key():
            case Qt.Key.Key_S:
                if event.modifiers() == Qt.ControlModifier:
                    self.update_last_action("save")
                    self.write.emit()
            case Qt.Key.Key_Z:
                if event.modifiers() == Qt.ControlModifier | Qt.ShiftModifier:
                    self.update_last_action("redo")
                if event.modifiers() == Qt.ControlModifier:
                    self.update_last_action("undo")

        return super().keyPressEvent(event)

    def update_last_action(self, action):
        time = datetime.now().time()
        time = f"{time}"[:-7]
        match action:
            case "save":
                self.updateBottomBar.emit("action", f"Saved at {time}")
            case "undo":
                self.updateBottomBar.emit("action", f"Undo at {time}")
            case "redo":
                self.updateBottomBar.emit("action", f"Redo at {time}")
            case _:
                print(f"unknown action: {action}")

    def update_text_position(self):
        cursor = self.textCursor()
        pos = cursor.position()

        # Get entire document text up to the cursor
        text_before = self.toPlainText()[:pos]
        lines = text_before.split("\n")

        line_number = len(lines)  # 1-based line number
        column_number = len(lines[-1])  # character index within that line

        # self.cursorPositionChanged.emit(line_number, column_number)
        self.updateBottomBar.emit("cursor", [line_number, column_number])
