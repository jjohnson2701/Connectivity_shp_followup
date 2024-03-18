import geopandas as gpd
import pandas as pd
import numpy as np
from tqdm import tqdm

def process_shapefiles(input_directories, output_file):
    gdfs = []

    for directory in input_directories:
        masked_files = glob.glob(os.path.join(directory, '*connectivity_masked_reprojected.shp'))

        for file_path in tqdm(masked_files, desc=f"Processing files in {directory}"):
            gdf = gpd.read_file(file_path)
            gdf_array = np.array(gdf)
            gdf = gpd.GeoDataFrame(gdf_array, geometry=gdf.geometry)
            gdfs.append(gdf)

    combined_gdf = pd.concat(gdfs, ignore_index=True)

    combined_gdf['Area'] = combined_gdf.geometry.area

    combined_gdf['SigmaLevel'] = combined_gdf['SigmaLevel'].replace({'msig': 'minus', 'psig': 'plus', 'Mean': 'middle'})

    area_summary = combined_gdf.groupby(['Year', 'VLM', 'SigmaLevel'])['Area'].sum().reset_index()

    area_summary['Area'] = area_summary['Area'] / 1000000

    area_summary = area_summary.sort_values(['Year', 'VLM', 'SigmaLevel'])

    print("Summed Areas:")
    for index, row in area_summary.iterrows():
        print(f"Year: {row['Year']}, VLM: {row['VLM']}, SigmaLevel: {row['SigmaLevel']}, Area: {row['Area']} sq km")

    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    combined_gdf.to_file(output_file, driver='ESRI Shapefile')

    area_summary.to_csv(output_file.replace('.shp', '.csv'), index=False)

    return area_summary, output_file