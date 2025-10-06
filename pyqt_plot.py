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
output_label2=QLabel("NONE")

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
navigator = PlotNavigator(data, win,renderer)
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
navigator2 = PlotNavigator(data2, win2,renderer2)

navigator2.position_changed.connect(
    lambda pos: output_label2.setText(f"Index Position {pos} !"))


def add_manifest_box(masterlayout, manifest):
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    print("this is a test to see if manifest is here")
    print(manifest)
    for item in manifest.keys():
        if item == 1:
            print(item)
            print(type(item))
        mini = MiniWidget(str(item))
        layout.addWidget(mini)

        # mini.clicked.connect(navigator.goto)

    widget.setLayout(layout)
    masterlayout.addWidget(widget)


toggle_button = QtWidgets.QPushButton("Toggle Masks")
next_button = QtWidgets.QPushButton("Next Volume")
prev_button = QtWidgets.QPushButton("Previous Volume")

toggle_button2 = QtWidgets.QPushButton("Toggle Masks")
next_button2 = QtWidgets.QPushButton("Next Volume")
prev_button2 = QtWidgets.QPushButton("Previous Volume")


reload_button=QtWidgets.QPushButton("Reload Data")
reload_button.clicked.connect(reload_manifest)

insert_data=QtWidgets.QPushButton("Add new label data")




# def reload_manifest():
#     print("--- Reloading UI ---")
    
#     # Clear all widgets from the manifest layout
#     while h_layout_manifest.count():
#         child = h_layout_manifest.takeAt(0)
#         if child.widget():
#             child.widget().deleteLater()
    
#     # Reload the data manager (if needed)
#     try:
#         global data, navigator
#         data = DataManager(root_dir)
#         navigator.data_manager = data  # Update the navigator's data manager
#     except ValueError:
#         print("Error reloading data")
#         return
    
#     # Recreate the manifest box with updated data
#     add_manifest_box(h_layout_manifest, navigator.data_manager.manifest)
#     print("Manifest widgets reloaded successfully")


# def add_new_data():
#     text, ok = QInputDialog.getText(main, 'Add New Label', 'Enter label name:')
#     if ok and text:
#         print(f"Adding new label: {text}")
#         # Add your logic here to add the new label to the data manager
#         # Then reload the manifest
#         reload_manifest()





# MANIFEST LOGIC
h_layout_manifest = QtWidgets.QVBoxLayout()
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