import pyqtgraph as pg

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

pg.setConfigOption("imageAxisOrder", "row-major")
pg.setConfigOptions(useOpenGL=True)


@dataclass
class ImageData:
    vol_item: np.ndarray
    mask_item: np.ndarray
    visible: bool = True  # Add default value with type annotation
    mask_imageItem = []


class PlotNavigator(QObject):
    position_changed = pyqtSignal(int)

    def __init__(self, data_manager: DataManager, win,renderer):
        super().__init__()
        self.data_manager = data_manager
        self.win = win
        self.renderer=renderer
        self._position = 0  # Start at the first __getitem__
        data_len = len(data_manager)
        # self.imageDatas: List[ImageData] = [None] * data_len  # Preallocate list
        self.current_mask = None
        self.visible = True

    @property
    def position(self):
        """Returns the current index."""
        return self._position

    def _clear_display(self):
        self.win.clear()  # This removes all items from the layout

        # Also clear the current_mask reference

    def current(self):
        self._clear_display()
        vol, seg = self.load_data()
        vol_array, seg_array = vol, seg
        num_slices = vol_array.shape[0]
        cols = math.ceil(math.sqrt(num_slices))
        self.renderer.cols = cols

        if self.current_mask is not None:
            self.current_mask.clear()
            self.current_mask = None

        image_data = self.renderer.render_volume_slices(vol_array, seg_array)
        self.current_mask = image_data
        # we will store cache later, lets just get next and back working
        return self.current_mask

    def load_data(self):
        vol, seg = self.data_manager[self._position]
        return vol, seg

    def next(self):
        """Moves to the next item and returns it."""
        if self._position >= len(self.data_manager) - 1:
            self._position = 0
            self.position_changed.emit(self._position)
            return self.current()
        self._position += 1
        self.position_changed.emit(self._position)
        return self.current()

    def back(self):
        """Moves to the previous item and returns it."""
        if self._position <= 0:
            self._position = len(self.data_manager) - 1
            self.position_changed.emit(self._position)  # ← Emit signal!
            return self.current()
        self.position_changed.emit(self._position)  # ← Emit signal!
        self._position -= 1

        return self.current()

    def getImagedata(self):
        return self.current_mask

    def goto(self, index):
        self._position = index
        print("goto function called")
        print("this is the index", index)
        self.position_changed.emit(self._position)  # ← Emit signal!
        return self.current()

    def toggle_all_masks(self):
        current_data = self.visible
        new_visible_state = not current_data
        self.visible = new_visible_state

        # apply the new state to all mask items
        #
        if self.current_mask is not None:
            for mask in self.current_mask:
                print(mask)
                mask.setVisible(self.visible)

        print(f"new visible state: {new_visible_state}")


class SliceRenderer:
    """Handles all the plotting/rendering logic"""

    def __init__(
        self,
        win: pg.GraphicsLayoutWidget,
        cols: int = 5,
    ):
        self.win = win
        self.cols = cols

    def render_volume_slices(self, vol_array: np.ndarray, seg_array: np.ndarray):
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
        return image_data.mask_imageItem
