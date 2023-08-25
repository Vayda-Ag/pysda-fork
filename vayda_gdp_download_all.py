# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 10:39:28 2023

@author: gabri
"""
from sdapoly import shp
from sdaprop import getprop
from pathlib import Path
import geopandas as gpd
import os as os
from natsort import index_natsorted
from numpy import argsort
from shapely.geometry import Polygon


# Function to remove Z coordinates from a geometry
# Define SSURGO_CLASSES and other necessary definitions here
SSURGO_CLASSES = {
    "taxclname": {
        "methods": ["dom_comp_cat", "dom_cond"],
        "name": "taxonomic_classification_name",
        "type": "varchar",
        "title": "Taxonomic Classification"
    },
    "drainagecl": {
        "methods": ["dom_comp_cat", "dom_cond"],
        "name": "drainage_class",
        "type": "varchar",
        "title": "Drainage Classification"
    },
    "flsoilleachpot": {
        "methods": ["dom_comp_cat", "dom_cond"],
        "name": "fl_soil_leaching_potential",
        "type": "varchar",
        "title": "Soil Erodibility Factor RF"
    },
    "wtdepannmin": {
        "methods": ["muaggatt"],
        "name": "wtdepth_annual_min",
        "type": "integer",
        "title": "Water Table Depth Annual - Minimum (cm)"
    },
    "wtdepaprjunmin": {
        "methods": ["muaggatt"],
        "name": "wtdepth_apr_jun_min",
        "type": "integer",
        "title": "Water Table Depth April/June - Minimum (cm)"
    },
    "dbovendry_r": {
        "methods": ["wtd_avg"],
        "name": "bulk_density_oven_dry",
        "type": "float",
        "title": "Bulk Density (g/cm3)"
    },
    # "resdept": {
    #     "methods": None,
    #     "name": "restriction_depth_to_top",
    #     "type": "integer",
    #     "title": "Top Depth"
    # },
    "flodfreqdcd": {
        "methods": ["muaggatt"],
        "name": "flodfreq_dcd",
        "type": "varchar",
        "title": "Flooding Frequency - Dominant Condition"
    },
    "awc_r": {
        "methods": ["wtd_avg", "dom_comp_num"],
        "name": "available_water_capacity",
        "type": "float",
        "title": "Available Water Capacity (cm/cm)"
    },
    "kffact": {
        "methods": ["wtd_avg", "dom_comp_num"],
        "name": "soil_erodibility_factor_rf",
        "type": "varchar",
        "title": "Soil Erodibility Factor RF"
    },
    "weg": {
        "methods": ["dom_comp_cat", "dom_cond"],
        "name": "wind_erodibility_group",
        "type": "varchar",
        "title": "Wind Erodibility Group"
    },
    "farmlndcl": {
        "methods": ["dom_comp_cat", "dom_cond"],
        "name": "farmland_classification",
        "type": "varchar",
        "title": "Farm Classification"
    },
    "cec7_r": {
        "methods": ["wtd_avg", "dom_comp_num"],
        "name": "cation_exch_capcty_nh4oacph7",
        "type": "float",
        "title": "CEC-7 (cmol(+)/kg)"
    },
    "om_r": {
        "methods": ["wtd_avg", "dom_comp_num"],
        "name": "organic_matter_percent",
        "type": "float",
        "title": "Organic Matter (Percent)"
    },
    "claytotal_r": {
        "methods": ["wtd_avg", "dom_comp_num"],
        "name": "clay_total_separate",
        "type": "float",
        "title": "Total Clay (Percent)"
    },
    "silttotal_r": {
        "methods": ["wtd_avg", "dom_comp_num"],
        "name": "silt_total_separate",
        "type": "float",
        "title": "Total Silt (Percent)"
    },
    "sandtotal_r": {
        "methods": ["wtd_avg", "dom_comp_num"],
        "name": "sand_total_separate",
        "type": "float",
        "title": "Total Sand (Percent)"
    }
}

## Read in .gpkg files 
# files_list = list(Path(r"C:\Users\gabri\Documents").glob("*.gpkg"))

# Extract farm names between "Goldcrest_" and .gpkg
# files_substrings = [
 #   str(file_path.stem).split("Goldcrest_", 1)[-1]
 #   for file_path in files_list
#]

# fields = ["Goldcrest_" + name for name in files_substrings]
fields = ["Goldcrest_Baicy","Goldcrest_Bee_Lake","Goldcrest_Bell_Quail",
          "Goldcrest_Blue_Bayou","Goldcrest_Bolivar","Goldcrest_Clover_Blend",
          "Goldcrest_Coldwater","Goldcrest_Coldwater_Planting_Co","Goldcrest_Crown_Mill",
          "Goldcrest_Drew_County","Goldcrest_Eaglenest","Goldcrest_Field_Lake",
          "Goldcrest_Hatch_Lake","Goldcrest_Kitchens","Goldcrest_Morgan_Brake",
          "Goldcrest_Plum_Bayou","Goldcrest_South_Brinkley","Goldcrest_Swan_Lake",
          "Goldcrest_Yazoo_River"]
direc = Path(r"C:\Users\gabri\Desktop\Vayda\data\MVP\partner_farms")


    
# Loop to download SSURGO data for each property in the portfolio, as determined by the 'fields' list.    
for field in fields:
    
    # Creates SSURGO directory if it does not yet exist    
    lp_direc = os.path.join(direc, field + "\\ssurgo")
    os.makedirs(lp_direc , exist_ok=True)


    
    # Find the directory for the boundaries of each property
    file_path = os.path.join(direc, field, "fields\\all_fields.gpkg")
        
    # Load the AOI as a GeoDataFrame
    aoi = gpd.read_file(file_path)
    aoi= gpd.GeoDataFrame(aoi)

    # aoi['geometry'] = aoi['geometry'].apply(lambda geom: Polygon([(x, y) for x, y, z in geom.exterior.coords])) 
    
    
    columns_to_remove = ['Name', 'description', 'begin', 'end', 'altitudeMode', 'tessellate', 'extrude', 'visibility', 'drawOrder', 'icon', 'timestamp']

    columns_to_drop = [col for col in columns_to_remove if col in aoi.columns]
    aoi = aoi.drop(columns=columns_to_drop)
    
    
    # Define the output directory for transformed shapefiles
    output_path = os.path.join(direc, field, "ssurgo")

    # Transform AOI to a shapefile and save it
    shapefile_path = os.path.join(direc, field, "fields\\all_fields.shp")
    aoi.to_file(shapefile_path, driver='ESRI Shapefile')

    # Read back the transformed shapefile as a GeoDataFrame
    aoi = gpd.read_file(shapefile_path)
                       
    for class_name, ssurgo_class in SSURGO_CLASSES.items():
        method = ssurgo_class["methods"][0]

        if method == "muaggatt":
            top = None
            bottom = None
            prop = None
        else:
            top = 0
            bottom = 100
            prop = class_name

        data = getprop(
            df=aoi,
            column="mukey",
            method=method,
            top=top,
            bottom=bottom,
            prop=prop,
            minmax=None,
            prnt=False,
            meta=True
        )
        
        aoi_cols = aoi.columns.tolist()
        data_cols = data.columns.tolist()
        drop_cols = [col for col in data_cols if col in aoi_cols and col != "mukey"]
        data.drop(columns=drop_cols, inplace=True)
        merged_data = aoi.merge(data, how="inner", on="mukey")

        
        merged_data = merged_data.sort_values(
            by=class_name,
            key=lambda x: argsort(index_natsorted(merged_data[class_name]))
        )
        
        # Saving logic removed for simplicity

        merged_data.to_file(
            filename=f"{output_path}/{class_name}.gpkg",
            driver="GPKG"
        )
