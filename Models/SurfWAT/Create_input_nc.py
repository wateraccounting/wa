# -*- coding: utf-8 -*-
"""
Created on Thu Mar 08 08:29:00 2018

@author: tih
"""

import netCDF4
import os
import osr
import gdal
import pandas as pd
import numpy as np

import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC

########################### Start SurfWAT input file creator ##########################

# Open arrays and data
def main(files_DEM_dir, files_DEM, files_Basin, files_Runoff, files_Extraction, startdate, enddate, input_nc, resolution, Format_DEM_dir, Format_DEM, Format_Basin, Format_Runoff, Format_Extraction):

    # Define a year to get the epsg and geo
    Startdate_timestamp = pd.Timestamp(startdate)
    year = Startdate_timestamp.year

    ############################## Drainage Direction #####################################

    # Open Array DEM dir as netCDF
    if Format_DEM_dir == "NetCDF":
        file_DEM_dir = os.path.join(files_DEM_dir, "%d.nc" %year)
        DataCube_DEM_dir = RC.Open_nc_array(file_DEM_dir, "Drainage_Direction")
        geo_out_example, epsg_example, size_X_example, size_Y_example, size_Z_example, Time_example = RC.Open_nc_info(files_DEM_dir)

        # Create memory file for reprojection
        gland = DC.Save_as_MEM(DataCube_DEM_dir, geo_out_example, epsg_example)
        dataset_example = file_name_DEM_dir = gland

    # Open Array DEM dir as TIFF
    if Format_DEM_dir == "TIFF":
        file_name_DEM_dir = os.path.join(files_DEM_dir,"DIR_HydroShed_-_%s.tif" %resolution)
        DataCube_DEM_dir = RC.Open_tiff_array(file_name_DEM_dir)
        geo_out_example, epsg_example, size_X_example, size_Y_example = RC.Open_array_info(file_name_DEM_dir)
        dataset_example = file_name_DEM_dir

    # Calculate Area per pixel in m2
    import wa.Functions.Start.Area_converter as AC
    DataCube_Area = AC.Degrees_to_m2(file_name_DEM_dir)

    ################################## DEM ##########################################

    # Open Array DEM as netCDF
    if Format_DEM == "NetCDF":
        file_DEM = os.path.join(files_DEM, "%d.nc" %year)
        DataCube_DEM = RC.Open_nc_array(file_DEM, "Elevation")

    # Open Array DEM as TIFF
    if Format_DEM == "TIFF":
        file_name_DEM = os.path.join(files_DEM,"DEM_HydroShed_m_%s.tif" %resolution)
        DataCube_DEM = RC.Open_tiff_array(file_name_DEM)

    ################################ Landuse ##########################################

    # Open Array Basin as netCDF
    if Format_Basin == "NetCDF":
        file_Basin = os.path.join(files_Basin, "%d.nc" %year)
        DataCube_Basin = RC.Open_nc_array(file_Basin, "Landuse")
        geo_out, epsg, size_X, size_Y, size_Z, Time = RC.Open_nc_info(file_Basin, "Landuse")
        dest_basin = DC.Save_as_MEM(DataCube_Basin, geo_out, str(epsg))
        destLU = RC.reproject_dataset_example(dest_basin, dataset_example, method=1)
        DataCube_LU_CR = destLU.GetRasterBand(1).ReadAsArray()
        DataCube_Basin = np.zeros([size_Y_example, size_X_example])
        DataCube_Basin[DataCube_LU_CR > 0] = 1

    # Open Array Basin as TIFF
    if Format_Basin == "TIFF":
        file_name_Basin = files_Basin
        destLU = RC.reproject_dataset_example(file_name_Basin, dataset_example, method=1)
        DataCube_LU_CR = destLU.GetRasterBand(1).ReadAsArray()
        DataCube_Basin = np.zeros([size_Y_example, size_X_example])
        DataCube_Basin[DataCube_LU_CR > 0] = 1

    ################################ Surface Runoff ##########################################

    # Open Array runoff as netCDF
    if Format_Runoff == "NetCDF":
        DataCube_Runoff = RC.Open_ncs_array(files_Runoff, "Surface_Runoff", startdate, enddate)
        size_Z_example = DataCube_Runoff.shape[0]
        file_Runoff = os.path.join(files_Runoff, "%d.nc" %year)
        geo_out, epsg, size_X, size_Y, size_Z, Time = RC.Open_nc_info(file_Runoff, "Surface_Runoff")
        DataCube_Runoff_CR = np.ones([size_Z_example, size_Y_example, size_X_example]) * np.nan
        for i in range(0, size_Z):
            DataCube_Runoff_one = DataCube_Runoff[i,:,:]
            dest_Runoff_one = DC.Save_as_MEM(DataCube_Runoff_one, geo_out, str(epsg))
            dest_Runoff = RC.reproject_dataset_example(dest_Runoff_one, dataset_example, method=4)
            DataCube_Runoff_CR[i,:,:] = dest_Runoff.GetRasterBand(1).ReadAsArray()

        DataCube_Runoff_CR[:, DataCube_LU_CR == 0] = -9999
        DataCube_Runoff_CR[DataCube_Runoff_CR < 0] = -9999

    # Open Array runoff as TIFF
    if Format_Runoff == "TIFF":
        Data_Path = ''
        DataCube_Runoff = RC.Get3Darray_time_series_monthly(files_Runoff, Data_Path, startdate, enddate, Example_data = dataset_example)

    ################################ Surface Withdrawal ##########################################

    # Open Array Extraction as netCDF
    if Format_Extraction == "NetCDF":
        DataCube_Extraction = RC.Open_ncs_array(files_Extraction, "Surface_Withdrawal", startdate, enddate)
        size_Z_example = DataCube_Extraction.shape[0]
        file_Extraction = os.path.join(files_Extraction, "%d.nc" %year)
        geo_out, epsg, size_X, size_Y, size_Z, Time = RC.Open_nc_info(file_Extraction, "Surface_Withdrawal")
        DataCube_Extraction_CR = np.ones([size_Z_example, size_Y_example, size_X_example]) * np.nan
        for i in range(0, size_Z):
            DataCube_Extraction_one = DataCube_Extraction[i,:,:]
            dest_Extraction_one = DC.Save_as_MEM(DataCube_Extraction_one, geo_out, str(epsg))
            dest_Extraction = RC.reproject_dataset_example(dest_Extraction_one, dataset_example, method=4)
            DataCube_Extraction_CR[i,:,:] = dest_Extraction.GetRasterBand(1).ReadAsArray()

        DataCube_Extraction_CR[:, DataCube_LU_CR == 0] = -9999
        DataCube_Extraction_CR[DataCube_Extraction_CR < 0] = -9999

    # Open Array Extraction as TIFF
    if Format_Extraction == "TIFF":
        Data_Path = ''
        DataCube_Extraction = RC.Get3Darray_time_series_monthly(files_Extraction, Data_Path, startdate, enddate, Example_data = dataset_example)

    ################################ Create input netcdf ##########################################
    # Save data in one NetCDF file
    geo_out_example = np.array(geo_out_example)

    # Latitude and longitude
    lon_ls = np.arange(size_X_example)*geo_out_example[1]+geo_out_example[0] + 0.5 * geo_out_example[1]
    lat_ls = np.arange(size_Y_example)*geo_out_example[5]+geo_out_example[3] - 0.5 * geo_out_example[5]

    lat_n = len(lat_ls)
    lon_n = len(lon_ls)

    # Create NetCDF file
    nc_file = netCDF4.Dataset(input_nc, 'w')
    nc_file.set_fill_on()

    # Create dimensions
    lat_dim = nc_file.createDimension('latitude', lat_n)
    lon_dim = nc_file.createDimension('longitude', lon_n)

    # Create NetCDF variables
    crso = nc_file.createVariable('crs', 'i4')
    crso.long_name = 'Lon/Lat Coords in WGS84'
    crso.standard_name = 'crs'
    crso.grid_mapping_name = 'latitude_longitude'
    crso.projection = epsg_example
    crso.longitude_of_prime_meridian = 0.0
    crso.semi_major_axis = 6378137.0
    crso.inverse_flattening = 298.257223563
    crso.geo_reference = geo_out_example

    lat_var = nc_file.createVariable('latitude', 'f8', ('latitude',))
    lat_var.units = 'degrees_north'
    lat_var.standard_name = 'latitude'
    lat_var.pixel_size = geo_out_example[5]

    lon_var = nc_file.createVariable('longitude', 'f8', ('longitude',))
    lon_var.units = 'degrees_east'
    lon_var.standard_name = 'longitude'
    lon_var.pixel_size = geo_out_example[1]

    Dates = pd.date_range(startdate,enddate,freq = 'MS')
    time_or=np.zeros(len(Dates))
    i = 0
    for Date in Dates:
        time_or[i] = Date.toordinal()
        i += 1
    nc_file.createDimension('time', None)
    timeo = nc_file.createVariable('time', 'f4', ('time',))
    timeo.units = 'Monthly'
    timeo.standard_name = 'time'

    # Variables
    demdir_var = nc_file.createVariable('demdir', 'i',
                                           ('latitude', 'longitude'),
                                           fill_value=-9999)
    demdir_var.long_name = 'Flow Direction Map'
    demdir_var.grid_mapping = 'crs'

    dem_var = nc_file.createVariable('dem', 'f8',
                                           ('latitude', 'longitude'),
                                           fill_value=-9999)
    dem_var.long_name = 'Altitude'
    dem_var.units = 'meters'
    dem_var.grid_mapping = 'crs'

    basin_var = nc_file.createVariable('basin', 'i',
                                           ('latitude', 'longitude'),
                                           fill_value=-9999)
    basin_var.long_name = 'Altitude'
    basin_var.units = 'meters'
    basin_var.grid_mapping = 'crs'

    area_var = nc_file.createVariable('area', 'f8',
                                           ('latitude', 'longitude'),
                                           fill_value=-9999)
    area_var.long_name = 'area in squared meters'
    area_var.units = 'squared_meters'
    area_var.grid_mapping = 'crs'

    runoff_var = nc_file.createVariable('Runoff_M', 'f8',
                                   ('time', 'latitude', 'longitude'),
                                   fill_value=-9999)
    runoff_var.long_name = 'Runoff'
    runoff_var.units = 'm3/month'
    runoff_var.grid_mapping = 'crs'

    extraction_var = nc_file.createVariable('Extraction_M', 'f8',
                                    ('time', 'latitude', 'longitude'),
                                    fill_value=-9999)
    extraction_var.long_name = 'Surface water Extraction'
    extraction_var.units = 'm3/month'
    extraction_var.grid_mapping = 'crs'


    # Load data
    lat_var[:] = lat_ls
    lon_var[:] = lon_ls
    timeo[:] = time_or

    # Static variables
    demdir_var[:, :] = DataCube_DEM_dir[:, :]
    dem_var[:, :] = DataCube_DEM[:, :]
    basin_var[:, :] = DataCube_Basin[:, :]
    area_var[:, :] = DataCube_Area[:, :]
    for i in range(len(Dates)):
        runoff_var[i,:,:] = DataCube_Runoff_CR[i,:,:]
    for i in range(len(Dates)):
        extraction_var[i,:,:] = DataCube_Extraction_CR[i,:,:]

    # Close file
    nc_file.close()
    return()
