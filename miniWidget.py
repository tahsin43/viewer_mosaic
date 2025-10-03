from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel, QVBoxLayout

from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QMainWindow,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QTextEdit,
    QLabel,
)
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QMimeData
from PyQt5.QtGui import QDrag


class MiniWidget(QWidget):
    clicked = pyqtSignal(int)  # Signal: "I was clicked with this index"

    def __init__(self, text):
        super().__init__()
        self.setFixedSize(100, 40)
        self.text = text
        self.setStyleSheet("background: lightblue; border: 1px solid blue;")
        self.index = int(text)

        self.layout = QVBoxLayout()
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.drag_start_position = None

    def mousePressEvent(self, event):
        """User pressed mouse button"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Just remember where they clicked
            self.drag_start_position = event.pos()
            # DON'T emit clicked here - wait to see if they drag or just click

    def mouseMoveEvent(self, event):
        """User moved mouse while holding button"""
        # If not holding left button, ignore
        
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        # If we don't have a start position, ignore
        if self.drag_start_position is None:
            return

        # Check if they moved enough to be considered a drag (not just a tiny jitter)
        distance = (event.pos() - self.drag_start_position).manhattanLength()
        if distance < 5:  # Less than 5 pixels = probably just a click
            return

        # OK, this is a DRAG, not a click!
        # Create the drag operation
        drag = QDrag(self)
        mime_data = QMimeData()

        # Put the slice index in the package
        mime_data.setText(str(self.index))

        # Attach package to drag
        drag.setMimeData(mime_data)

        # Start dragging (this blocks until drop or cancel)
        drag.exec_(Qt.CopyAction)
        print(f"Drag started with index: {self.index}")

    def mouseReleaseEvent(self, event):
        """User released mouse button"""
        # If they released without dragging much, treat it as a click
        if self.drag_start_position is not None:
            distance = (event.pos() - self.drag_start_position).manhattanLength()
            if distance < 5:  # Small movement = click
                self.clicked.emit(self.index)  # NOW emit the clicked signal

        # Clean up
        self.drag_start_position = None
