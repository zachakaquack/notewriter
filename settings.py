import json
from rich.console import Group
from rich.traceback import install
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Settings(QScrollArea):
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.settings = settings

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setObjectName("settings-container")
        self.setStyleSheet(
            """
            #settings-container{
                color: white;
            }
            *{
                color: white;
                background-color: #1e1e1e;
            }
            """
        )

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.main_widget = QFrame(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(15, 15, 5, 5)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.setWidget(self.main_widget)

        self.label_font = QFont("Jetbrains Mono", 20)
        # save on file exit
        self.file_group_box = GroupBox("Save on File Exit")
        self.file_description = QLabel(
            "Toggles whether or not the file saves upon going back to home."
        )
        self.file_check = CheckBox(self.settings["settings"]["save_on_file_exit"])

        self.file_group_box.add_widget(self.file_check)
        self.file_group_box.add_widget(self.file_description)

        self.main_layout.addWidget(self.file_group_box)

        self.font_size_gb = GroupBox("Font Size")
        self.font_size_description = QLabel("Toggles the font size within the editor.")
        self.font_size_edit = QSpinBox(
            self.font_size_gb,
            minimum=8,
            maximum=48,
            value=self.settings["settings"]["font_size"],
        )

        self.font_size_gb.add_widget(self.font_size_edit)
        self.font_size_gb.add_widget(self.font_size_description)
        self.main_layout.addWidget(self.font_size_gb)

        # keep at bottom
        self.save_button = SaveButton("Save", self)
        self.save_button.clicked.connect(self.save_values)
        self.main_layout.addWidget(
            self.save_button, stretch=1, alignment=Qt.AlignmentFlag.AlignBottom
        )

    def save_values(self):
        with open(f"{self.settings['base_path']}settings.json", "r") as f:
            data = json.load(f)

        data["settings"] = self.get_dictionary()
        with open(f"{self.settings['base_path']}settings.json", "w") as f:
            f.write(json.dumps(data, indent=4))

    def get_dictionary(self):
        return {
            "save_on_file_exit": self.file_check.isChecked(),
            "font_size": self.font_size_edit.value(),
        }


class SaveButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(100, 50)
        self.change_ss("#303030")

    def change_ss(self, color):
        self.setStyleSheet(
            f"""
            QPushButton{{
                border: 1px solid white;
                background-color: {color};
                color: white;
                border-radius: 10px;
            }}
            """
        )

    def enterEvent(self, event: QEnterEvent, /) -> None:
        self.change_ss("#404040")
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent, /) -> None:
        self.change_ss("#303030")
        return super().leaveEvent(event)


class GroupBox(QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setStyleSheet(
            """
            QGroupBox{
                border: 1px solid white;
                border-radius: 5px;
                margin-top: 20px;
            }
            """
        )

        self.setMinimumHeight(50)

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )

    def add_widget(self, widget):
        self.main_layout.addWidget(widget)


class CheckBox(QPushButton):
    def __init__(self, checked_by_default, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setCheckable(True)
        self.setChecked(checked_by_default)
        self.setFixedSize(32, 32)
        self.setIconSize(QSize(32, 32))
        self.setText("")
        self.setStyleSheet(
            """
            border: none;
            """
        )

        self.unchecked = QIcon("/home/zach/Desktop/icons/light_check_box_outline.svg")
        self.checked = QIcon("/home/zach/Desktop/icons/light_check_box.svg")

        if checked_by_default:
            self.setIcon(self.checked)
        else:
            self.setIcon(self.unchecked)

    def mousePressEvent(self, e: QMouseEvent, /) -> None:
        if self.isChecked():
            self.setIcon(self.unchecked)
        else:
            self.setIcon(self.checked)
        return super().mousePressEvent(e)
