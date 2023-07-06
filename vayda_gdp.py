from sdapoly import shp
from sdaprop import getprop
from matplotlib import pyplot
from argparse import ArgumentParser
from pathlib import Path
from natsort import index_natsorted
from numpy import argsort
import os
import geopandas as gpd


# python3 vayda_gdp.py --shape-file-path C:/Users/gabri/Desktop/Vayda/data/MVP/partner_farms/Goldcrest_Green_River/fields/all_fields.gpkg --output-directory C:/Users/gabri/Desktop/Vayda/data/MVP/partner_farms/Goldcrest_Green_River/ssurgo



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
    "dbovendry": {
        "methods": ["muaggatt"],
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


parser = ArgumentParser()
parser.add_argument(
    "--shape-file-path",
    help="The local path to the farm/field boundaries shapefile.",
    required=True
)
parser.add_argument(
    "--output-directory",
    help="The directory where the data generated from SSURGO will be written to.",
    required=True
)
args = parser.parse_args()

bound_dir = os.path.dirname(args.shape_file_path)

# Check if the shape file path is a GeoPackage (.gpkg) file
if os.path.splitext(args.shape_file_path)[1].lower() == ".gpkg":
    # Convert GeoPackage to Shapefile
    output_shp = os.path.join(bound_dir, "all_fields.shp")
    data = gpd.read_file(args.shape_file_path)
    data.to_file(output_shp, driver="ESRI Shapefile")
    args.shape_file_path = output_shp  # Update the shape file path to the converted Shapefile

aoi = shp(args.shape_file_path)


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
    merged_data.head(1)

    fig, ax = pyplot.subplots(1, 1)
    fig.set_size_inches(6, 6)

    merged_data.plot(
        column=class_name,
        ax=ax,
        cmap="rainbow",
        legend=True
    )

    # Adjust the legend position and size
    leg = ax.get_legend()
    leg.set_frame_on(False)
    leg.set_bbox_to_anchor((1.02, 1))
    leg.set_title(ssurgo_class["title"])
    leg.get_title().set_fontsize(10)
    leg.get_title().set_fontweight('bold')
    
    # Set the figure title
    ax.set(title=ssurgo_class["title"])

   # Create the output directory if it doesn't exist
    Path(args.output_directory).mkdir(exist_ok=True, parents=True)

   # Save the figure as SVG and PNG
    # pyplot.savefig(
    #     f"{args.output_directory}/{class_name}.svg",
    #     format="svg",
    #     bbox_inches="tight"
    # )

    # pyplot.savefig(
    #     f"{args.output_directory}/{class_name}.png",
    #     bbox_inches="tight"
    # )

    merged_data.to_file(
        filename=f"{args.output_directory}/{class_name}.gpkg",
        driver="GPKG"
    )