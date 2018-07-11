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
import pandas as pd
import numpy as np
import netCDF4
import time

def Convert_nc_to_tiff(input_nc, output_folder):
    """
    This function converts the nc file into tiff files

    Keyword Arguments:
    input_nc -- name, name of the adf file
    output_folder -- Name of the output tiff file
    """
    from datetime import date
    import wa.General.raster_conversions as RC

    #All_Data = RC.Open_nc_array(input_nc)

    if type(input_nc) == str:
        nc = netCDF4.Dataset(input_nc)
    elif type(input_nc) == list:
        nc = netCDF4.MFDataset(input_nc)

    Var = nc.variables.keys()[-1]
    All_Data = nc[Var]

    geo_out, epsg, size_X, size_Y, size_Z, Time = RC.Open_nc_info(input_nc)

    if epsg == 4326:
        epsg = 'WGS84'

    # Create output folder if needed
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    for i in range(0,size_Z):
        if not Time == -9999:
            time_one = Time[i]
            d = date.fromordinal(time_one)
            name = os.path.splitext(os.path.basename(input_nc))[0]
            nameparts = name.split('_')[0:-2]
            name_out = os.path.join(output_folder, '_'.join(nameparts) + '_%d.%02d.%02d.tif' %(d.year, d.month, d.day))
            Data_one = All_Data[i,:,:]
        else:
            name=os.path.splitext(os.path.basename(input_nc))[0]
            name_out = os.path.join(output_folder, name + '.tif')
            Data_one = All_Data[:,:]


        Save_as_tiff(name_out, Data_one, geo_out, epsg)

    return()


def Convert_grb2_to_nc(input_wgrib, output_nc, band):

    import wa.General.raster_conversions as RC

    # Get environmental variable
    WA_env_paths = os.environ["WA_PATHS"].split(';')
    GDAL_env_path = WA_env_paths[0]
    GDAL_TRANSLATE_PATH = os.path.join(GDAL_env_path, 'gdal_translate.exe')

    # Create command
    fullCmd = ' '.join(['"%s" -of netcdf -b %d' %(GDAL_TRANSLATE_PATH, band), input_wgrib, output_nc])  # -r {nearest}

    RC.Run_command_window(fullCmd)

    return()

