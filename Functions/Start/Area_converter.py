# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Start
"""
# import general python modules
import numpy as np
import os

# import WA modules
from wa.General import raster_conversions as RC

def Degrees_to_m2(Reference_data):
    """
    This functions calculated the area of each pixel in squared meter.

    Parameters
    ----------
    Reference_data: str
        Path to a tiff file or nc file or memory file of which the pixel area must be defined

    Returns
    -------
    area_in_m2: array
        Array containing the area of each pixel in squared meters

    """
    try:
        # Get the extension of the example data
        filename, file_extension = os.path.splitext(Reference_data)

        # Get raster information
        if str(file_extension) == '.tif':
            geo_out, proj, size_X, size_Y = RC.Open_array_info(Reference_data)
        elif str(file_extension) == '.nc':
            geo_out, epsg, size_X, size_Y, size_Z, Time = RC.Open_nc_info(Reference_data)

    except:
        geo_out = Reference_data.GetGeoTransform()
        size_X = Reference_data.RasterXSize()
        size_Y = Reference_data.RasterYSize()

    # Calculate the difference in latitude and longitude in meters
    dlat, dlon = Calc_dlat_dlon(geo_out, size_X, size_Y)

    # Calculate the area in squared meters
    area_in_m2 =  dlat * dlon

    return(area_in_m2)

def Calc_dlat_dlon(geo_out, size_X, size_Y):
    """
    This functions calculated the distance between each pixel in meter.

    Parameters
    ----------
    geo_out: array
        geo transform function of the array
    size_X: int
        size of the X axis
    size_Y: int
        size of the Y axis

    Returns
    -------
    dlat: array
        Array containing the vertical distance between each pixel in meters
    dlon: array
        Array containing the horizontal distance between each pixel in meters
    """

    # Create the lat/lon rasters
    lon = np.arange(size_X + 1)*geo_out[1]+geo_out[0] - 0.5 * geo_out[1]
    lat = np.arange(size_Y + 1)*geo_out[5]+geo_out[3] - 0.5 * geo_out[5]

    dlat_2d = np.array([lat,]*int(np.size(lon,0))).transpose()
    dlon_2d =  np.array([lon,]*int(np.size(lat,0)))

    # Radius of the earth in meters
    R_earth = 6371000

    # Calculate the lat and lon in radians
    lonRad = dlon_2d * np.pi/180
    latRad = dlat_2d * np.pi/180

    # Calculate the difference in lat and lon
    lonRad_dif = abs(lonRad[:,1:] - lonRad[:,:-1])
    latRad_dif = abs(latRad[:-1] - latRad[1:])

    # Calculate the distance between the upper and lower pixel edge
    a = np.sin(latRad_dif[:,:-1]/2) * np.sin(latRad_dif[:,:-1]/2)
    clat = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a));
    dlat = R_earth * clat

    # Calculate the distance between the eastern and western pixel edge
    b = np.cos(latRad[1:,:-1]) * np.cos(latRad[:-1,:-1]) * np.sin(lonRad_dif[:-1,:]/2) * np.sin(lonRad_dif[:-1,:]/2)
    clon = 2 * np.arctan2(np.sqrt(b), np.sqrt(1-b));
    dlon = R_earth * clon

    return(dlat, dlon)