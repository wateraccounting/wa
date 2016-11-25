# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD9
"""

# import general python modules
import os
import numpy as np
import pandas as pd
from osgeo import osr, gdal
import urllib
from bs4 import BeautifulSoup
import re
import urlparse
import subprocess
import requests
from joblib import Parallel, delayed

# Water Accounting modules
from wa import WebAccounts
from wa import WA_Paths

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, cores):
    """
    This function downloads MOD9 daily data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -90 and 90)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine. It can be 'False'
             to avoid using parallel computing routines.
    """

    # Check start and end date and otherwise set the date to max
    if not Startdate:
        Startdate = pd.Timestamp('2000-02-24')
    if not Enddate: 
        Enddate = pd.Timestamp('Now')
    
    # Make an array of the days of which the NDVI is taken
    Dates = Make_TimeStamps(Startdate,Enddate)    
    
    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    if latlim[0] < -90 or latlim[1] > 90:
        print 'Latitude above 90N or below 90S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0], -90)
        latlim[1] = np.min(latlim[1], 90)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0], -180)
        lonlim[1] = np.min(lonlim[1], 180)
        
    # Make directory for the MODIS NDVI data
    Dir = Dir.replace("/", os.sep)						
    output_folder = os.path.join(Dir, 'Reflectance', 'MODIS')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Download list (txt file on the internet) which includes the lat and lon information of the MODIS tiles
    nameDownloadtext = 'http://modis-land.gsfc.nasa.gov/pdf/sn_gring_10deg.txt'  
    file_nametext = os.path.join(output_folder, nameDownloadtext.split('/')[-1])
    urllib.urlretrieve(nameDownloadtext, file_nametext)

    # Open text file with tiles which is downloaded before
    tiletext=np.genfromtxt(file_nametext,skip_header=7,skip_footer=1,usecols=(0,1,2,3,4,5,6,7,8,9))
    tiletext2=tiletext[tiletext[:,2]>=-900,:]
            
    # This function converts the values in the text file into horizontal and vertical number of the tiles which must be downloaded to cover the extent defined by the user
    TilesVertical, TilesHorizontal = Tiles_to_download(tiletext2=tiletext2,lonlim1=lonlim,latlim1=latlim)
            
    # Pass variables to parallel function and run
    args = [output_folder, TilesVertical, TilesHorizontal, lonlim, latlim]
    if not cores:
        for Date in Dates:
            RetrieveData(Date, args)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(RetrieveData)(Date, args)
                                                 for Date in Dates)
    # Remove all .hdf files
    for f in os.listdir(output_folder):
        if re.search(".hdf", f) or re.search(".txt", f):
            os.remove(os.path.join(output_folder, f))
        
	return results		

def RetrieveData(Date, args):
    """
    This function retrieves MOD9 Reflectance data for a given date from the
    http://e4ftl01.cr.usgs.gov/ server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, TilesVertical, TilesHorizontal, lonlim, latlim] = args

    # Collect the data from the MODIS webpage and returns the data and lat and long in meters of those tiles
    try:
        Collect_data(TilesHorizontal, TilesVertical, Date, output_folder)
    except:
        print "Was not able to download the file"  
         
    # Reproject the data to the WGS84 projection
    try:									
        name1, name2 = Reproject_data(output_folder)
    except:
        print "Was not able to reproject the file" 
              
    # Clip the data 
    try:														
        nameOut = Clip_data(output_folder, lonlim, latlim, name2)
    except:
        print "Was not able to clip the file" 
                  
    # Resample data
    try:																		
        data = Resample_data(output_folder,nameOut,lonlim,latlim)
    except:
        print "Was not able to resample the file"   
                
    # remove the side products       
    os.remove(os.path.join(output_folder, name1))
    os.remove(os.path.join(output_folder, name2))
    os.remove(os.path.join(output_folder, nameOut))
                
    # Save results as Gtiff
    NDVIfileName = os.path.join(output_folder, 'Reflectance_MOD09GQ_-_daily_' + Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + Date.strftime('%d') + '.tif')
    Save_as_Gtiff(data, NDVIfileName, lonlim, latlim)                     
                    
    return True

def Make_TimeStamps(Startdate,Enddate):
    '''
    This function determines all time steps of which the Reflecance must be downloaded   
    The time stamps are daily.
	
    Keywords arguments:
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    '''
    
    Dates = pd.date_range(Startdate, Enddate, freq = 'D')
    
    return(Dates)
            
            

