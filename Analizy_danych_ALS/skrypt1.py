import open3d as o3d
import numpy as np
import laspy
from matplotlib import cm
import matplotlib.pyplot as plt
from collections import Counter
import argparse

parser = argparse.ArgumentParser(description="Wizualizacja chmury punktów LAS/LAZ.")
parser.add_argument("file_path", type=str, help="Ścieżka do pliku LAS/LAZ")
args = parser.parse_args()

point_cloud_path = args.file_path

point_cloud = laspy.read(point_cloud_path)
class_counts = Counter(point_cloud.classification)
classes = sorted(class_counts.keys())
counts = [class_counts[cls] for cls in classes]
plt.figure(figsize=(10, 6))
bars = plt.bar(classes, counts, color='skyblue', edgecolor='black')
for bar, count in zip(bars, counts):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height, str(count), ha='center', va='bottom', fontsize=10)

plt.xlabel('Klasa ')
plt.title('Liczba punktów w poszczególnych klasach')
plt.xticks(classes)  
plt.gca().axes.get_yaxis().set_visible(False)  
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

points = np.vstack((point_cloud.x, point_cloud.y, point_cloud.z)).transpose()
classification = point_cloud.classification

mask = ~np.isin(classification, [7, 12])
filtered_points = points[mask]
filtered_classification = classification[mask]

class_colors = {
    0: [0.5, 0.5, 0.5],  
    2: [0.0, 1.0, 0.0],  
    3: [0.0, 0.5, 0.0],  
    4: [0.5, 0.25, 0.0], 
    5: [0.0, 0.0, 1.0],  
    6: [1.0, 0.0, 0.0],  
    9: [0.0, 1.0, 1.0]  
}

default_color = [0.0, 0.0, 0.0]  
filtered_colors = np.array([class_colors.get(cls, default_color) for cls in filtered_classification])

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(filtered_points)
pcd.colors = o3d.utility.Vector3dVector(filtered_colors)

o3d.visualization.draw_geometries([pcd], window_name="Wizualizacja 3D bez szumów")
