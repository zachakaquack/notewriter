from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import file_management

class NoteArea(QFrame):

    updateBottomBar = Signal(str, object)
    saved = Signal()

    def __init__(self, config, uuid, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.config = config
        self.uuid = uuid

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        # the main input area of the note area - this will be used for both
        # the plaintext and the markdown.
        self.input_area = InputArea(self.config)
        self.input = self.input_area.input
        self.main_layout.addWidget(self.input_area)

        self.input_area.updateBottomBar.connect(
            self.updateBottomBar.emit
        )
        self.input_area.saved.connect(self.saved.emit)

        self.main_layout.addWidget(self.input_area)

        self.markdown_viewer = None
        self.load_files()

    def refresh_upon_switch(self):

        settings = file_management.get_config()
        self.config = settings
        self.input_area.config = settings

        self.input_area.load_tab_length()
        self.input_area.load_font()

        self.input_area.load_line_numbers()

        if self.markdown_viewer:
            self.markdown_viewer.setFont(self.load_font())


    def load_files(self):
        filename = file_management.get_note_by_uuid(self.uuid)['file']
        with open(f"{self.config['base_path']}{filename}", "r") as f:
            text = f.read()
            self.input.setText(text)

    def load_font(self):
        font_size = self.config['settings']['font_size']
        return QFont("Jetbrains Mono", font_size)

    def swap_plaintext_markdown(self):
        """ plaintext by default, so if you want markdown run this"""

        # if it exists already, remove it
        if self.markdown_viewer:
            self.main_layout.removeWidget(self.markdown_viewer)
        else:
            self.markdown_viewer = MarkdownViewer()
            self.markdown_viewer.setFont(
                self.load_font()
            )
            self.input.textChanged.connect(
                lambda: self.markdown_viewer.setMarkdown(
                    self.input.toPlainText()
                )
            )
            self.main_layout.insertWidget(1, self.markdown_viewer)

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



class InputArea(QFrame):

    updateBottomBar = Signal(str, object)
    saved = Signal()

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.setStyleSheet(
            """
            QFrame{
                background-color: #1e1e1e;
            }
            QTextEdit{
                background-color: #1e1e1e;
                color: white;
            }
            """
        )

        self.config = config
        # keeps track of the amount of lines
        self.current_line_count = -1

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        # the actual input stuff
        # the event filter is to catch the undo / redo without having
        # to manually do it myself
        self.input = QTextEdit(self)
        self.input.installEventFilter(self)

        self.input.verticalScrollBar().valueChanged.connect(self.match_scrollbars)

        # the scroll area for the line numbers
        self.ln_scroll = QScrollArea()
        self.ln_scroll.setWidgetResizable(True)

        self.ln_scroll.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.ln_scroll.setMinimumWidth(25)
        self.ln_scroll.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.ln_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ln_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # the widget and layout for the scroll area
        self.ln_widget = QFrame()
        self.ln_layout = QVBoxLayout(self.ln_widget)

        self.ln_widget.setLayout(self.ln_layout)
        self.ln_widget.setStyleSheet("background-color: #1e1e1e;")
        self.ln_widget.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.ln_layout.setSpacing(0)

        self.ln_scroll.setWidget(self.ln_widget)

        # signals
        if not self.config['settings']['relative_line_numbers']:
            self.input.cursorPositionChanged.connect(self.update_line_numbers)
            self.input.cursorPositionChanged.connect(self.update_text_position)
            self.ln_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        else:
            self.ln_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.input.cursorPositionChanged.connect(self.update_relative_line_numbers)
            self.input.cursorPositionChanged.connect(self.update_text_position)

        # finishing the visual
        self.main_layout.addWidget(self.ln_scroll)
        self.main_layout.addWidget(self.input)

        # default shortcuts
        self.shortcuts = [
            # saving
            ["Ctrl+S", self.saved.emit],
            # movement
            ["Ctrl+H", lambda: self.move_character("h")],
            ["Ctrl+J", lambda: self.move_character("j")],
            ["Ctrl+K", lambda: self.move_character("k")],
            ["Ctrl+L", lambda: self.move_character("l")],
            # yank line
            ["Ctrl+Y", lambda: self.line_operations("yank")],
            # delete line
            ["Ctrl+D", lambda: self.line_operations("delete")],
        ]

        self.load_font()
        self.update_line_numbers()
        self.load_tab_length()
        self.load_shortcuts()

    def update_text_position(self):
        cursor = self.input.textCursor()
        pos = cursor.position()

        text_before = self.input.toPlainText()[:pos]
        lines = text_before.split("\n")

        line_number = len(lines)
        column_number = len(lines[-1])

        self.updateBottomBar.emit("cursor", [line_number, column_number])

    def load_shortcuts(self):
        for shortcut, function in self.shortcuts:
            sc = QShortcut(
                QKeySequence(shortcut), self.input
            )
            sc.activated.connect(function)

    def eventFilter(self, source, event):
        if source is self.input and event.type() == QEvent.Type.KeyPress:
            is_ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
            is_shift = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

            if event.key() == Qt.Key.Key_Z and is_ctrl:
                if is_shift:
                    self.updateBottomBar.emit("redo", "")
                else:
                    self.updateBottomBar.emit("undo", "")

        return super().eventFilter(source, event)


    def line_operations(self, operation):
        cursor = self.input.textCursor()

        line_number = cursor.blockNumber()
        text = self.input.toPlainText().split("\n")
        line = text[line_number]

        match operation:
            case "yank":
                QApplication.clipboard().setText(f"{line}")

                # update bottom bar
                self.updateBottomBar.emit(
                    "action", f"Yanked {len(line)} characters"
                )
            case "delete":
                # find, remove, and set the new text
                chars = len(text[line_number])
                text.pop(line_number)
                new_text = "\n".join(text)
                self.input.setText(new_text)

                # reset back to 0
                cursor.setPosition(0)

                # move vertically
                for _ in range(line_number -1):
                    cursor.movePosition(
                        cursor.MoveOperation.Down
                    )

                # move horizontally
                cursor.movePosition(cursor.MoveOperation.EndOfLine)

                # update bottom bar
                self.updateBottomBar.emit(
                    "action", f"Deleted {chars} characters"
                )
            case _:
                pass

        self.input.setTextCursor(cursor)

    def move_character(self, direction):
        cursor = self.input.textCursor()

        match direction:
            case "h":
                cursor.movePosition(cursor.MoveOperation.Left)
            case "j":
                cursor.movePosition(cursor.MoveOperation.Down)
            case "k":
                cursor.movePosition(cursor.MoveOperation.Up)
            case "l":
                cursor.movePosition(cursor.MoveOperation.Right)
            case _:
                pass

        self.input.setTextCursor(cursor)

    def update_settings(self):
        self.config = file_management.get_config()

    def load_tab_length(self):
        """
        loads the tab length (in spaces) from the settings
        """
        # tab_length = self.config['settings']['tab_length']
        tab_length = 5

        self.input.setTabStopDistance(
            QFontMetrics(self.input.font()).horizontalAdvance(" " * tab_length)
        )

    def load_font(self):
        font_size = self.config['settings']['font_size']
        self.main_font = QFont("Jetbrains Mono", font_size)
        self.input.setFont(self.main_font)

        for child in self.ln_widget.children():
            if isinstance(child, QLabel):
                child.setFont(self.main_font)

    def load_line_numbers(self):
        self.input.cursorPositionChanged.disconnect()

        if not self.config['settings']['relative_line_numbers']:
            self.input.cursorPositionChanged.connect(self.update_line_numbers)
            self.input.cursorPositionChanged.connect(self.update_text_position)
            self.ln_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.update_line_numbers()
        else:
            self.ln_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.input.cursorPositionChanged.connect(self.update_relative_line_numbers)
            self.input.cursorPositionChanged.connect(self.update_text_position)
            self.update_relative_line_numbers()


    def update_line_numbers(self):
        """
        updates the amount of line numbers according to the actual amount
        there is.
        """
        numbers = self.input.document().blockCount()

        if self.current_line_count != numbers:

            while (child := self.ln_layout.takeAt(0)) != None:
                if child.widget() and isinstance(child.widget(), QLabel):
                    child.widget().deleteLater()

            for i in range(numbers):
                l = QLabel(f"{i + 1}")
                l.setFont(self.main_font)
                l.setAlignment(Qt.AlignmentFlag.AlignRight)
                self.ln_layout.addWidget(l)

    def update_relative_line_numbers(self):

        while (child := self.ln_layout.takeAt(0)) != None:
            if child.widget() and isinstance(child.widget(), QLabel):
                child.widget().deleteLater()

        numbers = self.input.document().blockCount()
        line_number = self.input.textCursor().blockNumber()

        for i in range(numbers):
            num = abs(i - line_number)
            if num == 0:
                num = line_number + 1
                l = QLabel(f"{num}")
                l.setStyleSheet(
                    "color: white;"

                )
            else:
                l = QLabel(f"{num}")
                l.setStyleSheet(
                    "color: #7aa2f7;"
                )
            l.setFont(self.main_font)
            l.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.ln_layout.addWidget(l)

    def match_scrollbars(self, value):
        """
        matches the scrollbars, so the line numbers scroll
        accordingly to the scroll value of the actual input area
        """
        self.ln_scroll.verticalScrollBar().setValue(value)
