# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 10:06:46 2023

@author: gabri
"""
from pathlib import Path
import geopandas as gpd
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import re
import os

grower = 'Bland'
grower_g_drive = 'Anthony Bland'
direc = r'C:\Users\gabri\Desktop\Vayda\data\MVP\partner_farms\\'
direc_g_drive = r'G:\Shared drives\Vayda Team\MVP Grower Services\3 - Customer Data\\'

grower_dir = os.path.join(direc, grower)
grower_dir_g_drive = os.path.join(direc_g_drive, grower_g_drive)

# Read in the boundary file
bounds = gpd.read_file(os.path.join(grower_dir, 'fields', 'all_fields.gpkg'))

# Read in SSURGO files
files_dir = os.path.join(grower_dir, 'ssurgo')
pattern = '*.gpkg'

path_list = list(Path(files_dir).glob(pattern))

files_list = {}
for path in path_list:
    dt = gpd.read_file(path)
    joined = gpd.sjoin(dt, bounds, how='inner', predicate='intersects')
    files_list[path] = joined


# Objects within dictionary can be retrieved via [] and not {} like is used to create them
files_list[path_list[0]]
files_list[path_list[0]].columns

pattern = r"ssurgo\\(.+?)\.gpkg"

extracted_strings = {}

for path in path_list:
    path = str(path)
    match = re.search(pattern, path)
    if match:
        extracted_strings[path] = match.group(1)   
    else:
        print("No match found.")

variables = list(extracted_strings.values())
inverted_dict = {value: key for key, value in extracted_strings.items()}


# Increases font size for all text in the figure
plt.rcParams.update({'font.size': 13})
plt.ioff()

for var in variables:
    farms = files_list[path_list[0]]['Farm'].unique()
    column_to_plot = var
     
    # Creating the figure
    fig, ax = plt.subplots(figsize=(20, 20))

    data = files_list[Path(inverted_dict[column_to_plot])]
    subset_data = data

    subset_data.plot(column=column_to_plot, ax=ax, cmap='viridis', legend=True)

    ax.set_title(f'{column_to_plot}')
    ax.set_aspect('equal')
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))

    leg = ax.get_legend()
    leg.set_frame_on(True)
    leg.set_bbox_to_anchor((0.6, -0.2))
    ax.add_artist(leg)
    
    plt.savefig(
        f"{grower_dir}/ssurgo/{var}.png",
        bbox_inches="tight",
        pad_inches=3
    )
    
    plt.savefig(
        f"{grower_dir_g_drive}/ssurgo/{var}.png",
        bbox_inches="tight",
        pad_inches=3
    )
    

        

# Archived code to create the figures for each farm as facets. It does not look that nice though, as it is difficult to create a single legend for both figures.
for var in variables:
    # Creating the figure
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 16))
    axes = np.array(axes).flatten()
    
    farms = files_list[path_list[0]]['Farm'].unique()
    column_to_plot = var
     
    for i, ax in enumerate(axes):
        data = files_list[Path(inverted_dict[column_to_plot])]
        farm = farms[i]
      
        subset_data = data[data['Farm'] == farm]
        subset_data.columns
        subset_data.plot(column=column_to_plot, ax=ax, cmap='viridis', legend=True)
        
        plt.subplots_adjust(bottom=0.2)
                             
        ax.set_title(f'{farm} Farm - {column_to_plot}')
        ax.set_aspect(1)
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        
        leg = ax.get_legend()
        leg.set_frame_on(False)
        leg.set_bbox_to_anchor((0.6, -0.2))
        ax.add_artist(leg)
    
        plt.savefig(
            f"{grower_dir}/{var}.png",
            bbox_inches="tight",
            pad_inches=2
        )
        
        plt.savefig(
            f"{grower_dir_g_drive}/{var}.png",
            bbox_inches="tight",
            pad_inches=2
        )
    plt.show()

# Archived code to create one figure per farm. It did not seggregate correctly by farm so decided not to use it.
for var in variables:
    farms = files_list[path_list[0]]['Farm'].unique()
    column_to_plot = var
     
    for farm in farms:
        # Creating the figure
        fig, ax = plt.subplots(figsize=(20, 16))

        data = files_list[Path(inverted_dict[column_to_plot])]
        subset_data = data[data['Farm'] == farm]

        subset_data.plot(column=column_to_plot, ax=ax, cmap='viridis', legend=True)

        ax.set_title(f'{farm} Farm - {column_to_plot}')
        ax.set_aspect(1)
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))

        leg = ax.get_legend()
        leg.set_frame_on(True)
        leg.set_bbox_to_anchor((0.6, -0.2))
        ax.add_artist(leg)
        
        plt.savefig(
            f"{grower_dir}/ssurgo/{var}_{farm}.png",
            bbox_inches="tight",
            pad_inches=3
        )
