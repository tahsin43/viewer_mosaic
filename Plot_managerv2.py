# 1. Consolidated and corrected imports
import math
from collections import defaultdict
from pathlib import Path
from re import L
from typing import OrderedDict

import matplotlib.pyplot as plt
import nrrd
import numpy as np
from matplotlib.widgets import Button, Slider
from PIL import Image, ImageEnhance
from skimage import exposure
from matplotlib.figure import Figure
import pyqtgraph as pg


:
class PlotObjectv2:
    def __init__(self, image, mask, figure, main_container):
        self.image = image
        self.mask = mask
        self.figure = figure
        self.mask_visibility = True  # Default state
        self.main_container = main_container

    def create_sinle_image_and_mask_view(self,image_data,mask_data,alpha=0.5):
        image_view=pg.ImageView()
        image_view.seImage(image_data.T)
        image_view.ui.histogram.hide()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        plt.








        
