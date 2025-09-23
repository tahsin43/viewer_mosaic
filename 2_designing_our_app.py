# import
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)


# Main app set up
app = QApplication([])
main_window = QWidget()
main_window = setWindowTitle("Random_Window")
main_window.resize()


# Create all app objects:
#
title = QLabel("Random Keyword")

text1 = QLabel("?")
text2 = QLabel("?")
text3 = QLabel("?")

button1 = QPushButton("Click Me")

button2 = QPushButton("Click Me")
button3 = QPushButton("Click Me")

# ADD THEM TO THE SCREEN

master_layout = QVBoxLayout()
row1 = QHBoxLayout()
row2 = QHBoxLayout()
row3 = QHBoxLayout()

row1.addWidget(title)
row2.addWidget(text2)
row2.addWidget(text1)

row3.addWidget(button1)
row3.addWidget(button3)
row3.addWidgdet(button2)
row4jjjjjjsdasdjjjjjjkkjjjjjjj
