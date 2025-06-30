import json
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from flow import FlowLayout
from make_note_prompt import MakeNotePrompt
import os


class HomePage(QFrame):

    noteSelected = Signal(str)
    noteCreated = Signal(str, QFrame)

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setStyleSheet("background-color: #1e1e1e;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.config = config

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.top_bar = TopBar(self.config)
        self.top_bar.noteCreated.connect(
            lambda data: self.note_container.load_notes(data["base_path"])
        )
        self.main_layout.addWidget(self.top_bar)

        self.special_layout = QVBoxLayout()
        self.special_layout.setContentsMargins(10, 10, 10, 10)
        self.special_layout.setSpacing(10)

        self.note_container = NotePreviewerContainer()
        self.special_layout.addWidget(self.note_container)

        self.note_container.noteSelected.connect(self.noteSelected)
        self.note_container.noteCreated.connect(self.noteCreated)

        self.main_layout.addLayout(self.special_layout)


class TopBar(QFrame):

    noteCreated = Signal(dict)

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setFixedHeight(64)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.setObjectName("top-bar")
        self.setStyleSheet(
            """
            #top-bar{
                border-bottom: 1px solid white;
                border-radius: 0px;
            }
            *{
                border: none;
                background-color: #303030;
            }
            """
        )

        self.config = config

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignHCenter
        )

        self.add_note_button = self.IconButton(
            QIcon("/home/zach/Desktop/icons/light_add.svg")
        )
        self.add_note_button.clicked.connect(self.make_prompt)
        self.main_layout.addWidget(self.add_note_button)

    def make_prompt(self):
        self.make_note_prompt = MakeNotePrompt()
        self.make_note_prompt.accepted.connect(self.make_note)
        # self.make_note_prompt.denied.connect(print)
        # self.make_note_prompt.closed.connect(print)
        self.make_note_prompt.show()

    def make_note(self, dictionary):
        data = self.write_to_json(dictionary)

        path = self.config["base_path"]
        with open(f"{path}/{dictionary['file']}", "w") as f:
            f.write("")

        self.noteCreated.emit(data)

    def write_to_json(self, dictionary):
        path = self.config["base_path"]
        with open(f"{path}/settings.json", "r") as f:
            data = json.load(f)

            data["notes"].append(dictionary)
            with open(f"{path}/settings.json", "w") as f:
                f.write(json.dumps(data, indent=4))
                return data

    class IconButton(QPushButton):
        def __init__(self, ico: QIcon, *args, **kwargs):
            super().__init__(*args, *kwargs)

            self.setFixedSize(63, 63)
            self.setIcon(ico)
            self.setIconSize(QSize(32, 32))

        def enterEvent(self, event: QEnterEvent, /) -> None:
            self.setStyleSheet("background-color: #404040;")
            return super().enterEvent(event)

        def leaveEvent(self, event: QEvent, /) -> None:
            self.setStyleSheet("background-color: #303030;")
            return super().leaveEvent(event)


class NotePreviewerContainer(QScrollArea):

    noteSelected = Signal(str)
    noteCreated = Signal(str, QFrame)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.notes = []

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.main_widget = QFrame()
        self.main_layout = FlowLayout(self.main_widget)
        self.main_widget.setLayout(self.main_layout)
        self.main_layout.setSpacing(25)
        self.setWidget(self.main_widget)

    def load_notes(self, base_path):

        while (child := self.main_layout.takeAt(0)) != None:
            child.widget().hide()

        with open(f"{base_path}settings.json", "r") as f:
            notes = json.load(f)["notes"]

        for note in notes:
            preview = NotePreview(base_path, note)
            self.noteCreated.emit(preview.uuid, preview)
            preview.noteSelected.connect(self.noteSelected.emit)
            preview.noteDeleted.connect(lambda b=base_path: self.load_notes(b))
            self.notes.append(preview)
            self.main_layout.addWidget(preview)


