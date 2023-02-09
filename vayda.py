from matplotlib import pyplot
import sdapoly, sdaprop

shape_file_path = "C:/Users/gabri/Desktop/Vayda/data/MSHUB/Fall 2022/Fields/boundaries.shp"
aoi = sdapoly.shp(shape_file_path)

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

# TODO: wtdepannmin, wtdepaprjunmin, flodfreqdcd
key_name = "cec7_r"
ssurgo_class = SSURGO_CLASSES[key_name]
method = ssurgo_class["methods"][0]

if method == "muaggatt":
    top = None
    bottom = None
    prop = None
else:
    top = 0 
    bottom = 100
    prop = key_name

data=sdaprop.getprop(
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
print(data)

# ValueError: Unknown aggregation method. Specify one of the following: 'wtd_avg','dom_comp_cat','dom_comp_num','dom_cond','minmax','muaggatt'

from natsort import index_natsorted
import numpy

# remove duplicate columns, join/merge the results, show first record
aoi_cols = aoi.columns.tolist()
data_cols = data.columns.tolist()
drop_cols = [col for col in data_cols if col in aoi_cols and col != 'mukey']
data.drop(columns = drop_cols, inplace = True)


merged_data = aoi.merge(data, how = 'inner', on = 'mukey')

merged_data = merged_data.sort_values(
    by=key_name,
    key=lambda x: numpy.argsort(index_natsorted(merged_data[key_name]))
)
merged_data.head(1)
print(merged_data)

# merged_data[key_name] = "(" + getattr(merged_data, key_name) + ")" + " " + merged_data.muname
fig, ax = pyplot.subplots(1,1)
fig.set_size_inches(6,6)

merged_data.plot(
    column=key_name,
    ax=ax,
    cmap="rainbow",
    legend=True
)

# numerical and gradient if we have > 15 "classes". for integers/floats

# add a legend
leg = ax.get_legend()
# print(leg.properties())
# print(dir(leg.legendHandles[0]))
leg._set_loc(2)
leg.set_frame_on(False)
leg.set_bbox_to_anchor((0.5, 0.55))
ax.set(title=ssurgo_class["title"])
print(ax.legend().texts)
ax.legend().update_from(leg)

pyplot.axis("off")
pyplot.axis("tight")
pyplot.axis("image")
handles, labels = ax.get_legend_handles_labels()
print(handles, labels)

pyplot.savefig(
    f"C:/Users/gabri/Desktop/Vayda/data/MVP/Regen Ag Plan 1.0/SUURGO/MSHUB/{key_name}.svg",
    format="svg",
    bbox_inches="tight"
)

pyplot.savefig(
    f"C:/Users/gabri/Desktop/Vayda/data/MVP/Regen Ag Plan 1.0/SUURGO/MSHUB/{key_name}.png",
    bbox_inches="tight"
)

merged_data.to_file(
    filename=f"C:/Users/gabri/Desktop/Vayda/data/MVP/Regen Ag Plan 1.0/SUURGO/MSHUB/{key_name}.gpkg",
    driver="GPKG"
)
