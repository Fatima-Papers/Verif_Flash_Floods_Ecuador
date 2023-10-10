import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import metview as mv

###################################################################################################
# CODE DESCRIPTION
# 04b_Plot_SpatialDistr_GridFR_EFFCI.py plots a map that shows the location of point and grid flood reports, for a specific
# date and EFFCI index.
# Note: runtime negligible.

# INPUT PARAMETERS DESCRIPTION
# Date (date, in YYYY format): date to plot.
# Acc (number, in hours): accumulation to consider.
# EFFCI (integer, from 1 to 10): EFFCI index.
# RegionCode_list (list of integers): codes for the domain's regions to consider. 
# RegionName_list (list of strings): names for the domain's regions to consider.
# RegionColour_list (list of strings): rgb-codes for the domain's regions to consider.
# Git_repo (string): repository's local path.
# FileIN_Mask (string): relative path of the file containing the domain's mask.
# FileIN (string): relative path of the file containing the clean point flood reports.
# DirOUT (string): relative path where to store the map plots.

# INPUT PARAMETERS
DateS = datetime(2020,2,28,0)
Acc = 12
EFFCI = 6
CornersDomain_list = [1.6,-81.2,-5.11,-75]
RegionCode_list = [1,2,3]
RegionName_list = ["La Costa", "La Sierra", "El Oriente"]
RegionColour_list = ["RGB(255/255,234/255,0/255)", "RGB(193/255,154/255,107/255)", "RGB(170/255,255/255,0/255)"]
Git_repo="/ec/vol/ecpoint_dev/mofp/Papers_2_Write/Verif_Flash_Floods_Ecuador"
FileIN_Mask = "Data/Raw/Ecuador_Mask_ENS/Mask.grib"
FileIN_PointFR = "Data/Compute/01_Clean_PointFR/Ecu_FF_Hist_ECMWF.csv"
DirIN_GridFR = "Data/Compute/03_GridFR_EFFCI_AccPer"
DirOUT = "Data/Plot/04b_SpatialDistr_GridFR_EFFCI"
###################################################################################################


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

no_title = mv.mtext(
      text_line_1 = " "
      )

# Saving the plot
print("Saving the map plot ...")
DirOUT= Git_repo + "/" + DirOUT
if not os.path.exists(DirOUT):
      os.makedirs(DirOUT)
FileOUT = DirOUT + "/GridFR_" + DateF.strftime("%Y%m%d") + "_" + DateF.strftime("%H") + "_EFFCI" + f"{EFFCI:02d}"
png = mv.png_output(output_name = FileOUT)
mv.setoutput(png)
mv.plot(geo_view, mask, mask_shading, GridFR, GridFR_shading, PointFR, PointFR_contour, no_title)