class NotePreview(QFrame):

    noteSelected = Signal(str)
    noteDeleted = Signal()

    def __init__(self, base_path, note, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.base_path = base_path
        self.note = note
        self.file = note["file"]
        self.path = f"{self.base_path}{self.file}"

        self.note_title = note["title"]
        self.note_date = note["created"]
        self.edited_date = note["edited"]
        self.uuid = note["uuid"]

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("note-preview")
        self.setStyleSheet(
            """
            #note-preview{
                background-color: white;
                border: 1px solid white;
                border-radius: 10px;
            }
            QFrame{
                border-radius: 10px;
            }
            """
        )
        self.setFixedSize(382, 200)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(5, 5)
        self.shadow.setColor(QColor(255, 255, 255, 50))
        self.setGraphicsEffect(self.shadow)

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        # top section (the "rendered" version)
        self.rendered_section = QFrame(self)
        self.rendered_section.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.rendered_section_layout = QVBoxLayout(self.rendered_section)
        self.main_layout.addWidget(self.rendered_section)
        self.rendered_section.setObjectName("rendered-section")

        self.rendered_section.setStyleSheet(
            """
            #rendered-section{
                background-color: hsl(0, 0%, 10%);
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
            """
        )

        with open(self.path, "r") as f:
            self.path_text = f.read()

        self.path_label = QLabel(self.path_text)
        self.path_label.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        self.path_label.setStyleSheet(
            "background-color: hsl(0, 0%, 10%); color: hsla(0, 0%, 80%, 0.5)"
        )
        self.path_label.setFont(QFont("Jetbrains Mono", 20))
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.rendered_section_layout.addWidget(
            self.path_label, alignment=Qt.AlignmentFlag.AlignTop
        )

        # bottom section (the information)
        self.info_section = QFrame(self)
        self.info_section.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.info_section_layout = QHBoxLayout(self.info_section)
        self.main_layout.addWidget(self.info_section)

        self.icon_label = QPushButton("", self)

        if self.note['type'] == "plain":
            self.icon = QIcon("/home/zach/Desktop/icons/draft.svg")
        else:
            self.icon = QIcon("/home/zach/Desktop/icons/light_markdown.svg")
        self.icon_label.setIcon(self.icon)
        self.icon_label.setIconSize(QSize(32, 32))
        self.info_section_layout.addWidget(self.icon_label)

        self.note_title_label = EllipsisLabel(f"{self.note_title}", self.info_section)
        self.info_section_layout.addWidget(self.note_title_label, stretch=1)

        dt = [int(a) for a in self.note_date.split("-")]
        self.datetime = QDateTime(*dt)
        string = self.datetime.toString()
        string = string[:3] + ", " + string[4:]
        string = string[:11] + "\n" + string[12:]
        # string = string[:21] + "\n" + string[22:]
        self.note_date_label = QLabel(
            f"{string}",
            self.info_section,
        )
        self.note_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_section_layout.addWidget(
            self.note_date_label, alignment=Qt.AlignmentFlag.AlignRight
        )

        for label in [self.note_title_label, self.note_date_label]:
            label.setFont(QFont("Jetbrains Mono", 10))

        self.main_layout.setStretch(0, 70)
        self.main_layout.setStretch(1, 30)

        self.info_thing = InfoButton(self)
        self.info_thing.move(382 - 20 - 25 - 10, 0 + 10)
        self.info_thing.raise_()
        self.info_thing.clicked.connect(self.open_info)

        # the three dots
        self.three_dots_thing = ThreeDots(self)
        self.three_dots_thing.move(382 - 20 - 10, 0 + 10)
        self.three_dots_thing.raise_()
        self.three_dots_thing.clicked.connect(self.open_menu)

        self.set_infosection_stylesheet("#303030")

    def set_infosection_stylesheet(self, color):
        self.info_section.setStyleSheet(
            f"""
            background-color: {color};
            color: white;
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            """
        )

    def redo_preview(self):
        with open(self.path, "r") as f:
            text = f.read()
            self.path_label.setText(text)

    def mousePressEvent(self, event: QMouseEvent, /) -> None:
        self.noteSelected.emit(f"{self.uuid}")
        return super().mousePressEvent(event)

    def enterEvent(self, event: QEnterEvent, /) -> None:
        self.set_infosection_stylesheet("#404040")
        self.shadow.setOffset(10, 10)
        self.setGraphicsEffect(self.shadow)
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent, /) -> None:
        self.set_infosection_stylesheet("#303030")
        self.shadow.setOffset(5, 5)
        self.setGraphicsEffect(self.shadow)
        return super().leaveEvent(event)

    def open_menu(self):
        menu = Menu()

        menu.deleteNote.connect(self.delete_note)
        menu.duplicateNote.connect(self.duplicate_note)

        pos = self.three_dots_thing.mapToGlobal(self.three_dots_thing.rect().topLeft())
        pos.setX(pos.x() - 100)
        menu.exec(pos)

    def delete_note(self):
        with open(f"{self.base_path}settings.json", "r") as f:
            data = json.load(f)

        for i, note in enumerate(data["notes"]):
            if note["uuid"] == self.uuid:
                data["notes"].pop(i)
                os.remove(f"{data['base_path']}{note['file']}")

        with open(f"{self.base_path}settings.json", "w") as f:
            f.write(json.dumps(data, indent=4))
        self.noteDeleted.emit()

    def duplicate_note(self):
        print("duplicating note")

    def open_info(self):
        self.menu = InfoFrame(self.note)
        self.menu.show()


class InfoFrame(QFrame):
    def __init__(self, note, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.note = note

        self.setFixedSize(500, 500)
        self.setStyleSheet(
            """
            background-color: #1e1e1e;
            color: white;
            """
        )

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        for key, value in self.note.items():
            key = key.title()
            if key.lower() == "uuid":
                key = "UUID"

            groupbox = QGroupBox()
            layout = QVBoxLayout()
            groupbox.setLayout(layout)

            groupbox.setTitle(key)
            label = QLabel(f"{value}")
            layout.addWidget(label)
            self.main_layout.addWidget(groupbox)

        self.close_button = QPushButton("Close", self)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.close_button.clicked.connect(self.close)
        self.main_layout.addWidget(
            self.close_button, stretch=1, alignment=Qt.AlignmentFlag.AlignBottom
        )


class Menu(QMenu):

    deleteNote = Signal()
    duplicateNote = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setFixedWidth(100)

        self.setStyleSheet(
            """
            QMenu{
                color: white;
                background-color: #303030;
            }
            """
        )

        self.addAction("Delete", self.deleteNote.emit)
        self.addSeparator()
        # self.addAction("Duplicate", self.duplicateNote.emit)


class ThreeDots(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setStyleSheet(
            """
            background-color: transparent;
            border: none;
            """
        )
        siz = 20
        self.light = QIcon("/home/zach/Desktop/icons/light_more_vert.svg")
        self.setFixedSize(siz, siz)
        self.setIconSize(QSize(siz, siz))
        self.setIcon(self.light)


class InfoButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setStyleSheet(
            """
            background-color: transparent;
            border: none;
            """
        )
        siz = 20
        self.light = QIcon("/home/zach/Desktop/icons/light_info.svg")
        self.setFixedSize(siz, siz)
        self.setIconSize(QSize(siz, siz))
        self.setIcon(self.light)


class EllipsisLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self.setText(text)

    def setText(self, text):
        self._text = text
        self.updateText()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateText()

    def updateText(self):
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(
            self._text, Qt.TextElideMode.ElideRight, self.width()
        )
        super().setText(elided)
