import argparse
from preprocessing import preprocess_shapefiles, get_mask_datasets
from processing import process_shapefiles
from visualization import create_graphs

def main():
    parser = argparse.ArgumentParser(description='Process and analyze inundation shapefiles.')
    parser.add_argument('-i', '--input_directories', nargs='+', help='Input directory paths')
    parser.add_argument('-m', '--mask_dir', type=str, help='Mask directory path')
    parser.add_argument('-o', '--output_file', type=str, required=False, help='Output shapefile path')
    parser.add_argument('-f', '--graph_type', type=str, default='all', choices=['bar', 'year', 'all'], help='Type of graph to create (default: all)')
    args = parser.parse_args()

    input_directories = args.input_directories
    mask_datasets = get_mask_datasets(args.mask_dir)
    output_file = args.output_file

    extent = find_largest_extent(input_directories)
    preprocess_shapefiles(input_directories, mask_datasets, output_file, extent)

    area_summary, processed_file = process_shapefiles(input_directories, output_file)

    for mask_dataset in mask_datasets:
        dataset_name = os.path.basename(mask_dataset).split(':')[0]
        create_graph_func = getattr(visualization, f'create_graph_{dataset_name}', None)
        if create_graph_func:
            create_graph_func(area_summary, processed_file, args.graph_type, mask_dataset)
        else:
            print(f"No 'create_graph' function found for dataset: {dataset_name}")

if __name__ == '__main__':
    main()