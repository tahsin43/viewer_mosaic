# 1. Consolidated and corrected imports
import math
from collections import defaultdict
from pathlib import Path
from typing import OrderedDict

import matplotlib.pyplot as plt
import nrrd
import numpy as np
from matplotlib.widgets import Button, Slider
from PIL import Image, ImageEnhance
from skimage import exposure
from matplotlib.figure import Figure

# Assuming data_manager.py contains these classes
# from data_manager import DataManager, DataManagerNavigator


class PlotObject:
    def __init__(self, image, mask, figure, canvas):
        self.image = image
        self.mask = mask
        self.figure = figure
        self.canvas = canvas
        self.mask_artists = []  # Changed to plural for clarity
        self.mask_visibility = True  # Default state

        # The object now draws itself upon creation
        self.visualize_all_image_and_mask()

    def plot_enhanced_image_on_ax(
        self,
        ax,
        image_data,
        mask_data,
        title="",
        alpha=0.5,
    ):
        """
        Enhances and plots a single image and its mask onto a provided matplotlib axis.
        """
        if image_data is None:
            ax.set_title("Invalid Image")
            ax.axis("off")
            return None

        # 1. Rescale intensity for better contrast
        p2, p98 = np.percentile(image_data, (2, 98))
        # rescaled_img = exposure.rescale_intensity(image_data, in_range=(p2, p98))

        # 2. Convert to PIL Image for further enhancement
        # Correctly use the rescaled image data for enhancement
        # pil_img = Image.fromarray(rescaled_img.astype(np.uint8), mode="L")

        # 3. Apply contrast enhancement
        # enhancer = ImageEnhance.Contrast(pil_img)
        # enhanced_img = enhancer.enhance(1.2)

        # 4. Plotting on the provided axis
        ax.imshow(image_data, cmap="gray")  # Use 'gray' for grayscale images
        masked_data = np.ma.masked_where(mask_data == 0, mask_data)

        mask_artist = ax.imshow(
            masked_data, alpha=alpha, cmap="viridis", visible=self.mask_visibility
        )
        ax.set_title(title)
        ax.axis("off")

        return mask_artist

    def visualize_all_image_and_mask(self):
        """
        Uses the object's figure to create subplots and display all images and masks.
        """
        self.figure.clear()  # Clear the figure before drawing

        num_images = self.image.shape[0]
        n_dim = math.ceil(math.sqrt(num_images))

        # Use the figure associated with this object, don't create a new one
        axes = self.figure.subplots(n_dim, n_dim).flatten()

        self.mask_artists = []  # Reset the list of artists
        for i in range(num_images):
            mask_artist = self.plot_enhanced_image_on_ax(
                ax=axes[i], image_data=self.image[i], mask_data=self.mask[i]
            )
            if mask_artist:
                self.mask_artists.append(mask_artist)

        # Turn off any unused axes
        for j in range(num_images, len(axes)):
            axes[j].axis("off")

        self.figure.tight_layout(pad=1.0, w_pad=0.1, h_pad=0.1)
        self.canvas.draw_idle()

    def plot_image(
        self,
    ):
        self.canvas.figure = self.figure
        self.canvas.draw_idle()

    def set_mask_visibility(self, visible):
        """
        Sets the mask visibility state and updates the plot.
        """
        self.mask_visibility = visible
        # Iterate through all mask artists for this plot object
        for artist in self.mask_artists:
            artist.set_visible(self.mask_visibility)

        if self.canvas:
            self.canvas.draw_idle()


class PlotManager:
    def __init__(self, shared_canvas, datamanager_navigator):
        self.canvas = shared_canvas
        self.datamanager_navigator = datamanager_navigator
        self.cache = OrderedDict()  # A standard dictionary is often sufficient
        self.active_plot_instance = None
        self.canvas.draw_idle()

    def display_plot(self):
        """
        Main method to display a plot.
        Fetches from cache or creates a new PlotObject and displays it.
        """
        index = self.datamanager_navigator.position

        print("this is the index in PlotMAnager", index)
        if index in self.cache:
            print("found in cahce")
            plot_obj = self.cache[index]
            print(plot_obj)
            print("this is the shape of image and mask")
            print(plot_obj.image.shape, plot_obj.mask.shape)
            plot_obj.plot_image()
        else:
            # Assuming the navigator has a method to get data by index
            # This part needs to be adapted to your DataManagerNavigator's API
            image, mask = self.datamanager_navigator.current()
            print("not found in cach, adding in caceh from postioin", index)

            print(image.shape, mask.shape)

            # Create a new plot object, which will automatically draw on the figure
            figure = Figure(figsize=(15, 15))
            plot_obj = PlotObject(image, mask, figure, self.canvas)
            plot_obj.visualize_all_image_and_mask()

            self.cache[index] = plot_obj

        self.active_plot_instance = plot_obj
        # The plot object's __init__ already handles drawing, but an explicit redraw can be good
        self.canvas.draw_idle()

    def toggle_mask_visibility(self, is_visible):
        """Toggles the mask visibility of the currently active plot."""
        if self.active_plot_instance:
            self.active_plot_instance.set_mask_visibility(is_visible)

        else:
            print("No active plot to toggle mask visibility.")
