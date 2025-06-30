from qdarktheme.base import json
from rich.traceback import install
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import qdarktheme
import sys

from home_page import HomePage
from note_page import NotePage
from settings import Settings

install()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setFixedSize(1280, 720)

        self.config = self.load_settings()
        self.base_path = self.config["base_path"]
        self.notes = self.config["notes"]

        self.main_widget = QFrame(self)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.main_layout)

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.main_switcher = Switcher()
        self.home_note_switcher = Switcher()
        self.settings_area = Settings(self.config)
        self.side_bar = SideBar()
        self.main_layout.addWidget(self.side_bar)

        self.side_bar.home.connect(self.swap_home_note)
        self.side_bar.settings.connect(self.swap_settings)

        self.home_page = HomePage(self.config)
        self.home_page.note_container.load_notes(self.base_path)
        self.home_note_switcher.addSwitcher("home_page", self.home_page)
        self.home_page.noteSelected.connect(self.switch_notes)

        self.note_page = NotePage()
        self.note_page.backButton.connect(self.swap_home_page)
        self.home_note_switcher.addSwitcher("note_page", self.note_page)

        self.main_switcher.addSwitcher("home_note", self.home_note_switcher)
        self.main_switcher.addSwitcher("settings", self.settings_area)
        self.main_layout.addWidget(self.main_switcher)

        self.setCentralWidget(self.main_widget)

    def load_settings(self) -> dict:
        with open("files/settings.json", "r") as f:
            return json.load(f)

    def swap_home_note(self):
        self.side_bar.change_ss_bottom()
        self.main_switcher.switchTo("home_note")
        self.note_page.note_container.refresh_upon_switch()

    def swap_settings(self):
        self.side_bar.change_ss_top()
        self.main_switcher.switchTo("settings")

    def swap_home_page(self):
        for note in self.home_page.note_container.notes:
            note.redo_preview()
        self.side_bar.remove_spacer()
        self.home_note_switcher.switchTo("home_page")

    def switch_notes(self, note_uuid):
        self.home_note_switcher.switchTo("note_page")
        self.side_bar.add_spacer()
        self.note_page.loadNote(note_uuid)

    def keyPressEvent(self, event: QKeyEvent, /) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()

        return super().keyPressEvent(event)


class SideBar(QFrame):

    home = Signal()
    settings = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            """
        background-color: #303030;
        border: none;
        """
        )
        self.setFixedSize(64, 720)

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.second_widget = QFrame()
        self.second_layout = QVBoxLayout(self.second_widget)
        self.second_widget.setLayout(self.second_layout)
        self.second_layout.setContentsMargins(0, 0, 0, 0)
        self.second_layout.setSpacing(0)
        self.second_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.second_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.second_widget.setStyleSheet(
            """
        border-right: 1px solid white;
        """
        )

        self.home_button = self.IconButton(
            QIcon("/home/zach/Desktop/icons/light_cottage.svg")
        )

        self.settings_button = self.IconButton(
            QIcon("/home/zach/Desktop/icons/light_settings.svg")
        )

        self.home_button.clicked.connect(self.home.emit)
        self.settings_button.clicked.connect(self.settings.emit)

        for button in self.home_button, self.settings_button:
            button.setStyleSheet(
                """
                border: none;
                """
            )

        self.main_layout.addWidget(self.home_button)
        self.second_layout.addWidget(self.settings_button)
        self.main_layout.addWidget(self.second_widget)

        self.spacer = QSpacerItem(100, 32)

    def add_spacer(self):
        self.main_layout.addSpacerItem(self.spacer)

    def remove_spacer(self):
        self.main_layout.removeItem(self.spacer)

    def change_ss_top(self):
        self.setStyleSheet(
            """
            background-color: #303030;
            border: none;
            border-right: 1px solid white;
            """
        )
        self.second_widget.setStyleSheet("border: none;")

    def change_ss_bottom(self):
        self.setStyleSheet(
            """
            background-color: #303030;
            border: none;
            """
        )
        self.second_widget.setStyleSheet(
            """
            border: none;
            border-right: 1px solid white;
            """
        )

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


class Switcher(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.switchers: list[tuple[str, QWidget]] = []
        self.main_switcher: tuple[str, QWidget] | None = None

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setMainSwitch(self, name: str) -> bool:
        for switch in self.switchers:
            if switch[0] == name:
                self.hideAllSwitches()
                self.main_switcher = switch
                self.main_switcher[1].show()
                return True
        else:
            return False

    def addSwitcherFromTuple(self, tup: tuple[str, QWidget]) -> bool:
        return self._addSwitcher(tup[0], tup[1])

    def addSwitcher(self, name: str, widget: QWidget) -> bool:
        return self._addSwitcher(name, widget)

    def _addSwitcher(self, name: str, widget: QWidget) -> bool:
        for switch in self.switchers:
            if switch[0] == name:
                return False
        self.switchers.append((name, widget))

        self.main_layout.addWidget(widget)
        widget.hide()

        if not self.main_switcher:
            self.main_switcher = self.switchers[0]
            self.main_switcher[1].show()

        return True

    def hideAllSwitches(self) -> None:
        for switch in self.switchers:
            switch[1].hide()
        return

    def switchTo(self, name: str) -> bool:
        for switch in self.switchers:
            if switch[0] == name:
                self.hideAllSwitches()
                switch[1].show()
                return True
        else:
            return False


app = QApplication(sys.argv)
qdarktheme.load_stylesheet()
w = MainWindow()
w.show()
sys.exit(app.exec())
