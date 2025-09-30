import sys
from PyQt5.QtCore import Qt

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
from PIL import Image, ImageEnhance
from PIL import Image, ImageEnhance
from skimage import exposure
from matplotlib.widgets import Button
from pyqtgraph.Qt import QtWidgets

from dataclasses import dataclass
from typing import List, Any  #
import math
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
    QTextEdit,
    QLabel,
)


import pyqtgraph as pg

pg.setConfigOption("imageAxisOrder", "row-major")
pg.setConfigOptions(useOpenGL=True)
#
# root_dir = "/Users/tahsin/tram/archive/June-28-2025/miller"
#
#
# data = DataManager(root_dir)
# manifest = data.get_Manifest()
#
# gen_data = (d for d in data)
#
# vol, seg = next(gen_data)
#
# vol_array = vol[0]
# seg_array = seg[0]
#
# vol, seg = (
#     nrrd.read(manifest[0]["vol"], index_order="C"),
#     nrrd.read(manifest[0]["seg"], index_order="C"),
# )
# vol_array = vol[0]
# seg_array = seg[0]
#
#
# vol_test, seg_test = vol_array[10, :, :], seg_array[10, :, :]
# print(vol_test)
# print(vol_test.shape)
#

# num_slices = vol_array.shape[0]


@dataclass
class ImageData:
    vol_item: np.ndarray
    mask_item: np.ndarray
    visible: bool = True  # Add default value with type annotation
    mask_imageItem = []


class PlotNavigator:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self._position = 0  # Start at the first __getitem__
        data_len = len(data_manager)
        # self.imageDatas: List[ImageData] = [None] * data_len  # Preallocate list
        self.current_mask = None

    @property
    def position(self):
        """Returns the current index."""
        return self._position

    def current(self):
        vol, seg = self.load_data()
        vol_array, seg_array = vol, seg
        num_slices = vol_array.shape[0]
        cols = math.ceil(math.sqrt(num_slices))
        renderer = SliceRenderer(win, cols)
        image_data = renderer.render_volume_slices(vol_array, seg_array)
        self.current_mask = image_data
        # we will store cache later, lets just get next and back working
        return self.current_mask

    def load_data(self):
        vol, seg = self.data_manager[self._position]
        return vol, seg

    # def hide_mask(self, position):
    #     #current_data = self.imageDatas[position]
    #     if current_data is not None:
    #         for vol in current_data.vol_item:
    #             vol.setVisible(False)
    #
    #         for mask in current_data.mask_item:
    #             mask.setVisible(False)

    # def show_current_masks(self, position):
    #     current_data = self.current_mask

    def next(self):
        self.current_mask = None
        """Moves to the next item and returns it."""
        if self._position >= len(self.data_manager) - 1:
            self._position = 0

            return self.current()
        self._position += 1

        return self.current()

    def back(self):
        """Moves to the previous item and returns it."""
        self.current_mask = None
        if self._position <= 0:
            self._position = len(self.data_manager) - 1

            return self.current()
        print(self._position)
        self._position -= 1

        return self.current()

    # def seek(self, index: int):
    #     """Jumps directly to a specific index."""
    #     # We can leverage the DataManager's bounds checking
    #     if not 0 <= index < len(self.data_manager):
    #         raise IndexError(f"Seek index {index} is out of range.")
    #     self._position = index
    #     return self.current()

    def getImagedata(self):
        return self.current_mask


class SliceRenderer:
    """Handles all the plotting/rendering logic"""

    def __init__(
        self,
        win: pg.GraphicsLayoutWidget,
        cols: int = 5,
    ):
        self.win = win
        self.cols = cols

    def render_volume_slices(
        self, vol_array: np.ndarray, seg_array: np.ndarray
    ) -> ImageData:
        """Creates ImageData with all rendered slices"""

        image_data = ImageData(vol_array, seg_array)

        image_data.visible = True

        # Clear existing plots
        num_slices = vol_array.shape[0]
        for i in range(num_slices):
            row = i // self.cols
            col = i % self.cols
            vb = self.win.addViewBox(row=row, col=col)

            # Volume image
            # store list in image_data

            img_item = pg.ImageItem(np.flip(vol_array[i, :, :], 0))
            vb.addItem(img_item)
            vb.setAspectLocked(True)
            shape = seg_array.shape

            # Mask overlay
            mask_array = np.flip(seg_array[i], 0)
            rgba_mask = np.zeros((shape[1], shape[2], 4), dtype=np.ubyte)
            rgba_mask[..., 0] = 255  # RED
            rgba_mask[..., 1] = 0  # GREEN
            rgba_mask[..., 2] = 0  # BLUE
            rgba_mask[..., 3] = (mask_array * 120).astype(np.ubyte)  # ALPHA

            mask_item = pg.ImageItem(rgba_mask)
            vb.addItem(mask_item)
            image_data.mask_imageItem.append(mask_item)

        return image_data


app = QtWidgets.QApplication([])
main = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout(main)
output_label = QLabel("Index 0")

layout.addWidget(output_label)
win = pg.GraphicsLayoutWidget()
layout.addWidget(win)

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
navigator = PlotNavigator(data)

navigator.current()

current_data = navigator.getImagedata()


def toggle_all_masks():
    new_visible_state = not current_data.visible
    current_data.visible = new_visible_state

    # Apply the new state to all mask items
    for mask in current_data.mask_imageItem:
        mask.setVisible(new_visible_state)

    print(f"New visible state: {new_visible_state}")


def next_volume():
    global current_data
    current_data = navigator.next()
    execute_logic(output_label, navigator._position)


def prev_volume():
    global current_data
    current_data = navigator.back()
    execute_logic(output_label, navigator._position)


def execute_logic(output_label, position):
    message = f"Index Position {position} !"
    output_label.setText(message)


toggle_button = QtWidgets.QPushButton("Toggle Masks")
next_button = QtWidgets.QPushButton("Next Volume")
prev_button = QtWidgets.QPushButton("Previous Volume")

layout.addWidget(toggle_button)
layout.addWidget(next_button)
layout.addWidget(prev_button)
toggle_button.clicked.connect(toggle_all_masks)
next_button.clicked.connect(next_volume)
prev_button.clicked.connect(prev_volume)

main.show()
app.exec_()
