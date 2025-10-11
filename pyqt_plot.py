import importlib
import DroppablePlotWidget
from PlotNavigator import PlotNavigator, data_manager, SliceRenderer
import sys
from PyQt5.QtCore import Qt, QObject, pyqtSignal
import data_manager
from miniWidget import MiniWidget

# this is a test to see how good pyqt plot is
from data_manager import DataManager, DataManagerNavigator
from skimage import exposure
from PIL.Image import alpha_composite
from matplotlib import image
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import nrrd
from importlib import reload
import math
from data_manager import DataManager
from matplotlib.widgets import Slider

# load the nrrd data
from PIL import Image, ImageEnhance
from skimage import exposure
from matplotlib.widgets import Button
from pyqtgraph.Qt import QtWidgets

from dataclasses import dataclass
from typing import List, Any  #
import math
from PyQt5.QtWidgets import (
    QInputDialog,
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
    QMessageBox,
)
from DroppablePlotWidget import DroppablePlotWidget

import pyqtgraph as pg

pg.setConfigOption("imageAxisOrder", "row-major")
pg.setConfigOptions(useOpenGL=True)


app = QtWidgets.QApplication([])
main = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
layout_graph2 = QtWidgets.QVBoxLayout()
hlayout = QtWidgets.QHBoxLayout()
output_label = QLabel("Index 0")
output_label2 = QLabel("NONE")

layout.addWidget(output_label)
layout_graph2.addWidget(output_label2)

# win = pg.GraphicsLayoutWidget()
# win2 = pg.GraphicsLayoutWidget()
win = DroppablePlotWidget()
win2 = DroppablePlotWidget()


layout.addWidget(win)
layout_graph2.addWidget(win2)


# Example masks: binary numpy arrays for each slice
# number of idea slice
name = input("Patient_number: ")


root_dir = "/Users/tahsin/gdrive/My Drive/OPAL/krispy_kreme_tahsin/"
root_dir = f"{root_dir}{name}"
try:
    data = DataManager(root_dir)
except ValueError:
    sys.exit(1)

renderer = SliceRenderer(win)
navigator = PlotNavigator(data, win, renderer)
navigator.position_changed.connect(
    lambda pos: output_label.setText(f"Index Position {pos} !")
)
navigator.current()

# navigaotr2
try:
    data2 = DataManager(root_dir)
except ValueError:
    sys.exit(1)

renderer2 = SliceRenderer(win2)
navigator2 = PlotNavigator(data2, win2, renderer2)

navigator2.position_changed.connect(
    lambda pos: output_label2.setText(f"Index Position {pos} !")
)


manifest_widget = None  # Keep a reference to the manifest widget


def add_manifest_box(masterlayout, manifest):
    global manifest_widget
    # If a manifest widget already exists, remove it first.
    if manifest_widget is not None:
        manifest_widget.deleteLater()
        manifest_widget = None

    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    for item in manifest.keys():
        mini = MiniWidget(str(item))
        layout.addWidget(mini)
        # mini.clicked.connect(navigator.goto) # You may need to connect this signal

    widget.setLayout(layout)
    manifest_widget = widget
    # Insert at the top of the layout, so the reload button is pushed down.
    masterlayout.insertWidget(0, manifest_widget)


def reload_data():
    global data, data2, navigator, navigator2, name, root_dir

    # For development: reload the miniWidget module
    import miniWidget
    importlib.reload(miniWidget)

    print(f"--- reloading data from {root_dir} ---")
    try:
        # Create new DataManager instances
        new_data_manager1 = DataManager(root_dir)
        new_data_manager2 = DataManager(root_dir)

        # The add_manifest_box function now handles removing the old one
        add_manifest_box(h_layout_manifest, new_data_manager1.manifest)

        # Update navigators with new data managers
        if navigator:
            navigator.update_data_manager(new_data_manager1)
            navigator.current()
        if navigator2:
            navigator2.update_data_manager(new_data_manager2)
            navigator2.current()

        # Update the global data manager references
        data = new_data_manager1
        data2 = new_data_manager2

    except (ValueError, FileNotFoundError) as e:
        print(f"Error reloading data for patient '{name}': {e}")
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Critical)
        msg_box.setText(f"Failed to load data for patient: {name}")
        msg_box.setInformativeText(str(e))
        msg_box.setWindowTitle("Error")
        msg_box.exec_()


def handle_reload_click():
    global name, root_dir
    """Handle reload button click with input dialog"""
    text, ok = QInputDialog.getText(
        main,
        "Reload Data",
        "Enter patient name:",
        text=name,  # Pre-fill with current patient name
    )
    if ok and text.strip():
        new_patient_name = text.strip()
        print(f"Reloading data for patient: {new_patient_name}")

        # Update patient name and root directory
        name = new_patient_name
        root_dir = (
            f"/Users/tahsin/gdrive/My Drive/OPAL/krispy_kreme_tahsin/{new_patient_name}"
        )

        reload_data()
    else:
        print("Reload cancelled or no patient name entered.")


toggle_button = QtWidgets.QPushButton("Toggle Masks")
next_button = QtWidgets.QPushButton("Next Volume")
prev_button = QtWidgets.QPushButton("Previous Volume")

toggle_button2 = QtWidgets.QPushButton("Toggle Masks")
next_button2 = QtWidgets.QPushButton("Next Volume")
prev_button2 = QtWidgets.QPushButton("Previous Volume")


# MANIFEST LOGIC
h_layout_manifest = QtWidgets.QVBoxLayout()

# Add a reload button
reload_button = QtWidgets.QPushButton("Reload Patient Data")
reload_button.clicked.connect(handle_reload_click)
h_layout_manifest.addWidget(reload_button)

add_manifest_box(h_layout_manifest, navigator.data_manager.manifest)
hlayout.addLayout(h_layout_manifest)

# for layout1
layout.addWidget(toggle_button)
layout.addWidget(next_button)
layout.addWidget(prev_button)

# for layout2
layout_graph2.addWidget(toggle_button2)
layout_graph2.addWidget(next_button2)
layout_graph2.addWidget(prev_button2)


toggle_button.clicked.connect(navigator.toggle_all_masks)
next_button.clicked.connect(navigator.next)
prev_button.clicked.connect(navigator.back)


toggle_button2.clicked.connect(navigator2.toggle_all_masks)
next_button2.clicked.connect(navigator2.next)
prev_button2.clicked.connect(navigator2.back)


win.slice_dropped.connect(navigator.goto)
win2.slice_dropped.connect(navigator2.goto)


hlayout.addLayout(layout)
hlayout.addLayout(layout_graph2)

main.setLayout(hlayout)
main.show()
app.exec_()

