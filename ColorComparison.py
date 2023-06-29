import cv2
import numpy as np
import matplotlib.pyplot as plt

def get_main_colors(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Reduce each color channel to 2 bits
    reduced_color_image = image // 64
    # Flatten the image and compute color counts
    flattened_image = reduced_color_image.reshape(-1, 3)
    unique_colors, counts = np.unique(flattened_image, axis=0, return_counts=True)
    # Sort colors by their count
    sorted_indices = np.argsort(-counts)
    unique_colors = unique_colors[sorted_indices]
    counts = counts[sorted_indices]

    return unique_colors, counts