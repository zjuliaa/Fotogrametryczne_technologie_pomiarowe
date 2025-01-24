import laspy
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import argparse

def read_las(las):
    x, y, z = las.x, las.y, las.z
    points = np.float64([x, y, z]).T
    return points

def calculate_density(points, radius, density_mode):
    kdtree = cKDTree(points)
    neighbours_of_point = kdtree.query_ball_point(points[::100], r=radius, workers = -1)
    if density_mode == "2D":
        densities = [(len(neighbours))/(np.pi * radius**2) for neighbours in neighbours_of_point]
    elif density_mode == "3D":
        densities = [(len(neighbours))/(4/3 * np.pi * radius**3) for neighbours in neighbours_of_point]
    scaling_factor = len(points) / len(points[::100])
    return densities, scaling_factor


def plot_histogram(densities, scaling_factor, density_mode, ground_only):
    plt.figure(figsize=(10, 6))
    mode = density_mode.upper()
    counts, bins, _ = plt.hist(densities, bins=500, color='steelblue', edgecolor='black', alpha=0.7)
    plt.bar(bins[:-1], counts * scaling_factor, width=(bins[1] - bins[0]), color='steelblue', edgecolor='black', alpha=0.7)
    plt.xlabel(f'Gęstość punktów na {"m²" if mode == "2D" else "m³"}')
    plt.ylabel('Liczba punktów')
    plt.title(f'Histogram rozkładu gęstości punktów {"dla klasy gruntu" if ground_only else ""}')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Analiza gęstości chmury punktów z pliku LAS/LAZ.")
    parser.add_argument("las_file", type=str, help="Ścieżka do pliku LAS/LAZ.")
    parser.add_argument("--density_mode", choices=["2D", "3D"], default="2D", help="Tryb obliczania gęstości: '2D' (na metr kwadratowy) lub '3D' (na metr sześcienny). Domyślnie 2D.")
    parser.add_argument("--ground_only", action="store_true", help="Jeśli ustawione, analiza będzie przeprowadzona tylko dla klasy gruntu.")

    args = parser.parse_args()
    las = laspy.read(args.las_file)
    points = read_las(las)
    if args.ground_only:
        ground_mask = las.classification == 2
        points = points[ground_mask]
    translate_vector = las.header.min
    points_translated = points - translate_vector
    densities, scaling_factor = calculate_density(points_translated, radius=1.0, density_mode=args.density_mode)
    plot_histogram(densities, scaling_factor, density_mode=args.density_mode, ground_only=args.ground_only)

if __name__ == "__main__":
    main()