def Resample_data(output_folder,nameOut,lonlim1,latlim1):
    '''
    This function resample the dataset
	
    Keywords arguments:
    output_folder -- 'C:/file/to/path/'
    nameOut -- Name of the dataset that must be resampled
    lonlim1 -- [ymin, ymax] (longitude limits of the chunk or whole image)
    latlim1 -- [ymin, ymax] (latitude limits of the chunk or whole image) 
    '''
    # Open dataset that must be resampled  
    g = gdal.Open(nameOut)

    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName( 'MEM' )
   
    # Size of the new array
    ncol = int((lonlim1[1] - lonlim1[0]) / 0.0025)
    nrow = int((latlim1[1] - latlim1[0]) / 0.0025)
    dest2 = mem_drv.Create('', ncol, nrow, 1, gdal.GDT_Float32)

    # Set the geotransform of the new resampled array
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(int(4326))
    dest2.SetGeoTransform([lonlim1[0], 0.0025, 0.0, latlim1[1], 0.0, -0.0025])
    dest2.SetProjection (osng.ExportToWkt())
   
    # projection of the old array
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(int(4326))
   
    # Perform the projection/resampling 
    res = gdal.ReprojectImage(g, dest2 ,wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Bilinear)   

    # Open the array of the resampled data   
    band = dest2.GetRasterBand(1)
    data = np.flipud(band.ReadAsArray(0, 0, ncol, nrow))
 
    # remove the links to the images	 
    g = None
    dest2 = None
    return(data)   
                
                
def Clip_data(output_folder, lonlim1, latlim1, name2):
    '''
    This function clips the dataset
	
    Keywords arguments:
    output_folder -- 'C:/file/to/path/'
    lonlim1 -- [ymin, ymax] (longitude limits of the chunk or whole image)
    latlim1 -- [ymin, ymax] (latitude limits of the chunk or whole image) 
    name2 -- Name of the dataset that must be clipped			
    '''
    # Define the output name
    nameOut = os.path.join(output_folder, 'Clipped.tif')

    # find path to the executable
    path = WA_Paths.Paths(Type = 'GDAL')
    if path is '':
        # Apply the clipping part by using gdal_translate
        fullCmd = ' '.join(['gdal_translate -projwin %s %s %s %s' % (lonlim1[0] - 0.004, latlim1[1] + 0.004, lonlim1[1] + 0.004, latlim1[0] - 0.004), '-of GTiff', name2, nameOut])  # -r {nearest}

    else:		 
        gdal_translate_path = os.path.join(path,'gdal_translate.exe')

        # Apply the clipping part by using gdal_translate
        fullCmd = ' '.join(['"%s" -projwin %s %s %s %s' % (gdal_translate_path, lonlim1[0] - 0.004, latlim1[1] + 0.004, lonlim1[1] + 0.004, latlim1[0] - 0.004), '-of GTiff', name2, nameOut])  # -r {nearest}

    process = subprocess.Popen(fullCmd)
    process.wait() 
    return(nameOut)
    
def Tiles_to_download(tiletext2,lonlim1,latlim1):
    '''
    Defines the MODIS tiles that must be downloaded in order to cover the latitude and longitude limits
	
    Keywords arguments:
    tiletext2 -- 'C:/file/to/path/' to path of the txt file with all the MODIS tiles extents
    lonlim1 -- [ymin, ymax] (longitude limits of the chunk or whole image)
    latlim1 -- [ymin, ymax] (latitude limits of the chunk or whole image) 	
    '''   
    # calculate min and max longitude and latitude
    # lat down    lat up      lon left     lon right
    tiletextExtremes = np.empty([len(tiletext2),6])
    tiletextExtremes[:,0] = tiletext2[:,0]
    tiletextExtremes[:,1] = tiletext2[:,1]
    tiletextExtremes[:,2] = np.minimum(tiletext2[:,3], tiletext2[:,9])
    tiletextExtremes[:,3] = np.maximum(tiletext2[:,5], tiletext2[:,7])
    tiletextExtremes[:,4] = np.minimum(tiletext2[:,2], tiletext2[:,4])
    tiletextExtremes[:,5] = np.maximum(tiletext2[:,6], tiletext2[:,8])
    
    # Define the upper left tile
    latlimtiles1UL = tiletextExtremes[np.logical_and(tiletextExtremes[:,2] <= latlim1[1], tiletextExtremes[:,3] >= latlim1[1])]#tiletext2[:,3]>=latlim[0],tiletext2[:,4]>=latlim[0],tiletext2[:,5]>=latlim[0],tiletext2[:,6]>=latlim[0],tiletext2[:,7]>=latlim[0]))]
    latlimtilesUL = latlimtiles1UL[np.logical_and(latlimtiles1UL[:,4] <= lonlim1[0], latlimtiles1UL[:,5] >= lonlim1[0])]
    
    # Define the lower right tile
    latlimtiles1LR = tiletextExtremes[np.logical_and(tiletextExtremes[:,2] <= latlim1[0], tiletextExtremes[:,3] >= latlim1[0])]#tiletext2[:,3]>=latlim[0],tiletext2[:,4]>=latlim[0],tiletext2[:,5]>=latlim[0],tiletext2[:,6]>=latlim[0],tiletext2[:,7]>=latlim[0]))]
    latlimtilesLR = latlimtiles1LR[np.logical_and(latlimtiles1LR[:,4]<=lonlim1[1],latlimtiles1LR[:,5]>=lonlim1[1])]
    
    # Define the total tile
    TotalTiles = np.vstack([latlimtilesUL, latlimtilesLR])
    
    # Find the minimum horizontal and vertical tile value and the maximum horizontal and vertical tile value
    TilesVertical = [TotalTiles[:,0].min(), TotalTiles[:,0].max()]
    TilesHorizontal = [TotalTiles[:,1].min(), TotalTiles[:,1].max()]
    return(TilesVertical, TilesHorizontal)
    
