# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 15:27:52 2018

@author: tih
"""

import wa.Models.SurfWAT as SurfWAT

##################################### User input ######################################

# Create input File for SurfWAT
Format_DEM = "NetCDF"    # or "TIFF"
Format_Runoff = "NetCDF"    # or "TIFF"
Format_Extraction = "NetCDF"    # or "TIFF"
Format_DEM_dir = "NetCDF"    # or "TIFF"
Format_Basin = "TIFF"    # or "TIFF"

# Give path (for tiff) or file (netcdf)
files_DEM_dir = r"G:\Create_Sheets\Wainganga\Simulations\Simulation_1\Sheet_5\DEM_Dir_CR_Simulation1_.nc"
files_DEM = r"G:\Create_Sheets\Wainganga\Simulations\Simulation_1\Sheet_5\DEM_CR_Simulation1_.nc"
files_Runoff = r"G:\Create_Sheets\Wainganga\Simulations\Simulation_1\Sheet_5\Runoff_CR_Simulation1_monthly_mm_032010_122013.nc"
files_Extraction = r"G:\Create_Sheets\Wainganga\Simulations\Simulation_1\Sheet_5\Supply_Simulation1_monthly_m3_032010_122013.nc"
files_Basin = r"G:\Create_Sheets\LU\Wainganga.tif"

#files_DEM_dir = r"F:\Create_Sheets\Wainganga\HydroSHED\DIR"
#files_DEM = r"F:\Create_Sheets\Wainganga\HydroSHED\DEM"
#files_Runoff = r"F:\Create_Sheets\Wainganga\Evaporation\ETensV1_0"
#files_Extraction = r"F:\Create_Sheets\Wainganga\Precipitation\CHIRPS\Monthly"
#files_Basin = r"F:\Create_Sheets\Wainganga\Simulations\Simulation_1\Sheet_5\Basin_CR_Simulation1_.nc"

input_nc = r"G:\Create_Sheets\Wainganga\Simulations\Simulation_1\testnew2.nc"
output_nc = r"G:\Create_Sheets\Wainganga\Simulations\Simulation_1\testnew_out2.nc"
resolution = '15s'
input_JRC = r"G:\Create_Sheets\Wainganga\JRC\Occurrence\JRC_Occurrence_percent.tif"
Inflow_Text_Files = []
include_reservoirs = 1  # 1 = on, 0 = off

# Define start and enddate
startdate = "2011-01-01"
enddate = "2011-12-31"

# Create Input File
SurfWAT.Create_input_nc.main(files_DEM_dir, files_DEM, files_Basin, files_Runoff, files_Extraction, startdate, enddate, input_nc, resolution, Format_DEM_dir, Format_DEM, Format_Basin, Format_Runoff, Format_Extraction)

# Run SurfWAT
SurfWAT.Run_SurfWAT.main(input_nc, output_nc, input_JRC, Inflow_Text_Files, include_reservoirs)



