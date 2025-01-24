import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
import laspy
import argparse

def read_las(las):
    x, y, z = las.x, las.y, las.z
    points = np.float64([x, y, z]).T
    return points

def generate_raster_from_points(points, cell_size):
    x_min, y_min = np.min(points[:, 0]), np.min(points[:, 1])
    x_max, y_max = np.max(points[:, 0]), np.max(points[:, 1])
    cols = int(np.ceil((x_max - x_min) / cell_size))
    rows = int(np.ceil((y_max - y_min) / cell_size))
    origin = np.array([x_min, y_min])
    col_indices = ((points[:, 0] - origin[0]) / cell_size).astype(int)
    row_indices = ((points[:, 1] - origin[1]) / cell_size).astype(int)
    grouped_data = {}
    for idx, (col, row) in enumerate(zip(col_indices, row_indices)):
        key = (col, row)
        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(points[idx, 2])  
    raster = np.zeros((rows, cols))
    for (col, row), heights in grouped_data.items():
        raster[rows - 1 - row, col] = max(heights)  
    proj4_crs = "+proj=tmerc +lat_0=0 +lon_0=19 +k=0.9993 +x_0=500000 +y_0=-5300000 +ellps=GRS80 +units=m +no_defs"
    crs = CRS.from_proj4(proj4_crs)
    transform = from_origin(x_min, y_max, cell_size, cell_size)

    return raster, crs, transform

def save_raster(data, crs, transform, path):
    with rasterio.open(path,'w', driver='GTiff', count=1, dtype=data.dtype, width=data.shape[1], height=data.shape[0],
        crs=crs, transform=transform, nodata=-9999,
    ) as dst:
        dst.write(data, 1)

parser = argparse.ArgumentParser(description="Wizualizacja chmury punktów LAS/LAZ.")
parser.add_argument("file_path1", type=str, help="Ścieżka do pliku LAS/LAZ")
parser.add_argument("file_path2", type=str, help="Ścieżka do pliku LAS/LAZ")
parser.add_argument("output_path", type=str, help="Ścieżka do pliku wynikowego GeoTIFF")
args = parser.parse_args()

las_file1 = args.file_path1
las_file2 = args.file_path2
output_path = args.output_path
cell_size = 1.0


las1 = laspy.read(las_file1)
points1 = read_las(las1)
nmt_points1 = points1[las1.classification == 2]
nmpt_points1 = points1[np.isin(las1.classification, [2, 3, 4, 5, 6])]
nmt1, _, _ = generate_raster_from_points(nmt_points1, cell_size)
nmpt1, crs, transform = generate_raster_from_points(nmpt_points1, cell_size)

las2 = laspy.read(las_file2)
points2 = read_las(las2)
nmt_points2 = points2[las2.classification == 2]
nmpt_points2 = points2[np.isin(las2.classification, [2, 3, 4, 5, 6])]
nmt2, _, _ = generate_raster_from_points(nmt_points2, cell_size)
nmpt2, _, _ = generate_raster_from_points(nmpt_points2, cell_size)

difference_raster = nmpt1 - nmpt2
save_raster(difference_raster, crs, transform, output_path)

print(f"Raster różnicowy zapisany do {output_path}.")
