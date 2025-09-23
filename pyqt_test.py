import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow


class Mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()


def main():
    app = QApplication(sys.argv)
    window = Mainwindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
