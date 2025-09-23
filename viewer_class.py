from pathlib import Path
import sys
import matplotlib
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QMainWindow,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
)
from matplotlib.backend_bases import NavigationToolbar2
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class matplot_viewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.set_up()
        self.dir_path = None

    def set_up(self):
        self.state = False
        self.setWindowTitle("matplotlib_viever")
        # set up app-------
        self.app = QApplication(sys.argv)

        # main_window------
        self.main_window = QWidget()
        self.setCentralWidget(self.main_window)
        self.layout = QGridLayout()

        # GRID ----
        # File button----
        self.file_widget = QWidget()
        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(2)

        self.file_button = QPushButton("Open Volume")
        self.file_button.clicked.connect(self.open_file)

        self.file_button_segmentation = QPushButton(" Open Segmentation")
        self.file_button_segmentation.clicked.connect(self.open_file)

        self.vbox.addWidget(self.file_button)
        self.vbox.addWidget(self.file_button_segmentation)
        self.file_widget.setLayout(self.vbox)
        self.layout.addWidget(self.file_widget, 0, 0)

        # Fig 1
        self.fig1 = Figure(figsize=(6, 8))
        self.canvas1 = FigureCanvas(self.fig1)
        self.create_plot(self.fig1, self.canvas1, self.state)
        self.toolbar1 = NavigationToolbar(self.canvas1, self.main_window)
        self.layout.addWidget(self.toolbar1, 0, 1)
        self.layout.addWidget(self.canvas1, 1, 1)
        # Fig 2-----
        self.fig2 = Figure(figsize=(4, 3))
        self.canvas2 = FigureCanvas(self.fig2)
        self.toolbar2 = NavigationToolbar(self.canvas2, self.main_window)
        self.create_plot(self.fig2, self.canvas2, self.state)
        self.layout.addWidget(self.toolbar2, 0, 2)
        self.layout.addWidget(self.canvas2, 1, 2)
        self.push_button = QPushButton("toggle poly2d")
        self.push_button.clicked.connect(self.handle_click)
        self.layout.addWidget(self.push_button, 2, 2)
        self.main_window.setLayout(self.layout)

    def state_handle(self):
        self.state = not self.state

    def handle_click(self):
        """
        This method is called when the 'toggle poly2d' button is clicked.
        It updates the state and redraws both plots.
        """
        self.state_handle()  # Toggle the state
        print(f"Plot state toggled to: {self.state}")  # Optional: print current state

        # Redraw Fig 1 with the new state
        self.create_plot(self.fig1, self.canvas1, self.state)
        # Redraw Fig 2 with the new state

    #        self.create_plot(self.fig2, self.canvas2, self.state)

    def fit_polynomial(self, x, y, degree):
        # Fit the polynomial
        coefficients = np.polyfit(x, y, degree)

        # Create a polynomial function from the coefficients
        polynomial_function = np.poly1d(coefficients)

        # Calculate the y-values based on the fitted polynomial
        y_fitted = polynomial_function(x)

        return coefficients, y_fitted

    def create_plot(self, figure, canvas, state=False):
        # Generate random data
        figure.clear()
        np.random.seed(42)
        n_points = 50
        x = np.random.uniform(0, 100, n_points)
        y = 0.02 * x**2 + 2 * x + 10 + np.random.normal(0, 50, n_points)

        # Create subplot
        ax = figure.add_subplot(111)

        # Your original plotting code
        ax.scatter(x, y, alpha=0.7, color="#FF6B6B", s=60, label="Random Data")

        # Add trend line
        if state:
            coefficients, y_fitted = self.fit_polynomial(x, y, 1)
        else:
            coefficients, y_fitted = self.fit_polynomial(x, y, 2)
        ax.plot(
            x,
            y_fitted,
            color="#4ECDC4",
            linewidth=1,
            label=f"Trend Line (y = {coefficients[0]:.2f}x + {coefficients[1]:.2f})",
        )
        # Customize the plot
        ax.set_title("Random Data with Trend Line", fontsize=16, fontweight="bold")
        ax.set_xlabel("X Values", fontsize=12)
        ax.set_ylabel("Y Values", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Apply tight layout and draw
        figure.tight_layout()
        canvas.draw()

    def open_file(self):
        # Static method to open a directory dialog
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            print(f"Selected directory: {dir_path}")
            self.dir_path = Path(dir_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = matplot_viewer()
    window.show()
    sys.exit(app.exec_())
