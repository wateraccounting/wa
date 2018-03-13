# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 15:11:17 2018

@author: tih
"""
# input paramters SurfWAT

input_nc = r"F:\Create_Sheets\Wainganga\Simulations\Simulation_1\test1.nc"
output_nc = r"F:\Create_Sheets\Wainganga\Simulations\Simulation_1\test1_out.nc"



import time
import sys
import wa.General.raster_conversions as RC

time1 = time.time()

###############################################################################
############################### Run Part 1 ####################################
###############################################################################
                
import SurfWAT.Part1_Channel_Routing as Part1_Channel_Routing
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
nc_file = netCDF4.Dataset(output_nc, 'w')
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

nc_file.close()         

###############################################################################
############################### Run Part 2 ####################################
###############################################################################

###############################################################################
################## Create NetCDF Part 2 results ###############################
##############################################################################

# Create NetCDF file
nc_file = netCDF4.Dataset(output_nc, 'r+')
nc_file.set_fill_on()

###################### Save Dictionaries in NetCDF ############################

parms = nc_file.createGroup('demdict')
for k,v in DEM_dict.items():
    setattr(parms, str(k), str(v.tolist()))

parms = nc_file.createGroup('riverdict')
for k,v in River_dict.items():
    setattr(parms, str(k), str(v.tolist()))

parms = nc_file.createGroup('distancedict')
for k,v in Distance_dict.items():
    setattr(parms, str(k), str(v.tolist()))
    
parms = nc_file.createGroup('dischargedict')
for k,v in Discharge_dict.items():
    setattr(parms, str(k), str(v.tolist()))
    
# Close file
nc_file.close()
    

###############################################################################
############################### Run Part 3 ####################################
###############################################################################






###############################################################################
############################### Run Part 4 ####################################
###############################################################################




























                           
                            
                            
                            
                            
                            
                            
                            
                            
                            





























import numpy as np
import ast
import netCDF4

input1 = np.load("F:\Create_Sheets\Wainganga\Simulations\Simulation_1\Sheet_5\River_dict_CR1_simulation1.npy").item() 

input1 = np.load("F:\Create_Sheets\Wainganga\Simulations\Simulation_1\Sheet_5\Discharge_dict_CR1_simulation1.npy").item() 

Amount_months = 46

input2 = str(input1)



















def Open_nc_dict(input_netcdf, group_name, startdate = '', enddate = '')

    from netCDF4 import Dataset
    test = Dataset('test2.nc')
    data = test.groups['parameters']
    string_dict = str(data)
    split_dict = str(string_dict.split('\n')[2:-4])
    split_dict = split_dict.replace("'","")
    split_dict = split_dict[1:-1]
    dictionary = dict()
    import re
    split_dict_split = re.split(':|,  ',split_dict)
    
    for i in range(0,len(split_dict_split)):
        number_val = split_dict_split[i]
        if i % 2 == 0:
            Array_text = split_dict_split[i + 1].replace(",","")
            Array_text = Array_text.replace("[","")
            Array_text = Array_text.replace("]","")  
            tot_length = len(np.fromstring(Array_text,sep = ' '))
            dictionary[int(number_val)] = np.fromstring(Array_text,sep = ' ').reshape((Amount_months, tot_length/Amount_months))

    return(dictionary)    
    
    








