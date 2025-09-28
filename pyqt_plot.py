# this is a test to see how good pyqt plot is
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


import pyqtgraph as pg


root_dir = "/Users/tahsin/tram/archive/June-28-2025/miller"


data = DataManager(root_dir)
manifest = data.get_Manifest()

gen_data = (d for d in data)

vol, seg = next(gen_data)

vol_array = vol[0]
seg_array = seg[0]

vol, seg = (
    nrrd.read(manifest[0]["vol"], index_order="C"),
    nrrd.read(manifest[0]["seg"], index_order="C"),
)
vol_array = vol[0]
seg_array = seg[0]


dim = 10
vol_test, seg_test = vol_array[10, :, :], seg_array[10, :, :]
print(vol_test)
print(vol_test.shape)

app = QtWidgets.QApplication([])

# Create an ImageView instance
img_view = pg.ImageView()
img_view.setWindowTitle("PyQtGraph Image Viewer")

# Set the image data to the ImageView
img_view.setImage(vol_test)

# Show the ImageView widget. It will open as its own window.
img_view.show()

# Start the Qt event loop
app.exec_()
