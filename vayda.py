from sdapoly import shp
from sdaprop import getprop
from matplotlib import pyplot
from argparse import ArgumentParser
from pathlib import Path
from natsort import index_natsorted
from numpy import argsort


# python3 vayda.py --shape-file-path /Users/arahav/Downloads/MSHUB_Boundaries.shp --output-directory /Users/arahav/Downloads/ssurgo_data --ssurgo-class-name weg

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
    help="The directory where the data generated from ssurgo will be written to.",
    required=True
)
parser.add_argument(
    "--ssurgo-class-name",
    help="The SSURGO class name to retrieve data for.",
    default="taxclname",
    choices=list(SSURGO_CLASSES.keys())
)
args = parser.parse_args()

aoi = shp(args.shape_file_path)
ssurgo_class = SSURGO_CLASSES[args.ssurgo_class_name]
method = ssurgo_class["methods"][0]

if method == "muaggatt":
    top = None
    bottom = None
    prop = None
else:
    top = 0
    bottom = 100
    prop = args.ssurgo_class_name

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


# ValueError: Unknown aggregation method. Specify one of the following: "wtd_avg","dom_comp_cat","dom_comp_num","dom_cond","minmax","muaggatt"

# remove duplicate columns, join/merge the results, show first record
aoi_cols = aoi.columns.tolist()
data_cols = data.columns.tolist()
drop_cols = [col for col in data_cols if col in aoi_cols and col != "mukey"]
data.drop(columns=drop_cols, inplace=True)
merged_data = aoi.merge(data, how="inner", on="mukey")

merged_data = merged_data.sort_values(
    by=args.ssurgo_class_name,
    key=lambda x: argsort(index_natsorted(merged_data[args.ssurgo_class_name]))
)
merged_data.head(1)

# merged_data[args.ssurgo_class_name] = "(" + getattr(merged_data, args.ssurgo_class_name) + ")" + " " + merged_data.muname
fig, ax = pyplot.subplots(1, 1)
fig.set_size_inches(6, 6)

merged_data.plot(
    column=args.ssurgo_class_name,
    ax=ax,
    cmap="rainbow",
    legend=True
)

# numerical and gradient if we have > 15 "classes". for integers/floats

# add a legend
leg = ax.get_legend()
leg._set_loc(2)
leg.set_frame_on(False)
leg.set_bbox_to_anchor((0.5, 0.55))
ax.set(title=ssurgo_class["title"])

pyplot.axis("off")
pyplot.axis("tight")
pyplot.axis("image")

Path(args.output_directory).mkdir(exist_ok=True, parents=True)

pyplot.savefig(
    f"{args.output_directory}/{args.ssurgo_class_name}.svg",
    format="svg",
    bbox_inches="tight"
)

pyplot.savefig(
    f"{args.output_directory}/{args.ssurgo_class_name}.png",
    bbox_inches="tight"
)

merged_data.to_file(
    filename=f"{args.output_directory}/{args.ssurgo_class_name}.gpkg",
    driver="GPKG"
)
