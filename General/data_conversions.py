# -*- coding: utf-8 -*-
"""
Created on Sun Dec 18 13:07:32 2016

@author: tih
"""
import gzip
import zipfile
import gdal
import osr
import os
import subprocess
import pandas as pd
import numpy as np
from wa import WA_Paths

def Convert_grb2_to_nc(input_wgrib, output_nc, band):
	
    # find path to the executable
    path = WA_Paths.Paths(Type = 'GDAL')
    if path is '':
        fullCmd = ' '.join(['gdal_translate -of netcdf -b %d' %(band), input_wgrib, output_nc])  # -r {nearest}
	
    else: 				
        gdal_translate_path = os.path.join(path,'gdal_translate.exe')
				
	    # converting			
        fullCmd = ' '.join(['"%s" -of netcdf -b %d' %(gdal_translate_path, band), input_wgrib, output_nc])  # -r {nearest}

    process = subprocess.Popen(fullCmd)
    process.wait()  
    return()				

def Convert_adf_to_tiff(input_adf, output_tiff):
    """
    This function converts the adf files into tiff files

    Keyword Arguments:
    input_adf -- name, name of the adf file
    output_tiff -- Name of the output tiff file
    """

    # find path to the executable
    path = WA_Paths.Paths(Type = 'GDAL')
    if path is '':
        command = ("gdal_translate -co COMPRESS=DEFLATE -co PREDICTOR=1 -co "
                   "ZLEVEL=1 -of GTiff %s %s") % (input_adf, output_tiff)
	
    else:
        gdal_translate_path = os.path.join(path,'gdal_translate.exe')	
	
        # convert data from ESRI GRID to GeoTIFF
        command = ('"%s" -co COMPRESS=DEFLATE -co PREDICTOR=1 -co '
                   'ZLEVEL=1 -of GTiff %s %s') % (gdal_translate_path, input_adf, output_tiff)
    os.system(command)
    return(output_tiff)
				
def Extract_Data(input_file, output_folder):
    """
    This function extract the zip files

    Keyword Arguments:
    output_file -- name, name of the file that must be unzipped
    output_folder -- Dir, directory where the unzipped data must be
                           stored
    """
    # extract the data
    z = zipfile.ZipFile(input_file, 'r')
    z.extractall(output_folder)
    z.close()

def Extract_Data_gz(zip_filename, outfilename):
    """
    This function extract the zip files

    Keyword Arguments:
    zip_filename -- name, name of the file that must be unzipped
    outfilename -- Dir, directory where the unzipped data must be
                           stored
    """
				
    with gzip.GzipFile(zip_filename, 'rb') as zf:
        file_content = zf.read()
        save_file_content = file(outfilename, 'wb')
        save_file_content.write(file_content)
    save_file_content.close()
    zf.close()
    os.remove(zip_filename)				
				
def Save_as_tiff(name='', data='', geo='', projection=''):
    """
    This function save the array as a geotiff

    Keyword arguments:
    name -- string, directory name
    data -- [array], dataset of the geotiff
    geo -- [minimum lon, pixelsize, rotation, maximum lat, rotation,
            pixelsize], (geospatial dataset)
    projection -- interger, the EPSG code
    """
    # save as a geotiff
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(name, int(data.shape[1]), int(data.shape[0]), 1,
                           gdal.GDT_Float32, ['COMPRESS=LZW'])
    srse = osr.SpatialReference()
    srse.SetWellKnownGeogCS(projection)
    dst_ds.SetProjection(srse.ExportToWkt())
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform(geo)
    dst_ds.GetRasterBand(1).WriteArray(data)
    dst_ds = None
    return()						
				
def Save_as_NC(Dir_Basin, DataCube, Simulation, Var,  Reference_data, info = '', Startdate = '', Enddate = '', Time_steps = '', Scaling_factor = 1):

    # Import modules
    import wa.General.raster_conversions as RC
    from netCDF4 import Dataset

    # Create the output name					
    nameOut=''.join(['_'.join([Var,'Simulation%d' % Simulation,'_'.join(info)]),'.nc'])
    namePath = os.path.join(Dir_Basin,'Simulations')
    if not os.path.exists(namePath):
        os.makedirs(namePath)
    nameTot=os.path.join(namePath,nameOut)

    if not os.path.exists(nameTot):
	
        # Get raster information 			
        geo_out, proj, size_X, size_Y = RC.Open_array_info(Reference_data)				

        # Create the lat/lon rasters				
        lon = np.arange(size_X)*geo_out[1]+geo_out[0]
        lat = np.arange(size_Y)*geo_out[5]+geo_out[3]	

        # Create the nc file   
        nco = Dataset(nameTot, 'w', format='NETCDF4_CLASSIC')
        nco.description = '%s data' %Var

        # Create dimensions, variables and attributes:
        nco.createDimension('lon', size_X)
        nco.createDimension('lat', size_Y)

        # Create time dimension if the parameter is time dependent         											
        if Startdate is not '':     	
            if Time_steps == 'monthly':												
                Dates = pd.date_range(Startdate,Enddate,freq = 'MS')
            if Time_steps == 'daily':								
                Dates = pd.date_range(Startdate,Enddate,freq = 'D')	
            time_or=np.zeros(len(Dates))
            i = 0 								
            for Date in Dates:
                time_or[i] = Date.toordinal()
                i += 1 	
            nco.createDimension('time', len(Dates))
            timeo = nco.createVariable('time', 'f4', ('time',))
            timeo.units = '%s' %Time_steps
            timeo.standard_name = 'time'

        # Create the lon variable
        lono = nco.createVariable('lon', 'f4', ('lon',))
        lono.standard_name = 'longitude'
        lono.units = 'degrees_east'

        # Create the lat variable
        lato = nco.createVariable('lat', 'f4', ('lat',))
        lato.standard_name = 'latitude'
        lato.units = 'degrees_north'
 
        # Create container variable for CRS: lon/lat WGS84 datum
        crso = nco.createVariable('crs', 'i4')
        crso.long_name = 'Lon/Lat Coords in WGS84'
        crso.grid_mapping_name = 'latitude_longitude'
        crso.longitude_of_prime_meridian = 0.0
        crso.semi_major_axis = 6378137.0
        crso.inverse_flattening = 298.257223563
        crso.geo_reference = geo_out		

        # Create the data variable			
        if Startdate is not '':			
            preco = nco.createVariable('%s' %Var, 'f4',  ('time', 'lat', 'lon'),zlib=True, fill_value=-9999, least_significant_digit=3)
            timeo[:]=time_or	
        else:
            preco = nco.createVariable('%s' %Var, 'f4',  ('lat', 'lon'),zlib=True, fill_value=-9999, least_significant_digit=3)

        # Set the data variable information
        preco.scale_factor = Scaling_factor
        preco.add_offset = 0.00
        preco.grid_mapping = 'crs'
        preco.set_auto_maskandscale(False)                              																																																						

        # Set the lat/lon variable
        lono[:] = lon
        lato[:] = lat

        # Set the data variable
        if Startdate is not '':
            for i in range(len(Dates)):
                preco[i,:,:] = np.int_(np.flipud(DataCube[:,:,i]*1/Scaling_factor))
        else:
            preco[:,:] = np.int_(np.flipud(DataCube[:,:]*1/Scaling_factor))
		
        nco.close()				
    return(nameTot)				
				