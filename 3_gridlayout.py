import sys
import matplotlib
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QGridLayout, QMainWindow
from matplotlib.backend_bases import NavigationToolbar2
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Set up main QApplication

# load a data:


import numpy as np


global plot_state
plot_state=False

def create_plot(figure, canvas,state=False):
    # Generate random data
    figure.clear()
    np.random.seed(42)
    n_points = 50
    x = np.random.uniform(0, 100, n_points)
    y = 2 * x + 10 + np.random.normal(0, 15, n_points)

    # Create subplot
    ax = figure.add_subplot(111)

    # Your original plotting code
    ax.scatter(x, y, alpha=0.7, color="#FF6B6B", s=60, label="Random Data")

    # Add trend line
    if state:
        z = np.polyfit(x, y, 1)
        p=np.poly1d(z)
    else: 
        z=np.polyfit(x,y,2)
    p = np.poly1d(z)
    ax.plot(
        x,
        p(x),
        color="#4ECDC4",
        linewidth=3,
        label=f"Trend Line (y = {z[0]:.2f}x + {z[1]:.2f})",
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



def handle_click():
    nonlocal plot_state
    return plot_state= not plot_state



def event_plot_handler(initial_state=False,figure_obj=None,canvas_obj=None):    
    
    plot_state=False
    def handle_click():
        nonlocal plot_state
        plot_state=not plot_state
        if plot_state:
            print("Button was clicked. Trend line visibility toggled to polyfit 1" )
        else:
            print("Button was clicked. Trend line visibility toggled to polyfit 2" )

        if figure_obj and canvas_obj:
                create_plot(figure_obj, canvas_obj, plot_state)
        else:
            print("Error: Figure or Canvas objects not provided for plotting.")

        return plot_state
  # Perform an initial plot drawing based on the initial state
    if figure_obj and canvas_obj:
        create_plot(figure_obj, canvas_obj, plot_state)
    else:
        print("Warning: Figure or Canvas objects not provided during setup, initial plot not drawn.")

    return handle_click() # Return the function that handles clicks








# Main Script
app = QApplication([])
main_window = QWidget()
layout = QGridLayout()

# File widget (left column)
file_button = QPushButton("Open File")
layout.addWidget(file_button, 0, 0, 2, 1)  # the 2,1 is span row=2, span_col=1
# j First plot and toolbar

fig1 = Figure(figsize=(6, 8))
canvas1 = FigureCanvas(fig1)
create_plot(fig1, canvas1)
toolbar1 = NavigationToolbar(canvas1, main_window)
layout.addWidget(toolbar1, 0, 1)
layout.addWidget(canvas1, 1, 1)


# Second plot and toolbar
fig2 = Figure(figsize=(4, 3))
canvas2 = FigureCanvas(fig2)
toolbar2 = NavigationToolbar(canvas2, main_window)
create_plot(fig2, canvas2)
layout.addWidget(toolbar2, 0, 2)
layout.addWidget(canvas2, 1, 2)

# adding button underneathd
push_button = QPushButton("toggle poly2d")
layout.addWidget(push_button, 2, 2)
push_button.clicked.connect(handle_click)


# set laayout to main window
main_window.setLayout(layout)


if __name__ == "__main__":
    try:
        main_window.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Exiting program")
        app.quit()
        sys.exit(0)
