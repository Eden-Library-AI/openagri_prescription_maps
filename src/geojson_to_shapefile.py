# Import libraries
import os
import sys
import json
import shutil
import argparse
import pandas as pd
from osgeo import ogr, osr


def generate_production_map_shapefile(input_geojson_path, output_dir):

    with open(input_geojson_path) as f:
        data = json.load(f)

    #print(data['metadata']) #TODO: Print to external metadata textfile
    
    # Normalize the JSON data
    geojson_df = pd.json_normalize(data['features'])

    # Split variety_id & yield_class into columns
    geojson_df['variety_id'] = geojson_df['properties'].apply(lambda x: x[0]['variety_id'])
    geojson_df['yield_class'] = geojson_df['properties'].apply(lambda x: x[0]['yield_class'])
    geojson_df = geojson_df.drop(columns=['type', 'geometry.type', 'properties'])

    # Convert each geoJSON cell into specific dictionary format for Shapefile conversion
    for variety_id in geojson_df['variety_id'].unique(): # Create separate Shapefiles for each variety
        geojson_df_filter_variety = geojson_df[geojson_df['variety_id'] == variety_id]

        cellgrid = []
        for index, row in geojson_df_filter_variety.iterrows():
            coords_list = row['geometry.coordinates'][0]
            coords_list = [{"lon": i[0], "lat": i[1]} for i in coords_list]
            cell = {"coordinates": coords_list, "yield_class": row['yield_class']}
            cellgrid.append(cell)

        print(f"Generating Shapefile for variety {variety_id}...", file=sys.stderr)
        session_variety_name = os.path.splitext(os.path.basename(input_geojson_path))[0] + f"_{variety_id}"
        output_path = os.path.join(output_dir, session_variety_name)
        os.makedirs(output_path, exist_ok=True)
        convert_to_shapefile(output_path, session_variety_name, cellgrid)
        shutil.make_archive(output_path, 'zip', output_path)
        shutil.move(output_path + '.zip', os.path.join(output_path, session_variety_name + '.zip'))
        
    print("Process completed successfully.", file=sys.stderr)


def convert_to_shapefile(output_path, session_variety_name, cellgrid):

    # Define the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # Create a new data source and layer
    data_source = driver.CreateDataSource(os.path.join(output_path, f"{session_variety_name}.shp"))

    # Create spatial reference
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(4326)  # WGS84

    # Create a polygon layer
    layer = data_source.CreateLayer("production_map", spatial_ref, ogr.wkbPolygon) # "fields_layer"

    # Create a field
    field = ogr.FieldDefn("Target Rat", ogr.OFTReal) # Fieldname must have fewer than 10 characters
    field.SetWidth(24)
    layer.CreateField(field)

    # Add polygons and their attributes to the layer
    for cell in cellgrid:
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for point in cell["coordinates"]:
            ring.AddPoint(point["lon"], point["lat"])

        polygon = ogr.Geometry(ogr.wkbPolygon)
        polygon.AddGeometry(ring)

        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(polygon)
        feature.SetField("Target Rat", round(cell["yield_class"], 4))

        layer.CreateFeature(feature)
        feature = None

    # Close the data source
    data_source = None

    print(f"Shapefile '{output_path}' created successfully.", file=sys.stderr)


if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Convert a GeoJSON file to a Shapefile.")
    parser.add_argument('--input_path', type=str, help='The path to the input GeoJSON file.')
    parser.add_argument('--output_dir', type=str, help='The path to the output Shapefile folder.')

    # Parse the arguments
    args = parser.parse_args()
    input_path = args.input_path
    output_dir = args.output_dir

    # Call the function with the parsed argument
    if input_path[0:3] == "prd":
        print("GeoJSON file is ELV Production Map")
        generate_production_map_shapefile(input_path, output_dir)
    