def Convert_adf_to_tiff(input_adf, output_tiff):
    """
    This function converts the adf files into tiff files

    Keyword Arguments:
    input_adf -- name, name of the adf file
    output_tiff -- Name of the output tiff file
    """
    import wa.General.raster_conversions as RC

    # Get environmental variable
    WA_env_paths = os.environ["WA_PATHS"].split(';')
    GDAL_env_path = WA_env_paths[0]
    GDAL_TRANSLATE_PATH = os.path.join(GDAL_env_path, 'gdal_translate.exe')

    # convert data from ESRI GRID to GeoTIFF
    fullCmd = ('"%s" -co COMPRESS=DEFLATE -co PREDICTOR=1 -co '
                   'ZLEVEL=1 -of GTiff %s %s') % (GDAL_TRANSLATE_PATH, input_adf, output_tiff)

    RC.Run_command_window(fullCmd)

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
    projection -- integer, the EPSG code
    """
    # save as a geotiff
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(name, int(data.shape[1]), int(data.shape[0]), 1,
                           gdal.GDT_Float32, ['COMPRESS=LZW'])
    srse = osr.SpatialReference()
    if projection == '':
        srse.SetWellKnownGeogCS("WGS84")

    else:
        try:
            if not srse.SetWellKnownGeogCS(projection) == 6:
                srse.SetWellKnownGeogCS(projection)
            else:
                try:
                    srse.ImportFromEPSG(int(projection))
                except:
                    srse.ImportFromWkt(projection)
        except:
            try:
                srse.ImportFromEPSG(int(projection))
            except:
                srse.ImportFromWkt(projection)

    dst_ds.SetProjection(srse.ExportToWkt())
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform(geo)
    dst_ds.GetRasterBand(1).WriteArray(data)
    dst_ds = None
    return()

def Save_as_MEM(data='', geo='', projection=''):
    """
    This function save the array as a memory file

    Keyword arguments:
    data -- [array], dataset of the geotiff
    geo -- [minimum lon, pixelsize, rotation, maximum lat, rotation,
            pixelsize], (geospatial dataset)
    projection -- interger, the EPSG code
    """
    # save as a geotiff
    driver = gdal.GetDriverByName("MEM")
    dst_ds = driver.Create('', int(data.shape[1]), int(data.shape[0]), 1,
                           gdal.GDT_Float32, ['COMPRESS=LZW'])
    srse = osr.SpatialReference()
    if projection == '':
        srse.SetWellKnownGeogCS("WGS84")
    else:
        srse.SetWellKnownGeogCS(projection)
    dst_ds.SetProjection(srse.ExportToWkt())
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform(geo)
    dst_ds.GetRasterBand(1).WriteArray(data)
    return(dst_ds)

def Save_as_NC(namenc, DataCube, Var, Reference_filename,  Startdate = '', Enddate = '', Time_steps = '', Scaling_factor = 1):
    """
    This function save the array as a netcdf file

    Keyword arguments:
    namenc -- string, complete path of the output file with .nc extension
    DataCube -- [array], dataset of the nc file, can be a 2D or 3D array [time, lat, lon], must be same size as reference data
    Var -- string, the name of the variable
    Reference_filename -- string, complete path to the reference file name
    Startdate -- 'YYYY-mm-dd', needs to be filled when you want to save a 3D array,  defines the Start datum of the dataset
    Enddate -- 'YYYY-mm-dd', needs to be filled when you want to save a 3D array, defines the End datum of the dataset
    Time_steps -- 'monthly' or 'daily', needs to be filled when you want to save a 3D array, defines the timestep of the dataset
    Scaling_factor -- number, scaling_factor of the dataset, default = 1
    """
    # Import modules
    import wa.General.raster_conversions as RC
    from netCDF4 import Dataset

    if not os.path.exists(namenc):

        # Get raster information
        geo_out, proj, size_X, size_Y = RC.Open_array_info(Reference_filename)

        # Create the lat/lon rasters
        lon = np.arange(size_X)*geo_out[1]+geo_out[0] - 0.5 * geo_out[1]
        lat = np.arange(size_Y)*geo_out[5]+geo_out[3] - 0.5 * geo_out[5]

        # Create the nc file
        nco = Dataset(namenc, 'w', format='NETCDF4_CLASSIC')
        nco.description = '%s data' %Var

        # Create dimensions, variables and attributes:
        nco.createDimension('longitude', size_X)
        nco.createDimension('latitude', size_Y)

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
            nco.createDimension('time', None)
            timeo = nco.createVariable('time', 'f4', ('time',))
            timeo.units = '%s' %Time_steps
            timeo.standard_name = 'time'

        # Create the lon variable
        lono = nco.createVariable('longitude', 'f8', ('longitude',))
        lono.standard_name = 'longitude'
        lono.units = 'degrees_east'
        lono.pixel_size = geo_out[1]

        # Create the lat variable
        lato = nco.createVariable('latitude', 'f8', ('latitude',))
        lato.standard_name = 'latitude'
        lato.units = 'degrees_north'
        lato.pixel_size = geo_out[5]

        # Create container variable for CRS: lon/lat WGS84 datum
        crso = nco.createVariable('crs', 'i4')
        crso.long_name = 'Lon/Lat Coords in WGS84'
        crso.grid_mapping_name = 'latitude_longitude'
        crso.projection = proj
        crso.longitude_of_prime_meridian = 0.0
        crso.semi_major_axis = 6378137.0
        crso.inverse_flattening = 298.257223563
        crso.geo_reference = geo_out

        # Create the data variable
        if Startdate is not '':
            preco = nco.createVariable('%s' %Var, 'f8',  ('time', 'latitude', 'longitude'), zlib=True, least_significant_digit=1)
            timeo[:]=time_or
        else:
            preco = nco.createVariable('%s' %Var, 'f8',  ('latitude', 'longitude'), zlib=True, least_significant_digit=1)

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
                preco[i,:,:] = DataCube[i,:,:]*1./np.float(Scaling_factor)
        else:
            preco[:,:] = DataCube[:,:] * 1./np.float(Scaling_factor)

        nco.close()
    return()

def Create_NC_name(Var, Simulation, Dir_Basin, sheet_nmbr, info = ''):

    # Create the output name
    nameOut=''.join(['_'.join([Var,'Simulation%d' % Simulation,'_'.join(info)]),'.nc'])
    namePath = os.path.join(Dir_Basin,'Simulations','Simulation_%d' %Simulation, 'Sheet_%d' %sheet_nmbr)
    if not os.path.exists(namePath):
        os.makedirs(namePath)
    nameTot=os.path.join(namePath,nameOut)

    return(nameTot)

def Create_new_NC_file(nc_outname, Basin_Example_File, Basin):

    # Open basin file
    dest = gdal.Open(Basin_Example_File)
    Basin_array = dest.GetRasterBand(1).ReadAsArray()
    Basin_array[np.isnan(Basin_array)] = -9999
    Basin_array[Basin_array<0] = -9999

    # Get Basic information
    Geo = dest.GetGeoTransform()
    size_X = dest.RasterXSize
    size_Y = dest.RasterYSize
    epsg = dest.GetProjection()

    # Get Year and months
    year = int(os.path.basename(nc_outname).split(".")[0])
    Dates = pd.date_range("%d-01-01" %year, "%d-12-31" %year, freq = "MS")

    # Latitude and longitude
    lons = np.arange(size_X)*Geo[1]+Geo[0] + 0.5 * Geo[1]
    lats = np.arange(size_Y)*Geo[5]+Geo[3] + 0.5 * Geo[5]

    # Create NetCDF file
    nco = netCDF4.Dataset(nc_outname, 'w', format = 'NETCDF4_CLASSIC')
    nco.set_fill_on()
    nco.description = '%s' %Basin

    # Create dimensions
    nco.createDimension('latitude', size_Y)
    nco.createDimension('longitude', size_X)
    nco.createDimension('time', None)

    # Create NetCDF variables
    crso = nco.createVariable('crs', 'i4')
    crso.long_name = 'Lon/Lat Coords in WGS84'
    crso.standard_name = 'crs'
    crso.grid_mapping_name = 'latitude_longitude'
    crso.projection = epsg
    crso.longitude_of_prime_meridian = 0.0
    crso.semi_major_axis = 6378137.0
    crso.inverse_flattening = 298.257223563
    crso.geo_reference = Geo

    ######################### Save Rasters in NetCDF ##############################

    lato = nco.createVariable('latitude', 'f8', ('latitude',))
    lato.units = 'degrees_north'
    lato.standard_name = 'latitude'
    lato.pixel_size = Geo[5]

    lono = nco.createVariable('longitude', 'f8', ('longitude',))
    lono.units = 'degrees_east'
    lono.standard_name = 'longitude'
    lono.pixel_size = Geo[1]

    timeo = nco.createVariable('time', 'f4', ('time',))
    timeo.units = 'Monthly'
    timeo.standard_name = 'time'

    # Variables
    basin_var = nco.createVariable('Landuse', 'i',
                                           ('latitude', 'longitude'),
                                           fill_value=-9999)
    basin_var.long_name = 'Landuse'
    basin_var.grid_mapping = 'crs'

    # Create time unit
    i = 0
    time_or=np.zeros(len(Dates))
    for Date in Dates:
        time_or[i] = Date.toordinal()
        i += 1

    # Load data
    lato[:] = lats
    lono[:] = lons
    timeo[:] = time_or
    basin_var[:,:] = Basin_array

    # close the file
    time.sleep(1)
    nco.close()
    return()

def Add_NC_Array_Variable(nc_outname, Array, name, unit, Scaling_factor = 1):

    # create input array
    Array[np.isnan(Array)] = -9999 * np.float(Scaling_factor)
    Array = np.int_(Array * 1./np.float(Scaling_factor))

    # Create NetCDF file
    nco = netCDF4.Dataset(nc_outname, 'r+', format = 'NETCDF4_CLASSIC')
    nco.set_fill_on()

    paro = nco.createVariable('%s' %name, 'i',
                                   ('time', 'latitude', 'longitude'),fill_value=-9999,
                                    zlib=True, least_significant_digit=0)

    paro.scale_factor = Scaling_factor
    paro.add_offset = 0.00
    paro.grid_mapping = 'crs'
    paro.long_name = name
    paro.units = unit
    paro.set_auto_maskandscale(False)

    # Set the data variable
    paro[:,:,:] = Array

    # close the file
    time.sleep(1)
    nco.close()

    return()

def Add_NC_Array_Static(nc_outname, Array, name, unit, Scaling_factor = 1):

    # create input array
    Array[np.isnan(Array)] = -9999 * np.float(Scaling_factor)
    Array = np.int_(Array * 1./np.float(Scaling_factor))

    # Create NetCDF file
    nco = netCDF4.Dataset(nc_outname, 'r+', format = 'NETCDF4_CLASSIC')
    nco.set_fill_on()

    paro = nco.createVariable('%s' %name, 'i',
                                   ('latitude', 'longitude'),fill_value=-9999,
                                    zlib=True, least_significant_digit=0)

    paro.scale_factor = Scaling_factor
    paro.add_offset = 0.00
    paro.grid_mapping = 'crs'
    paro.long_name = name
    paro.units = unit
    paro.set_auto_maskandscale(False)

    # Set the data variable
    paro[:,:] = Array

    # close the file
    time.sleep(1)
    nco.close()

    return()

def Convert_dict_to_array(River_dict, Array_dict, Reference_data):

    import numpy as np
    import os
    import wa.General.raster_conversions as RC

    if os.path.splitext(Reference_data)[-1] == '.nc':
        # Get raster information
        geo_out, proj, size_X, size_Y, size_Z, Time = RC.Open_nc_info(Reference_data)
    else:
        # Get raster information
        geo_out, proj, size_X, size_Y = RC.Open_array_info(Reference_data)

    # Create ID Matrix
    y,x = np.indices((size_Y, size_X))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y,size_X),mode='clip').reshape(x.shape)) + 1

    # Get tiff array time dimension:
    time_dimension = int(np.shape(Array_dict[0])[0])

    # create an empty array
    DataCube = np.ones([time_dimension, size_Y, size_X]) * np.nan

    for river_part in range(0,len(River_dict)):
        for river_pixel in range(1,len(River_dict[river_part])):
            river_pixel_ID = River_dict[river_part][river_pixel]
            if len(np.argwhere(ID_Matrix == river_pixel_ID))>0:
                row, col = np.argwhere(ID_Matrix == river_pixel_ID)[0][:]
                DataCube[:,row,col] = Array_dict[river_part][:,river_pixel]

    return(DataCube)

