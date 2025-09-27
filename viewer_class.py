import importlib
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
from Plot_manager import PlotManager
from data_manager import DataManager, DataManagerNavigator
from miniWidget import MiniWidget
import miniWidget


class matplot_viewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.set_up()
        self.dir_path = None
        self.data_Manager = None
        self.data_Navigator = None
        # A button to trigger the reload

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
        self.fig1 = Figure(figsize=(15, 15))
        self.canvas1 = FigureCanvas(self.fig1)

        self.toolbar1 = NavigationToolbar(self.canvas1, self.main_window)
        self.layout.addWidget(self.toolbar1, 0, 1)
        self.layout.addWidget(self.canvas1, 1, 1)

        self.push_button = QPushButton(" toggle visibility ")

        self.push_button.clicked.connect(self.handle_click)

        self.PlotManager = None
        self.next_button = QPushButton(" Next Slice ")
        self.next_button.clicked.connect(self.next_click)
        self.layout.addWidget(self.next_button, 2, 1)

        # Fig 2-----
        # self.fig2 = Figure(figsize=(4, 3))
        # self.canvas2 = FigureCanvas(self.fig2)
        # self.toolbar2 = NavigationToolbar(self.canvas2, self.main_window)
        # self.create_plot(self.fig2, self.canvas2, self.state)
        # self.layout.addWidget(self.toolbar2, 0, 2)
        # self.layout.addWidget(self.canvas2, 1, 2)
        # self.push_button = QPushButton("toggle poly2d")
        # self.push_button.clicked.connect(self.handle_click)

        self.reload_button = QPushButton("Reload MiniWidget UI")
        self.reload_button.clicked.connect(self.reload)
        self.layout.addWidget(self.reload_button, 3, 0)

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
        print("this is the state", self.state)
        print(f"Plot state toggled to: {self.state}")  # Optional: print current state

        # Redraw Fig 1 with the new state
        self.PlotManager.toggle_mask_visibility(self.state)
        # Redraw Fig 2 with the new state

    #        self.create_plot(self.fig2, self.canvas2, self.state)
    def next_click(self):
        self.data_Navigator.next()

        self.PlotManager.display_plot()

    def open_file(self):
        # Static method to open a directory dialog

        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            print(f"Selected directory: {dir_path}")
            self.dir_path = Path(dir_path)
            self.data_Manager, self.data_Navigator = self.set_up_Data_Manager(dir_path)
            self.add_manifest_box()
            self.PlotManager = PlotManager(self.canvas1,self.data_Navigator)

            self.PlotManager.display_plot()

    def set_up_Data_Manager(self, root_dir):
        data_Manager = DataManager(root_dir)
        data_Navigator = DataManagerNavigator(data_Manager)
        return data_Manager, data_Navigator

    def add_manifest_box(self):
        widget = QWidget()
        # self.vbox.setSpacing(1j)
        manifest = self.data_Manager.get_Manifest()
        layout = QVBoxLayout()
        print("this is a test to see if manifest is here")
        print(manifest)
        for item in manifest.keys():
            mini = MiniWidget(str(item))
            layout.addWidget(mini)
        widget.setLayout(layout)
        self.layout.addWidget(widget, 1, 0)

    def reload(self, widget):
        print("--- Reloading UI ---")
        item = self.layout.itemAtPosition(1, 0)
        widget_delete = item.widget()
        print(item)
        self.layout.removeWidget(widget_delete)
        # 1. Reload the module containing the widget class
        importlib.reload(miniWidget)

        # 2. Delete the old widget instance
        # self.add_manifest_box()
        # 3. Create a new instance from the reloaded class
        #     widget_delete.deleteLater()
        print("Widget at (0,0) has been deleted.")

        # 4. Add the new instance to the layout:


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = matplot_viewer()
    window.show()
    sys.exit(app.exec_())
