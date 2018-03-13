# -*- coding: utf-8 -*-
"""
Authors: Gonzalo E. Espinoza-Dávalos
         IHE Delft 2017
Contact: g.espinoza@un-ihe.org
Repository: https://github.com/gespinoza/waterpix
Module: waterpix
"""

import os
import arcpy
import netCDF4


def output_nc_to_tiffs(output_nc, output_path):
    """
    Create raster files from the variables in the output netcdf file
    """
    # Output folders
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    path_y = os.path.join(output_path, 'yearly')
    path_m = os.path.join(output_path, 'monthly')
    path_a = os.path.join(output_path, 'additional')
    if not os.path.isdir(path_y):
        os.mkdir(path_y)
    if not os.path.isdir(path_m):
        os.mkdir(path_m)
    if not os.path.isdir(path_a):
        os.mkdir(path_a)

    # Read netcdf file
    nc_file = netCDF4.Dataset(output_nc, 'r')
    variables_ls = nc_file.variables.keys()
    time_y = nc_file.variables['time_yyyy'][:]
    time_m = nc_file.variables['time_yyyymm'][:]
    nc_file.close()

    # Remove variables
    for variable in ['latitude', 'longitude', 'time_yyyy', 'time_yyyymm',
                     'RoundCode', 'a_Y', 'b_Y', 'crs']:
        variables_ls.remove(variable)

    # Add sub-folders
    for variable in variables_ls:
        if '_Y' in variable:
            if not os.path.exists(os.path.join(path_y, variable)):
                os.mkdir(os.path.join(path_y, variable))
        elif '_M' in variable:
            if not os.path.exists(os.path.join(path_m, variable)):
                os.mkdir(os.path.join(path_m, variable))
        else:
            if not os.path.exists(os.path.join(path_a, variable)):
                os.mkdir(os.path.join(path_a, variable))

    # Main Loop
    for variable in variables_ls:
        # Yearly rasters
        if '_Y' in variable:
            for time in time_y:
                print '{0}\t{1}'.format(variable, time)
                file_name = variable[:-1] + '{0}.tif'.format(time)
                output_tiff = os.path.join(path_y, variable, file_name)
                arcpy.md.MakeNetCDFRasterLayer(output_nc, variable,
                                               'longitude', 'latitude',
                                               file_name[:-4], '#',
                                               'time_yyyy {0}'.format(time),
                                               'BY_VALUE')
                output_ras = arcpy.Raster(file_name[:-4])
                output_ras.save(output_tiff)
        # Monthly rasters
        elif '_M' in variable:
            for time in time_m:
                print '{0}\t{1}'.format(variable, time)
                file_name = variable[:-1] + '{0}.tif'.format(time)
                output_tiff = os.path.join(path_m, variable, file_name)
                arcpy.md.MakeNetCDFRasterLayer(output_nc, variable,
                                               'longitude', 'latitude',
                                               file_name[:-4], '#',
                                               'time_yyyymm {0}'.format(time),
                                               'BY_VALUE')
                output_ras = arcpy.Raster(file_name[:-4])
                output_ras.save(output_tiff)
        # Additional rasters
        else:
            print '{0}'.format(variable)
            file_name = variable[:-1] + '.tif'
            output_tiff = os.path.join(path_y, variable, file_name)
            arcpy.md.MakeNetCDFRasterLayer(output_nc, variable,
                                           'longitude', 'latitude',
                                           file_name[:-4])
            output_ras = arcpy.Raster(file_name[:-4])
            output_ras.save(output_tiff)

    # Return
    return output_path
