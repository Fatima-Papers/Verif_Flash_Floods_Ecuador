import os
import numpy as np
import pandas as pd
import metview as mv

#####################################################################
# CODE DESCRIPTION
# 02_Plot_PointFR_EFFCI.py plots maps that show the location of point flood reports 
# exceeding considered EFFCI indexes. 
# Note: runtime negligible.

# INPUT PARAMETERS DESCRIPTION
# Year_list (list of years, in YYYY format): years to extract from the raw table.
# EFFCI_list (list of integers, from 1 to 10): EFFCI indexes to consider.
# CornersDomain_list (list of floats): coordinates [N/E/S/W] of the domain to plot.
# RegionCode_list (list of integers): codes for the domain's regions to consider. 
# RegionName_list (list of strings): names for the domain's regions to consider.
# RegionColour_list (list of strings): rgb-codes for the domain's regions to consider.
# Git_repo (string): repository's local path.
# FileIN_Mask (string): relative path of the file containing the domain's mask.
# FileIN (string): relative path of the file containing the clean point flood reports.
# DirOUT (string): relative path where to store the map plots.

# INPUT PARAMETERS
Year_list = [2019,2020]
EFFCI_list = [1,6,10]
CornersDomain_list = [2,-81.5,-5.5,-74.5]
RegionCode_list = [1,2,3]
RegionName_list = ["La Costa", "La Sierra", "El Oriente"]
RegionColour_list = ["#ffea00", "#c19a6b", "#A9FE00"]
Git_repo="/ec/vol/ecpoint_dev/mofp/Papers_2_Write/Verif_Flash_Floods_Ecuador"
FileIN_Mask = "Data/Raw/Ecuador_Mask_ENS/Mask.grib"
FileIN = "Data/Compute/01_Clean_PointFR/Ecu_FF_Hist_ECMWF.csv"
DirOUT = "Data/Plot/02_PointFR_EFFCI"
#####################################################################


# Setting output directory
DirOUT= Git_repo + "/" + DirOUT
if not os.path.exists(DirOUT):
    os.makedirs(DirOUT)

# Reading the domain's mask
FileIN_Mask = Git_repo + "/" + FileIN_Mask
Mask = mv.read(FileIN_Mask)

# Reading the cleaned point flood reports
FileIN = Git_repo + "/" + FileIN
PointFR = pd.read_csv(FileIN)

# Sorting the region codes for plotting
RegionCode_list = (np.array(([0] + RegionCode_list), dtype=float) + 0.1).tolist()
 
# Selecting the point flood reports for the years of interest
for Year in Year_list: 

      PointFR_Year = PointFR.loc[PointFR["year"] == Year]

      # Selecting the point flood reports for EFFCI indexes of interest
      for EFFCI in EFFCI_list: 

            print(" ")
            print("Considering point flood reports in " + str(Year) + " with EFFCI>=" + str(EFFCI) + " ...")

            PointFR_EFFCI = PointFR_Year.loc[PointFR_Year["EFFCI"] >= EFFCI]
            
            # Replacing the regions' names with the regions' codes
            for indRegion in range(len(RegionName_list)):
                  
                  RegionName = RegionName_list[indRegion]
                  RegionCode = RegionCode_list[indRegion]
                  
                  ind = PointFR_EFFCI.index[ (PointFR_EFFCI["Georegion"] == RegionName) ]
                  PointFR_EFFCI.loc[ind,"Georegion"] = RegionCode
                  print("     n. of point flood reports in " + RegionName + ": " + str(ind.shape[0]))

            # Converting the point flood reports to geopoints
            PointFR_geo = mv.create_geo(
                  type = "xyv",
                  latitudes = PointFR_EFFCI["Y_DD"].to_numpy(),
                  longitudes = PointFR_EFFCI["X_DD"].to_numpy(),
                  values = np.array(PointFR_EFFCI["Georegion"].tolist()),
            )

            # Plotting the point flood reports
            coastlines = mv.mcoast(
                  map_coastline_resolution = "full",
                  map_coastline_colour = "charcoal",
                  map_coastline_thickness = 1,
                  map_coastline_sea_shade = "on",
                  map_coastline_sea_shade_colour = "rgb(0.6455,0.903,0.9545)",
                  map_boundaries = "on",
                  map_boundaries_colour = "charcoal",
                  map_boundaries_thickness = 1,
                  map_grid = "on",
                  map_grid_latitude_increment  = 2,
                  map_grid_longitude_increment = 2,
                  map_label = "on",
                  map_label_font = "arial",
                  map_label_colour = "charcoal",
                  map_label_height = 0.6
                  )

            geo_view = mv.geoview(
                  map_area_definition = "corners",
                  area = CornersDomain_list,
                  coastlines = coastlines
                  )

            mask_shading = mv.mcont(
                  legend = "off",
                  contour = "off",
                  contour_level_selection_type = "level_list",
                  contour_level_list = RegionCode_list,
                  contour_label = "off",
                  contour_shade = "on",
                  contour_shade_technique = "grid_shading",
                  contour_shade_colour_method = "list",
                  contour_shade_colour_list = RegionColour_list
                  )

            PointFR_contour = mv.msymb(
                  legend = "off",
                  symbol_type = "marker",
                  symbol_table_mode = "on",
                  symbol_outline = "on",
                  symbol_min_table = [0.1],
                  symbol_max_table = [3.1],
                  symbol_colour_table = "charcoal",
                  symbol_marker_table = 15,
                  symbol_height_table = 0.4
                  )

            PointFR_shades = mv.msymb(
                  legend = "off",
                  symbol_type = "marker",
                  symbol_table_mode = "on",
                  symbol_outline = "on",
                  symbol_min_table = RegionCode_list[0:-1],
                  symbol_max_table = RegionCode_list[1:],
                  symbol_colour_table = RegionColour_list, 
                  symbol_marker_table = 15,
                  symbol_height_table = 0.3
                  )

            title = mv.mtext(
                  text_line_count = 2,
                  text_line_1 = "Point Flood Reports for " + str(Year) + " with EFFCI >= " + str(EFFCI),
                  text_line_2 = " ",
                  text_colour = "charcoal",
                  text_font = "arial",
                  text_font_size = 0.6
                  )

            # Saving the plot
            print("Saving the map plot ...")
            FileOUT = DirOUT + "/PointFR_" + str(Year) + "_EFFCI" + f"{EFFCI:02d}"
            png = mv.png_output(output_name = FileOUT)
            mv.setoutput(png)
            mv.plot(geo_view, Mask, mask_shading, PointFR_geo, PointFR_contour, PointFR_shades, coastlines, title)