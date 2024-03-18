import geopandas as gpd
import glob
import rasterio
from rasterio import windows
import pyproj
from tqdm import tqdm

def find_largest_extent(input_directories):
    largest_extent = None
    largest_file = None

    for directory in input_directories:
        reprojected_files = glob.glob(os.path.join(directory, '*connectivity_reprojected.shp'))
        for file_path in reprojected_files:
            gdf = gpd.read_file(file_path)
            extent = gdf.total_bounds
            area = (extent[2] - extent[0]) * (extent[3] - extent[1])

            if largest_extent is None or area > largest_extent:
                largest_extent = area
                largest_file = file_path

    print(f"Using the extent from the file: {os.path.basename(largest_file)}")
    return gpd.read_file(largest_file).total_bounds

def get_mask_datasets(mask_dir):
    mask_datasets = glob.glob(os.path.join(mask_dir, 'GHS_*.tif'))
    print("Available mask datasets:")
    for i, dataset in enumerate(mask_datasets):
        print(f"{i+1}. {os.path.basename(dataset)}")

    confirm = input(f"Do you want to use all {len(mask_datasets)} datasets? (y/n) ").lower()
    if confirm == 'y':
        return mask_datasets
    else:
        print("Please select the datasets you want to use (comma-separated indices or ranges, e.g., 1,3-5,7):")
        selected_indices = input("> ")
        selected_datasets = []
        for index_range in selected_indices.split(','):
            if '-' in index_range:
                start, end = map(int, index_range.split('-'))
                selected_datasets.extend(mask_datasets[start-1:end])
            else:
                selected_datasets.append(mask_datasets[int(index_range)-1])
        return selected_datasets

def preprocess_shapefiles(input_directories, mask_datasets, output_file, extent):
    for mask_dataset in mask_datasets:
        mask_name = os.path.basename(mask_dataset).split(':')[0]
        print(f"Preprocessing for mask dataset: {mask_name}")

        with rasterio.open(mask_dataset) as src:
            for directory in input_directories:
                reprojected_files = glob.glob(os.path.join(directory, '*connectivity_reprojected.shp'))
                for reprojected_file in tqdm(reprojected_files, desc=f"Masking files in {directory}"):
                    gdf = gpd.read_file(reprojected_file)
                    cropped_raster_path = os.path.join(output_file, f"{os.path.basename(reprojected_file)}_{mask_name}_cropped_raster.shp")
                    crop_and_convert_raster(src, extent, cropped_raster_path, crs=src.crs.to_string(), population_threshold=75)
                    cropped_raster_gdf = gpd.read_file(cropped_raster_path)
                    masked_gdf = gpd.overlay(gdf, cropped_raster_gdf, how='intersection')
                    masked_file = os.path.join(output_file, os.path.basename(reprojected_file.replace('_reprojected.shp', f'_{mask_name}_masked_reprojected.shp')))
                    masked_gdf.to_file(masked_file, driver='ESRI Shapefile')
                    os.remove(cropped_raster_path)

def crop_and_convert_raster(raster_src, extent, output_shapefile_path, crs='EPSG:3857', population_threshold=None):
    with raster_src:
        affine = raster_src.transform
        src_crs = raster_src.crs
        left, bottom, right, top = extent
        window = windows.from_bounds(left, bottom, right, top, raster_src.transform)
        cropped_raster = raster_src.read(1, window=window, masked=True)

        if cropped_raster.mask.all():
            print(f"Warning: The cropped raster for the extent {extent} is completely masked (no data).")
            return

        dest_crs = pyproj.CRS(crs)
        reproj_raster, reproj_transform = rasterio.warp.reproject(
            source=cropped_raster.data,
            src_transform=affine,
            src_crs=src_crs,
            dst_crs=dest_crs,
            dst_transform=rasterio.warp.calculate_default_transform(
                src_crs, dest_crs, cropped_raster.shape[1], cropped_raster.shape[2], left, bottom, right, top
            ),
            resampling=rasterio.warp.Resampling.nearest
        )

        gdf = rasterio.features.raster_to_vector(reproj_raster, reproj_transform, dest_crs)

        if population_threshold:
            gdf = gdf[gdf['DN'] > population_threshold]

        gdf.to_file(output_shapefile_path, driver='ESRI Shapefile')