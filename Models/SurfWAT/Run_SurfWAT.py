# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 15:11:17 2018

@author: tih
"""
# input paramters SurfWAT

input_nc = r"F:\Create_Sheets\Wainganga\Simulations\Simulation_1\test1.nc"
output_nc = r"F:\Create_Sheets\Wainganga\Simulations\Simulation_1\test1_out.nc"
include_reservoirs = 1  # 1 = on, 0 = off


import time
import sys
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC
import numpy as np
import netCDF4

time1 = time.time()

###############################################################################
############################### Run Part 1 ####################################
###############################################################################
                
import wa.Models.SurfWAT.Part1_Channel_Routing as Part1_Channel_Routing
Routed_Array, Accumulated_Pixels, Rivers = Part1_Channel_Routing.Run(input_nc)
 
###############################################################################
################## Create NetCDF Part 1 results ###############################
###############################################################################

################### Get Example parameters for NetCDF #########################
                                    
# Create NetCDF   
geo_out_example, epsg_example, size_X_example, size_Y_example, size_Z_example, Time_example = RC.Open_nc_info(input_nc)                      
geo_out_example = np.array(geo_out_example)

time_or = RC.Open_nc_array(input_nc, Var = 'time')  
               
# Latitude and longitude
lon_ls = np.arange(size_X_example)*geo_out_example[1]+geo_out_example[0] + 0.5 * geo_out_example[1]
lat_ls = np.arange(size_Y_example)*geo_out_example[5]+geo_out_example[3] - 0.5 * geo_out_example[5]

lat_n = len(lat_ls)
lon_n = len(lon_ls)

################################ Save NetCDF ##################################

# Create NetCDF file
nc_file = netCDF4.Dataset(output_nc, 'w', format = 'NETCDF4')
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

######################### Save Rasters in NetCDF ##############################

lat_var = nc_file.createVariable('latitude', 'f8', ('latitude',))
lat_var.units = 'degrees_north'
lat_var.standard_name = 'latitude'

lon_var = nc_file.createVariable('longitude', 'f8', ('longitude',))
lon_var.units = 'degrees_east'
lon_var.standard_name = 'longitude'

nc_file.createDimension('time', None)
timeo = nc_file.createVariable('time', 'f4', ('time',))
timeo.units = 'Monthly'
timeo.standard_name = 'time'

# Variables
rivers_var = nc_file.createVariable('rivers', 'i',
                                       ('latitude', 'longitude'),
                                       fill_value=-9999)
rivers_var.long_name = 'Rivers'
rivers_var.grid_mapping = 'crs'

accpix_var = nc_file.createVariable('accpix', 'f8',
                                       ('latitude', 'longitude'),
                                       fill_value=-9999)
accpix_var.long_name = 'Accumulated Pixels'
accpix_var.units = 'AmountPixels'
accpix_var.grid_mapping = 'crs'

discharge_nat_var = nc_file.createVariable('discharge_natural', 'f8',
                               ('time', 'latitude', 'longitude'),
                               fill_value=-9999)
discharge_nat_var.long_name = 'Natural Discharge'
discharge_nat_var.units = 'm3/month'
discharge_nat_var.grid_mapping = 'crs'

# Load data
lat_var[:] = lat_ls
lon_var[:] = lon_ls
timeo[:] = time_or

# Static variables
rivers_var[:, :] = Rivers[:, :]
accpix_var[:, :] = Accumulated_Pixels[:, :]
for i in range(len(time_or)):
    discharge_nat_var[i,:,:] = Routed_Array[i,:,:]       

time.sleep(1)
nc_file.close()         
del Routed_Array, Accumulated_Pixels, Rivers

###############################################################################
############################### Run Part 2 ####################################
###############################################################################

import wa.Models.SurfWAT.Part2_Create_Dictionaries as Part2_Create_Dictionaries
DEM_dict, River_dict, Distance_dict, Discharge_dict = Part2_Create_Dictionaries.Run(input_nc, output_nc)

###############################################################################
################## Create NetCDF Part 2 results ###############################
###############################################################################

# Create NetCDF file
nc_file = netCDF4.Dataset(output_nc, 'r+', format = 'NETCDF4')
nc_file.set_fill_on()

###################### Save Dictionaries in NetCDF ############################

parmsdem = nc_file.createGroup('demdict_static')
for k,v in DEM_dict.items():
    setattr(parmsdem, str(k), str(v.tolist()))

parmsriver = nc_file.createGroup('riverdict_static')
for k,v in River_dict.items():
    setattr(parmsriver, str(k), str(v.tolist()))

parmsdist = nc_file.createGroup('distancedict_static')
for k,v in Distance_dict.items():
    setattr(parmsdist, str(k), str(v.tolist()))
    
parmsdis = nc_file.createGroup('dischargedict_dynamic')
for k,v in Discharge_dict.items():
    setattr(parmsdis, str(k), str(v.tolist()))
    
# Close file
time.sleep(1)
nc_file.close()
del DEM_dict, River_dict, Distance_dict, Discharge_dict

###############################################################################
############################### Run Part 3 ####################################
###############################################################################
'''
if include_reservoirs == 1:
    import wa.Models.SurfWAT.Part2_Create_Dictionaries as Part2_Create_Dictionaries
    Discharge_dict_reservoirs, River_dict_res, Distance_dict_res, DEM_dict_res = Part2_Create_Dictionaries.Run(input_nc, output_nc)   




'''
###############################################################################
############################### Run Part 4 ####################################
###############################################################################

import wa.Models.SurfWAT.Part4_Withdrawals as Part4_Withdrawals
Discharge_dict_end = Part4_Withdrawals.Run(input_nc, output_nc)

###############################################################################
################## Create NetCDF Part 4 results ###############################
###############################################################################

# Create NetCDF file
nc_file = netCDF4.Dataset(output_nc, 'r+', format = 'NETCDF4')
nc_file.set_fill_on()

###################### Save Dictionaries in NetCDF ############################

parmsdisend = nc_file.createGroup('dischargedictend_dynamic')
for k,v in Discharge_dict_end.items():
    setattr(parmsdisend, str(k), str(v.tolist()))

# Close file
time.sleep(1)
nc_file.close()
del Discharge_dict_end

###############################################################################
############### Part 5 Convert dictionaries to rasters ########################
###############################################################################

River_dict = RC.Open_nc_dict(output_nc, 'riverdict_static')

# End discharge dictionary to raster
Discharge_dict_end = RC.Open_nc_dict(output_nc, 'dischargedictend_dynamic')
DataCube_Discharge_end = DC.Convert_dict_to_array(River_dict, Discharge_dict_end, input_nc)

###################### Save Dictionaries in NetCDF ############################

# Create NetCDF file
nc_file = netCDF4.Dataset(output_nc, 'r+', format = 'NETCDF4')
nc_file.set_fill_on()

discharge_end_var = nc_file.createVariable('discharge_end', 'f8',
                               ('time', 'latitude', 'longitude'),
                               fill_value=-9999)
discharge_end_var.long_name = 'End Discharge'
discharge_end_var.units = 'm3/month'
discharge_end_var.grid_mapping = 'crs'

for i in range(len(time_or)):
    discharge_end_var[i,:,:] = DataCube_Discharge_end[i,:,:]      

# Close file
nc_file.close()
del DataCube_Discharge_end












                           
                            
                            
                            
                            
                            
                            
                            
                            
                            




























import pandas as pd
import numpy as np
import ast
import netCDF4

input1 = np.load("F:\Create_Sheets\Wainganga\Simulations\Simulation_1\Sheet_5\River_dict_CR1_simulation1.npy").item() 

input1 = np.load("F:\Create_Sheets\Wainganga\Simulations\Simulation_1\Sheet_5\Discharge_dict_CR1_simulation1.npy").item() 

Amount_months = 46

input2 = str(input1)













input_netcdf = output_nc
group_name = 'dischargedict'
group_name = 'demdict_static'




    
    








