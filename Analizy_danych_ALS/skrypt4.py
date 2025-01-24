import laspy
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import argparse

def read_las(las):
    """Funkcja odczytująca punkty z pliku LAS/LAZ."""
    x, y, z = las.x, las.y, las.z
    return np.float64([x, y, z]).T

def main():
    parser = argparse.ArgumentParser(description="Wizualizacja chmury punktów LAS/LAZ z klasteryzacją budynków.")
    parser.add_argument("file_path", type=str, help="Ścieżka do pliku LAS/LAZ")
    args = parser.parse_args()

    las = laspy.read(args.file_path)
    points = read_las(las)
    building_indices = las.classification == 6
    ground_indices = las.classification == 2
    buildings = points[building_indices]
    ground = points[ground_indices]

    print("Przeprowadzanie klasteryzacji budynków...")
    building_cloud = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(buildings))
    clusters = building_cloud.cluster_dbscan(eps=2.0, min_points=100, print_progress=True)
    labels = np.array(clusters)
    max_label = labels.max()
    colors = plt.get_cmap("tab20")(labels / max_label if max_label > 0 else labels)
    colors[labels < 0] = [0.5, 0.5, 0.5, 1.0] 
    building_cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])

    ground_cloud = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(ground))
    ground_cloud.paint_uniform_color([0.6, 0.8, 0.6])  

    combined_cloud = ground_cloud + building_cloud
    o3d.visualization.draw_geometries([combined_cloud])

if __name__ == "__main__":
    main()
