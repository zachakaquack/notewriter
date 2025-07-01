from types import FunctionType
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class TopBar(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        # geometry
        self.setFixedHeight(64)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # styling

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

        # layout
        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        # store the widgets in the top bar
        self.widgets = []

    def set_spacing(self, spacing: int) -> None:
        """
        sets the spacing between the widgets within the layout
        """
        self.main_layout.setSpacing(spacing)

    def set_contents_margins(self, margins: tuple[int, int, int, int]) -> None:
        self.main_layout.setContentsMargins(*margins)

    def add_widget(self, name: str, widget: QWidget, cb: FunctionType) -> None:
        """
        add a widget to the top bar.
        if you want the widget to have on click or anything,
        it has to have it by itself on click or someting.
        """
        self.widgets.append([name, widget, cb])
        self.main_layout.addWidget(widget)

    def add_button(self, name: str, icon: QIcon, cb: FunctionType) -> None:
        """
        same thing ass add_widget, but it just uses a button.
        """
        button = self.IconButton(icon)
        button.clicked.connect(cb)
        self.widgets.append([name, button, cb])
        self.main_layout.addWidget(button)

    def add_button_from_file(self, name: str, icon_path: str, cb: FunctionType) -> None:
        """
        same thing as add_button, but uses a path instead of a qicon
        """
        button = self.IconButton(QIcon(icon_path))
        button.clicked.connect(cb)
        self.widgets.append([name, button, cb])
        self.main_layout.addWidget(button)

    def remove_widget(self, widget: QWidget) -> None:
        """
        remove the widget from the layout
        """
        self.main_layout.removeWidget(widget)

    def remove_widget_by_name(self, name: str) -> None:
        """
        remove the widget from the layout by name
        """
        for widget in self.widgets:
            if widget[0] == name:
                self.main_layout.removeWidget(widget[1])


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
