import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import metview as mv

#####################################################################################
# CODE DESCRIPTION
# 05_Plot_SpatialDistr_PointFR_GridFR_EFFCI_AccPer.py plots a map that shows the location of point 
# and grid flood reports, for a specific date, EFFCI index, and accumulation period.
# Note: runtime negligible.

# INPUT PARAMETERS DESCRIPTION
# Date (date, in YYYY format): date to plot.
# Acc (number, in hours): accumulation to consider.
# EFFCI (integer, from 1 to 10): EFFCI index.
# CornersDomain_list (list of floats): coordinates [N/E/S/W] of the domain to plot.
# RegionCode_list (list of integers): codes for the domain's regions to consider. 
# RegionName_list (list of strings): names for the domain's regions to consider.
# RegionColour_list (list of strings): rgb-codes for the domain's regions to consider.
# Git_repo (string): repository's local path.
# FileIN_Mask (string): relative path of the file containing the domain's mask.
# FileIN_PointFR (string): relative path of the file containing the clean point flood reports.
# DirIN_GridFR (string): relative path of the directory containing the gridded, accumulated flood reports.
# DirOUT (string): relative path where to store the map plots.

# INPUT PARAMETERS
DateS = datetime(2020,2,28,6)
Acc = 12
EFFCI = 6
CornersDomain_list = [2,-81.5,-5.5,-74.5] 
RegionCode_list = [1,2,3]
RegionName_list = ["La Costa", "La Sierra", "El Oriente"]
RegionColour_list = ["#ffea00", "#c19a6b", "#A9FE00"]
Git_repo="/ec/vol/ecpoint_dev/mofp/Papers_2_Write/Verif_Flash_Floods_Ecuador"
FileIN_Mask = "Data/Raw/Ecuador_Mask_ENS/Mask.grib"
FileIN_PointFR = "Data/Compute/01_Clean_PointFR/Ecu_FF_Hist_ECMWF.csv"
DirIN_GridFR = "Data/Compute/03_GridFR_EFFCI_AccPer"
DirOUT = "Data/Plot/05_SpatialDistr_PointFR_GridFR_EFFCI_AccPer"
#####################################################################################


print("Plotting the location of point and gridded flood reports with EFFCI>=" + str(EFFCI) + " for the " + str(Acc) + "-hourly accumulation period starting on " + DateS.strftime("%Y%m%d") + " at " + DateS.strftime("%H") + " UTC")

# Defining the accumulation period
DateF = DateS + timedelta(hours=Acc) 

# Reading the domain's mask
FileIN_Mask = Git_repo + "/" + FileIN_Mask
mask = mv.read(FileIN_Mask)

# Reading the gridded flood reports
FileIN_GridFR = Git_repo + "/" + DirIN_GridFR + "/" +  f"{Acc:02d}" + "h/EFFCI" + f"{EFFCI:02d}" + "/" + DateF.strftime("%Y%m%d") + "/" + "GridFR_" + f"{Acc:02d}" + "h_EFFCI" + f"{EFFCI:02d}" + "_" + DateF.strftime("%Y%m%d") + "_" + DateF.strftime("%H") + ".grib"                 
GridFR = mv.read(FileIN_GridFR)

# Reading the point flood reports
FileIN_PointFR = Git_repo + "/" + FileIN_PointFR
PointFR = pd.read_csv(FileIN_PointFR)
PointFR["ReportDateTimeUTC"] = pd.to_datetime(PointFR["ReportDateTimeUTC"] )
PointFR_EFFCI = PointFR.loc[PointFR["EFFCI"] >= EFFCI]
ind = PointFR_EFFCI.index[ (PointFR_EFFCI["ReportDateTimeUTC"]>=DateS) & (PointFR_EFFCI["ReportDateTimeUTC"]<DateF) ]
PointFR = mv.create_geo(
      type = "xyv",
      latitudes = PointFR_EFFCI.loc[ind, "Y_DD"].to_numpy(),
      longitudes = PointFR_EFFCI.loc[ind, "X_DD"].to_numpy(),
      values = np.zeros(len(PointFR_EFFCI.loc[ind, "Y_DD"].to_numpy())),
)

# Plotting the point and grid flood reports
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

RegionCode_list = (np.array(([0] + RegionCode_list), dtype=float) + 0.1).tolist()
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
                  symbol_min_table = [-0.1],
                  symbol_max_table = [0.1],
                  symbol_colour_table = "#372800",
                  symbol_marker_table = 15,
                  symbol_height_table = 0.4
                  )

GridFR_shading = mv.mcont(
      contour = "off",
      contour_level_selection_type = "level_list",
      contour_level_list = [0.1, 100],
      contour_label = "off",
      contour_shade = "on",
      contour_shade_technique = "grid_shading",
      contour_shade_colour_method = "list",
      contour_shade_colour_list = ["#f67293"]
      )

title = mv.mtext(
      text_line_count = 3,
      text_line_1 = "Spatial distribution of flood reports (FR) with EFFCI>=" + f"{EFFCI:02d}",
      text_line_2 = "over the " + f"{Acc:02d}" + "-hourly period starting on " + DateF.strftime("%Y-%m-%d") + " at " + DateS.strftime("%H") + " UTC",
      text_line_3 = " ",
      text_font = "sansserif",
      text_colour = "charcoal",
      text_font_size = 0.6,
      text_font_style = "bold"
      )

# Saving the plot
DirOUT= Git_repo + "/" + DirOUT
if not os.path.exists(DirOUT):
      os.makedirs(DirOUT)
FileOUT = DirOUT + "/GridFR_" + DateS.strftime("%Y%m%d") + "_" + DateS.strftime("%H") + "_EFFCI" + f"{EFFCI:02d}"
png = mv.png_output(output_name = FileOUT)
mv.setoutput(png)
mv.plot(geo_view, mask, mask_shading, GridFR, GridFR_shading, PointFR, PointFR_contour, title)