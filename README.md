markdown


# Inundation Shapefile Processing and Visualization

This project is designed to preprocess, process, and visualize inundation shapefiles, incorporating population density data and other relevant datasets. The code is modularized and can be used to generate various visualizations, such as stacked bar charts, line plots with shaded envelopes, and heatmaps.

## Installation

1. Clone the repository:
git clone [https://github.com/your-username/inundation-project.git](https://github.com/jjohnson2701/Connectivity_shp_followup.git)



2. Install the required dependencies:
pip install -r requirements.txt #coming soon

## Usage

The main script is `main.py`, which accepts the following command-line arguments:
usage: main.py [-h] [-i INPUT_DIRECTORIES [INPUT_DIRECTORIES ...]]
[-m MASK_DIR] [-o OUTPUT_FILE] [-f {bar,year,all}]

Process and analyze inundation shapefiles.

optional arguments:
-h, --help            show this help message and exit
-i INPUT_DIRECTORIES [INPUT_DIRECTORIES ...], --input_directories INPUT_DIRECTORIES [INPUT_DIRECTORIES ...]
Input directory paths
-m MASK_DIR, --mask_dir MASK_DIR
Mask directory path
-o OUTPUT_FILE, --output_file OUTPUT_FILE
Output shapefile path
-f {bar,year,all}, --graph_type {bar,year,all}
Type of graph to create (default: all)


To run the script, use the following command:
python main.py -i /path/to/input/dirs -m /path/to/mask/dir -o /path/to/output/file -f graph_type



Replace `/path/to/input/dirs` with the paths to the directories containing the input shapefiles, `/path/to/mask/dir` with the path to the directory containing the mask datasets (GHS_*.tif files), `/path/to/output/file` with the desired path for the output shapefile, and `graph_type` with one of the options: `bar`, `year`, or `all`.



### Mask Dataset Selection

When running the script, it will prompt you to select the mask datasets you want to use. You can either use all available datasets by typing `y` or select specific datasets by entering comma-separated indices or ranges (e.g., `1,3-5,7`).

### Example Usage
python main.py -i /data/input_dirs/dir1 /data/input_dirs/dir2 -m /data/mask_dir -o /data/output/result.shp -f all
