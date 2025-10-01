from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class MiniWidget(QWidget):
    clicked = pyqtSignal(int)

    def __init__(self, text):
        super().__init__()
        self.setFixedSize(100, 40)
        self.text = text
        self.setStyleSheet("background: lightblue; border: 1px solid blue;")
        self.index = text

        self.layout = QVBoxLayout()

        # Create a label to display the text and center it
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the label to the layout
        self.layout.addWidget(self.label)

        # Set the layout for this MiniWidget
        self.setLayout(self.layout)
        self.index=int(self.index)

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)
