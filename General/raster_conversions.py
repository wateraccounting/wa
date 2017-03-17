# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 19:04:22 2016

@author: tih
"""
import pandas as pd
import glob
import gdal
import osr
import os
import numpy as np
import subprocess
from pyproj import Proj, transform
import scipy.interpolate

def Open_array_info(filename=''):

    f = gdal.Open(r"%s" %filename)
    if f is None:
        print '%s does not exists' %filename
    else:					
        geo_out = f.GetGeoTransform()
        proj = f.GetProjection()
        size_X = f.RasterXSize
        size_Y = f.RasterYSize
        f = None
    return(geo_out, proj, size_X, size_Y)		
				
def Open_tiff_array(filename='', band=''):	

    f = gdal.Open(filename)
    if f is None:
        print '%s does not exists' %filename
    else:
        if band is '':
            band = 1
        Data = f.GetRasterBand(band).ReadAsArray()				
    return(Data)

def Open_nc_array(NC_filename,Var):
	
    from netCDF4 import Dataset
				
    fh = Dataset(NC_filename, mode='r')
    Data = fh.variables[Var][:]	
				
    return(Data)				
				
def clip_data(input_file, latlim, lonlim):
    """
    Clip the data to the defined extend of the user (latlim, lonlim) or to the
    extend of the DEM tile

    Keyword Arguments:
    input_file -- output data, output of the clipped dataset
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    """
				
    if input_file.split('.')[-1] == 'tif':
        dest_in = gdal.Open(input_file)               					
    else:
        dest_in = input_file
	
    # Open Array
    data_in = dest_in.GetRasterBand(1).ReadAsArray()	

    # Define the array that must remain
    Geo_in = dest_in.GetGeoTransform()
    Geo_in = list(Geo_in)			
    Start_x = np.max([int(round(((lonlim[0] - Geo_in[1]) - Geo_in[0])/ Geo_in[1])),0])   				
    End_x = np.min([int(round(((lonlim[1] + Geo_in[1]) - Geo_in[0])/ Geo_in[1])),int(dest_in.RasterXSize)])				
				
    Start_y = np.max([int(round((Geo_in[3] - (latlim[1] - Geo_in[5]))/ -Geo_in[5])),0])
    End_y = np.min([int(round(((latlim[0] + Geo_in[5]) - Geo_in[3])/ Geo_in[5])), int(dest_in.RasterYSize)])	

    #Create new GeoTransform
    Geo_in[0] = Geo_in[0] + Start_x * Geo_in[1]
    Geo_in[3] = Geo_in[3] + Start_y * Geo_in[5]
    Geo_out = tuple(Geo_in)
				
    data = np.zeros([End_y - Start_y, End_x - Start_x])				

    data = data_in[Start_y:End_y,Start_x:End_x] 

    return(data, Geo_out)
				
				
def reproject_dataset_epsg(dataset, pixel_spacing, epsg_to, method = 2):
    """
    A sample function to reproject and resample a GDAL dataset from within
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure is slightly long-winded, but
    goes like this:

    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection
    """

    # 1) Open the dataset
    g = gdal.Open(dataset)
    if g is None:
        print 'input folder does not exist'

    # Get EPSG code
    epsg_from = Get_epsg(g)
   
    # Get the Geotransform vector:
    geo_t = g.GetGeoTransform()
    # Vector components:
    # 0- The Upper Left easting coordinate (i.e., horizontal)
    # 1- The E-W pixel spacing
    # 2- The rotation (0 degrees if image is "North Up")
    # 3- The Upper left northing coordinate (i.e., vertical)
    # 4- The rotation (0 degrees)
    # 5- The N-S pixel spacing, negative as it is counted from the UL corner
    x_size = g.RasterXSize  # Raster xsize
    y_size = g.RasterYSize  # Raster ysize

    epsg_to = int(epsg_to)

    # 2) Define the UK OSNG, see <http://spatialreference.org/ref/epsg/27700/>
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(epsg_to)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(epsg_from)

    inProj = Proj(init='epsg:%d' %epsg_from)
    outProj = Proj(init='epsg:%d' %epsg_to)
				
    # Up to here, all  the projection have been defined, as well as a
    # transformation from the from to the to
    ulx, uly = transform(inProj,outProj,geo_t[0], geo_t[3])
    lrx, lry = transform(inProj,outProj,geo_t[0] + geo_t[1] * x_size,
                                        geo_t[3] + geo_t[5] * y_size)

    # See how using 27700 and WGS84 introduces a z-value!
    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName('MEM')

    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    col = int((lrx - ulx)/pixel_spacing)
    rows = int((uly - lry)/pixel_spacing)

    # Re-define lr coordinates based on whole number or rows and columns
    (lrx, lry) = (ulx + col * pixel_spacing, uly -
                  rows * pixel_spacing)
																		
    dest = mem_drv.Create('', col, rows, 1, gdal.GDT_Float32)
    if dest is None:
        print 'input folder to large for memory, clip input map'
     
   # Calculate the new geotransform
    new_geo = (ulx, pixel_spacing, geo_t[2], uly,
               geo_t[4], - pixel_spacing)
    
    # Set the geotransform
    dest.SetGeoTransform(new_geo)
    dest.SetProjection(osng.ExportToWkt())
      
    # Perform the projection/resampling
    if method is 1:				
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(),gdal.GRA_NearestNeighbour)
    if method is 2:				
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(),gdal.GRA_Bilinear)						
    if method is 3:				
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Lanczos)
    if method is 4:				
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Average)
    return dest, ulx, lry, lrx, uly, epsg_to

def reproject_MODIS(input_name, epsg_to):       
    '''
    Reproject the merged data file
	
    Keywords arguments:
    output_folder -- 'C:/file/to/path/'
    '''                    
    # Define the output name
    name_out = ''.join(input_name.split(".")[:-1]) + '_reprojected.tif'
    
    # Get environmental variable
    WA_env_paths = os.environ["WA_PATHS"].split(';')
    GDAL_env_path = WA_env_paths[0]
    GDALWARP_PATH = os.path.join(GDAL_env_path, 'gdalwarp.exe')

    # find path to the executable
    fullCmd = ' '.join(["%s" %(GDALWARP_PATH), '-overwrite -s_srs "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"', '-t_srs EPSG:%s -of GTiff' %(epsg_to), input_name, name_out])   
    process = subprocess(fullCmd)
    process.wait() 
				
    return(name_out)  
				
def reproject_dataset_example(dataset, dataset_example,method=1):

    # open dataset that must be transformed    
    g = gdal.Open(dataset)
    epsg_from = Get_epsg(g)	   

    # open dataset that is used for transforming the dataset
    gland=gdal.Open(dataset_example) 
    epsg_to = Get_epsg(gland)	

    # Set the EPSG codes
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(epsg_to)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(epsg_from)

    # Get shape and geo transform from example				
    geo_land = gland.GetGeoTransform()			
    col=gland.RasterXSize
    rows=gland.RasterYSize

    # Create new raster			
    mem_drv = gdal.GetDriverByName('MEM')
    dest1 = mem_drv.Create('', col, rows, 1, gdal.GDT_Float32)
    dest1.SetGeoTransform(geo_land)
    dest1.SetProjection(osng.ExportToWkt())
    
    # Perform the projection/resampling
    if method is 1:				
        gdal.ReprojectImage(g, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_NearestNeighbour)
    if method is 2:				
        gdal.ReprojectImage(g, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Bilinear)
    if method is 3:				
        gdal.ReprojectImage(g, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Lanczos)
    if method is 4:				
        gdal.ReprojectImage(g, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Average)
    return(dest1)				
				
def Get_epsg(g):				
			
    try:
        # Get info of the dataset that is used for transforming     
        g_proj = g.GetProjection()
        Projection=g_proj.split('EPSG","')
        epsg_to=int((str(Projection[-1]).split(']')[0])[0:-1])				      
    except:
       epsg_to=4326	
       #print 'Was not able to get the projection, so WGS84 is assumed'							
    return(epsg_to)			

def gap_filling(dataset,NoDataValue):
    """
    This function fills the no data gaps in a numpy array
				
    Keyword arguments:
    dataset -- 'C:/'  path to the source data (dataset that must be filled)
    NoDataValue -- Value that must be filled
    """
    import wa.General.data_conversions as DC	
	
    # Open the numpy array
    data = Open_tiff_array(dataset)

    # fill the no data values
    if NoDataValue is np.nan:
        mask = ~(np.isnan(data))
    else:
        mask = ~(data==NoDataValue)
    xx, yy = np.meshgrid(np.arange(data.shape[1]), np.arange(data.shape[0]))
    xym = np.vstack( (np.ravel(xx[mask]), np.ravel(yy[mask])) ).T
    data0 = np.ravel( data[:,:][mask] )
    interp0 = scipy.interpolate.NearestNDInterpolator( xym, data0 )
    data_end = interp0(np.ravel(xx), np.ravel(yy)).reshape( xx.shape )
    EndProduct=dataset[:-4] + '_GF.tif'	
		
    # collect the geoinformation			
    geo_out, proj, size_X, size_Y = Open_array_info(dataset)
				
    # Save the filled array as geotiff		
    DC.Save_as_tiff(name=EndProduct, data=data_end, geo=geo_out, projection=proj)			
				
    return (EndProduct)

def Get3Darray_time_series_monthly(Dir_Basin, Data_Path, Startdate, Enddate, Example_data = None):	

    Dates = pd.date_range(Startdate, Enddate, freq = 'MS')
    os.chdir(os.path.join(Dir_Basin,Data_Path))
    i = 0
    for Date in Dates:
        End_tiff_file_name = '%d.%02d.01.tif' %(Date.year, Date.month)					
        file_name = glob.glob('*%s' %End_tiff_file_name)
        file_name_path = os.path.join(Dir_Basin, Data_Path, file_name[0])								
        if Example_data is not None:
            if Date == Dates[0]:
                    geo_out, proj, size_X, size_Y = Open_array_info(Example_data)													
                    dataTot=np.zeros([len(Dates),size_Y,size_X])														
                      									
            dest = reproject_dataset_example(file_name_path, Example_data, method=1)
            Array_one_date = dest.GetRasterBand(1).ReadAsArray() 								
        else: 								
            if Date is Dates[0]:
                    geo_out, proj, size_X, size_Y = Open_array_info(file_name_path)													
                    dataTot=np.zeros([len(Dates),size_Y,size_X])			
            Array_one_date = Open_tiff_array(file_name_path)
								
        dataTot[i,:,:]	 = Array_one_date						
        i += 1
								
    return(dataTot)		

def Vector_to_Raster(Dir, shapefile_name, reference_raster_data_name):

    from osgeo import gdal, ogr

    geo, proj, size_X, size_Y=Open_array_info(reference_raster_data_name)

    x_min = geo[0]
    x_max = geo[0] + size_X * geo[1]
    y_min = geo[3] + size_Y * geo[5]
    y_max = geo[3]
    pixel_size = geo[1]				
				
    # Filename of the raster Tiff that will be created
    Dir_Basin_Shape = os.path.join(Dir,'Basin')	
    if not os.path.exists(Dir_Basin_Shape):
        os.mkdir(Dir_Basin_Shape)					

    Basename = os.path.basename(shapefile_name)
    Dir_Raster_end = os.path.join(Dir_Basin_Shape, os.path.splitext(Basename)[0]+'.tif')				

    # Open the data source and read in the extent
    source_ds = ogr.Open(shapefile_name)
    source_layer = source_ds.GetLayer()

    # Create the destination data source
    x_res = int(round((x_max - x_min) / pixel_size))
    y_res = int(round((y_max - y_min) / pixel_size))

    # Create tiff file
    target_ds = gdal.GetDriverByName('GTiff').Create(Dir_Raster_end, x_res, y_res, 1, gdal.GDT_Float32, ['COMPRESS=LZW'])
    target_ds.SetGeoTransform(geo)
    srse = osr.SpatialReference()
    srse.SetWellKnownGeogCS(proj)
    target_ds.SetProjection(srse.ExportToWkt())
    band = target_ds.GetRasterBand(1)
    target_ds.GetRasterBand(1).SetNoDataValue(-9999)				
    band.Fill(-9999)

    # Rasterize the shape and save it as band in tiff file
    gdal.RasterizeLayer(target_ds, [1], source_layer, None, None, [1], ['ALL_TOUCHED=TRUE'])
    target_ds = None
	
    # Open array
    Raster_Basin = Open_tiff_array(Dir_Raster_end)
			
    return(Raster_Basin)				

						
								