# import
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget

# main app
app = QApplication(
    []
)  # Always takes a empty list as an argument to define rows and column
main_window = QWidget()
main_window.setWindowTitle("Random Word Window")

# Events


# Show and ruin
main_window.show()  # always show main window
