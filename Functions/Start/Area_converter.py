# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:06:53 2017

@author: tih
"""
import numpy as np
from wa.General import raster_conversions as RC

def Degrees_to_m2(Reference_data):

    dlat, dlon = Calc_dlat_dlon(Reference_data)  

    # Calculate the area in squared meters
    area_in_m2 =  dlat * dlon

    return(area_in_m2)

def Calc_dlat_dlon(Reference_data):

    # Get raster information 			
    geo_out, proj, size_X, size_Y = RC.Open_array_info(Reference_data)				

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