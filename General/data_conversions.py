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