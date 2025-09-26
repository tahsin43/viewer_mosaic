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


def plot_enhanced_image_on_ax(
    ax,
    image_data,
    mask_data,
    title="",
    alpha=0.5,
    brightness_factor=1.0,
    sharpness_factor=1.0,
    gamma=0.5,
):
    """
    Enhances and plots a single image and its mask onto a provided matplotlib axis.
    """
    if image_data is None:
        ax.set_title("Invalid Image")
        ax.axis("off")
        return

    # # 1. Normalize and convert to uint8 if the image is float
    # if image_data.dtype in [np.float32, np.float64]:
    #     image_data = (image_data * 255).astype(np.uint8)
    #
    # # 2. Apply enhancement pipeline
    # img_gamma_corrected = exposure.adjust_gamma(image_data, gamma=gamma)
    # img_pil = Image.fromarray(img_gamma_corrected, mode='L')
    # img_bright = ImageEnhance.Brightness(img_pil).enhance(brightness_factor)
    # final_image = np.array(img_enhanced_pil)
    # img_enhanced_pil = ImageEnhance.Sharpness(img_bright).enhance(sharpness_factor)

    # 3. Plotting on the provided axis
    p2, p98 = np.percentile(image_data, (2, 98))

    image_data = image_data.astype(np.uint8)
    enhanced = exposure.rescale_intensity(image_data, in_range=(p2, p98))
    enhanced = Image.fromarray(image_data, mode="L")

    enhanced_contrast = ImageEnhance.Contrast(enhanced)
    enhanced_img = enhanced_contrast.enhance(1.2)

    ax.imshow(enhanced_img, cmap="viridis")

    mask_artist = ax.imshow(
        mask_data, alpha=alpha, cmap="viridis"
    )  # Using 'viridis' for masks for better visibility
    ax.set_title(title)
    ax.axis("off")

    return mask_artist


def visualize_all_image_and_mask(image, mask):
    num_images = image.shape[0]
    n_dim = math.ceil(math.sqrt(num_images))
    fig, axes = plt.subplots(n_dim, n_dim, figsize=(n_dim * 5, n_dim * 5))
    axes = axes.flatten()
    mask_artist = []
    for i in range(num_images):
        mask_ = plot_enhanced_image_on_ax(
            ax=axes[i], image_data=image[i], mask_data=mask[i]
        )
        mask_artist.append(mask_)

    for j in range(num_images, len(axes)):
        axes[j].axis("off")
    fig.tight_layout(pad=1.0, w_pad=0.1, h_pad=0.1)
    ax_button = fig.add_axes([0.4, 0.02, 0.2, 0.05])

    def toggle_mask_visibility(event):
        for artist in mask_artist:
            artist.set_visible(not artist.get_visible())  # Toggle visibility
        fig.canvas.draw_idle()  #

    button = Button(ax_button, "Toggle Mask Visibility")
    button.on_clicked(toggle_mask_visibility)
    plt.show()
    return fig, axes, button


fig, axes, button_widget = visualize_all_image_and_mask(vol_array, seg_array)
