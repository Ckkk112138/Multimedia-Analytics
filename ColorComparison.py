import cv2
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from sklearn.cluster import KMeans

def get_main_colors_kmeans(image_path, num_colors=6):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    flattened_image = image.reshape(-1, 3)

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=num_colors, random_state=0)
    kmeans.fit(flattened_image)
    main_colors = kmeans.cluster_centers_.astype(int)

    # Calculate the proportion of each color in the image
    _, counts = np.unique(kmeans.labels_, return_counts=True)
    proportions = counts / counts.sum()

    return main_colors, proportions