def Reproject_data(output_folder):       
    '''
    Reproject the merged data file
	
    Keywords arguments:
    output_folder -- 'C:/file/to/path/'
    '''     
                
    # Define the input and output name
    name1 = os.path.join(output_folder, 'Merged.tif')
    name2 = os.path.join(output_folder, 'reprojected.tif')

    # Define the projection in EPSG code
    epsg_to = 4326

    # find path to the executable
    path = WA_Paths.Paths(Type = 'GDAL')
    if path is '':	
        # Apply the reprojection by using gdalwarp
        fullCmd = ' '.join(['gdalwarp -overwrite -s_srs "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"', '-t_srs EPSG:%s -of GTiff' %(epsg_to), name1, name2])  # -r {nearest}
 
    else:
        gdalwarp_path = os.path.join(path,'gdalwarp.exe')

        # Apply the reprojection by using gdalwarp
        fullCmd = ' '.join(["%s" %(gdalwarp_path), '-overwrite -s_srs "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"', '-t_srs EPSG:%s -of GTiff' %(epsg_to), name1, name2])  # -r {nearest}

    process = subprocess.Popen(fullCmd)
    process.wait() 
    return(name1, name2)    
    
def Collect_data(TilesHorizontal,TilesVertical,Date,output_folder):
    '''
    This function downloads all the needed MODIS tiles from http://e4ftl01.cr.usgs.gov/MOLT/MOD13Q1.006/ as a hdf file.

    Keywords arguments:
    TilesHorizontal -- [TileMin,TileMax] max and min horizontal tile number	
    TilesVertical -- [TileMin,TileMax] max and min vertical tile number	
    Date -- 'yyyy-mm-dd' 				
    output_folder -- 'C:/file/to/path/'	
    '''
    
    # Make a new tile for the data
    sizeX = int((TilesHorizontal[1] - TilesHorizontal[0] + 1) * 4800)
    sizeY = int((TilesVertical[1] - TilesVertical[0] + 1) * 4800)
    DataTot = np.zeros((sizeY, sizeX))
    
    # Load accounts
    username, password = WebAccounts.Accounts(Type = 'NASA')
    
    # Create the Lat and Long of the MODIS tile in meters
    for Vertical in range(int(TilesVertical[0]), int(TilesVertical[1])+1):
        Distance = 231.65635826395834 # resolution of a MODIS pixel in meter
        countY=(TilesVertical[1] - TilesVertical[0] + 1) - (Vertical - TilesVertical[0]) 
                          
        for Horizontal in range(int(TilesHorizontal[0]), int(TilesHorizontal[1]) + 1):
            countX=Horizontal - TilesHorizontal[0] + 1
            
            # Download the MODIS NDVI data            
            url = 'http://e4ftl01.cr.usgs.gov/MOLT/MOD09GQ.006/' + Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + Date.strftime('%d') + '/' 
            curl_path_exe = WA_Paths.Paths(Type = 'curl.exe')
								
            if curl_path_exe is '':
                 f = os.popen("curl -l " + url, "r")	
            else:														
                 f = os.popen('"%s" -l ' %(curl_path_exe) + url,  "r")
												
            # Sum all the files on the server												
            soup = BeautifulSoup(f, "lxml")
            for i in soup.findAll('a', attrs = {'href': re.compile('(?i)(hdf)$')}):
													
                # Find the file with the wanted tile number													
                Vfile=str(i)[30:32]
                Hfile=str(i)[27:29]
                if int(Vfile) is int(Vertical) and int(Hfile) is int(Horizontal):
																	
                    # Define the whole url name																	
                    full_url = urlparse.urljoin(url, i['href'])
																				
		           # Reset the begin parameters for downloading												
                    downloaded = 0   
                    N=0  
																				
                    # if not downloaded try to download file																	
                    while downloaded == 0:		
																					
                        try:# open http and download whole .hdf       
                            nameDownload = full_url  
                            file_name = os.path.join(output_folder,nameDownload.split('/')[-1])
                            if os.path.isfile(file_name):
                                print "file ", file_name, " already exists"
                                downloaded = 1
                            else:
                                x = requests.get(nameDownload, allow_redirects = False)
                                try:																						
                                    y = requests.get(x.headers['location'], auth = (username, password))
                                except:
                                    y = requests.get(x.headers['location'], auth = (username, password), verify = False)					     																							
                                z = open(file_name, 'wb')
                                z.write(y.content)
                                z.close()
                                statinfo = os.stat(file_name)																									
                                # Say that download was succesfull		
                                if int(statinfo.st_size) > 10000:																								
                                     downloaded = 1
	    			
                        # If download was not succesfull								
                        except:	
													
                            # Try another time                     																				
                            N = N + 1
																				
				  # Stop trying after 10 times																				
                    if N == 10:
                        print 'Data from ' + Date.strftime('%Y-%m-%d') + ' is not available'
                        downloaded = 1
                    try:
                        # Open .hdf only band with NDVI and collect all tiles to one array
                        dataset = gdal.Open(file_name)
                        sdsdict = dataset.GetMetadata('SUBDATASETS')
                        sdslist = [sdsdict[k] for k in sdsdict.keys() if '_2_NAME' in k]
                        sds = []
                       
                        for n in sdslist:
                            sds.append(gdal.Open(n))
                            full_layer = [i for i in sdslist if 'sur_refl_b01_1' in i]
                            idx = sdslist.index(full_layer[0])
                            if Horizontal == TilesHorizontal[0] and Vertical == TilesVertical[0]:
                                geo_t = sds[idx].GetGeoTransform()  
                                
                                # get the projection value
                                proj = sds[idx].GetProjection()

                            data = sds[idx].ReadAsArray() 
                            countYdata = (TilesVertical[1] - TilesVertical[0] + 2) - countY
                            DataTot[int((countYdata - 1) * 4800):int(countYdata * 4800), int((countX - 1) * 4800):int(countX * 4800)]=data
                        del data
                        
                    # if the tile not exists or cannot be opened, create a nan array with the right projection                          
                    except:
                        if Horizontal==TilesHorizontal[0] and Vertical==TilesVertical[0]:
                             x1 = (TilesHorizontal[0] - 19) * 4800 * Distance
                             x4 = (TilesVertical[0] - 9) * 4800 * -1 * Distance
                             geo = 	[x1, Distance, 0.0, x4, 0.0, -Distance]															
                             geo_t=tuple(geo)

                        proj='PROJCS["unnamed",GEOGCS["Unknown datum based upon the custom spheroid",DATUM["Not specified (based on custom spheroid)",SPHEROID["Custom spheroid",6371007.181,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Sinusoidal"],PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'																													 
                        data=np.ones((4800,4800)) * (-9999)
                        countYdata=(TilesVertical[1] - TilesVertical[0] + 2) - countY
                        DataTot[(countYdata - 1) * 4800:countYdata * 4800,(countX - 1) * 4800:countX * 4800] = data

    # Make geotiff file      
    name2 = os.path.join(output_folder, 'Merged.tif')
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(name2, DataTot.shape[1], DataTot.shape[0], 1, gdal.GDT_Float32, ['COMPRESS=LZW'])     
    try:
         dst_ds.SetProjection(proj)
    except:
        proj='PROJCS["unnamed",GEOGCS["Unknown datum based upon the custom spheroid",DATUM["Not specified (based on custom spheroid)",SPHEROID["Custom spheroid",6371007.181,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Sinusoidal"],PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'																													 
        x1 = (TilesHorizontal[0] - 18) * 4800 * Distance
        x4 = (TilesVertical[0] - 9) * 4800 * -1 * Distance
        geo = [x1, Distance, 0.0, x4, 0.0, -Distance]															
        geo_t = tuple(geo)        
        dst_ds.SetProjection(proj)		
        									
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform(geo_t)
    dst_ds.GetRasterBand(1).WriteArray(DataTot*10000)
    dst_ds = None
    sds = None
    return()
    
def Save_as_Gtiff(A,NDVIfileName,lonlim,latlim):
    '''
	This function saves an array as a tiff file

    Keywords arguments:
    A -- Numpy array (includes values for the tiff file)
    NDVIfileName -- 'C:/file/to/path/' (the output tiff file)	
    lonlim -- [ymin, ymax] (longitude limits of the whole image)
    latlim -- [ymin, ymax] (latitude limits of the whole image) 	
    '''    
    # Make geotiff file              
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(NDVIfileName, A.shape[1], A.shape[0], 1, gdal.GDT_Float32, ['COMPRESS=LZW'])                    
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")
    dst_ds.SetProjection(srs.ExportToWkt())
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform([lonlim[0],0.0025,0,latlim[1],0,-0.0025])
    dst_ds.GetRasterBand(1).WriteArray(np.flipud(A))
    dst_ds = None
