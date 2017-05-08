# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/JRC
"""

# import general python modules
import os
import numpy as np
import shutil

# Water Accounting modules
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC

def DownloadData(Dir,latlim, lonlim):
    """
    This function downloads JRC data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    latlim -- [ymin, ymax] (values must be between -90 and 90)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)

    """

    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    if latlim[0] < -90 or latlim[1] > 90:
        print 'Latitude above 90N or below 90S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0], -90)
        latlim[1] = np.min(latlim[1], 90)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0], -180)
        lonlim[1] = np.min(lonlim[1], 180)
        
    # Make directory for the JRC water occurrence data
    Dir = Dir.replace("/", os.sep)						
    output_folder = os.path.join(Dir, 'JRC', 'Occurrence')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    fileName_out = os.path.join(output_folder, 'JRC_Occurrence_percent.tif')
    
    if not os.path.exists(fileName_out):
        
        # This function defines the name of dataset that needs to be collected
        Names_to_download = Tiles_to_download(lonlim,latlim)
            
        # Pass variables to parallel function and run
        args = [output_folder, Names_to_download, lonlim, latlim]
        RetrieveData(args)
        
    else:
        print 'JRC water occurrence map already exists'
           						
    return()	


def RetrieveData(args):
    """
    This function retrieves JRC data for a given date from the
    http://storage.googleapis.com/global-surface-water/downloads/ server.

    Keyword arguments:
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, Names_to_download, lonlim, latlim] = args

    # Collect the data from the JRC webpage and returns the data and lat and long in meters of those tiles
    try:
        Collect_data(Names_to_download, output_folder)
    except:
        print "Was not able to download the file"  
    		
    # Clip the data to the users extend	
    if len(Names_to_download) == 1:
        trash_folder = os.path.join(output_folder, "Trash")
        data_in = os.path.join(trash_folder, Names_to_download[0])
        data_end, geo_end = RC.clip_data(data_in, latlim, lonlim)
    else:
        
        data_end = np.zeros([int((latlim[1] - latlim[0])/0.00025), int((lonlim[1] - lonlim[0])/0.00025)])

        for Name_to_merge in Names_to_download:
            trash_folder = os.path.join(output_folder, "Trash")
            data_in = os.path.join(trash_folder, Name_to_merge)
            geo_out, proj, size_X, size_Y = RC.Open_array_info(data_in)
            lat_min_merge = np.maximum(latlim[0], geo_out[3] + size_Y * geo_out[5])
            lat_max_merge = np.minimum(latlim[1], geo_out[3])                    
            lon_min_merge = np.maximum(lonlim[0], geo_out[0])   
            lon_max_merge = np.minimum(lonlim[1], geo_out[0] + size_X * geo_out[1])       
            
            lonmerge = [lon_min_merge, lon_max_merge]
            latmerge = [lat_min_merge, lat_max_merge]
            data_one, geo_one = RC.clip_data(data_in, latmerge, lonmerge)
            
            Ystart = int((geo_one[3] - latlim[1])/geo_one[5])
            Yend = int(Ystart + np.shape(data_one)[0])
            Xstart = int((geo_one[0] - lonlim[0])/geo_one[1])
            Xend = int(Xstart + np.shape(data_one)[1])           
            
            data_end[Ystart:Yend, Xstart:Xend] = data_one
                    
        geo_end = tuple([lonlim[0], geo_one[1], 0, latlim[1], 0, geo_one[5]])
        
    # Save results as Gtiff
    fileName_out = os.path.join(output_folder, 'JRC_Occurrence_percent.tif')
    DC.Save_as_tiff(name=fileName_out, data=data_end, geo=geo_end, projection='WGS84')
    shutil.rmtree(trash_folder) 
    return True


    
def Tiles_to_download(lonlim, latlim):
    '''
    Defines the JRC tiles that must be downloaded in order to cover the latitude and longitude limits
	
    Keywords arguments:
    lonlim -- [ymin, ymax] (longitude limits of the chunk or whole image)
    latlim -- [ymin, ymax] (latitude limits of the chunk or whole image) 	
    '''   
    latmin = int(np.floor(latlim[0]/10.)*10)
    latmax = int(np.ceil(latlim[1]/10.)*10)
    lonmin = int(np.floor(lonlim[0]/10.)*10)
    lonmax = int(np.ceil(lonlim[1]/10.)*10)
                    
    lat_steps = range(latmin + 10 , latmax + 10 , 10)                                  
    lon_steps = range(lonmin, lonmax, 10)               
 
    Names_to_download = []

    for lon_step in lon_steps:
        if lon_step < 0:
            string_long = "%sW" %abs(lon_step)
        else:
            string_long = "%sE" %lon_step            
        for lat_step in lat_steps:
            if lat_step < 0:
                string_lat = "%sS" %abs(lat_step)
            else:
                string_lat = "%sN" %lat_step              

            Name_to_download = "occurrence_%s_%s.tif" %(string_long, string_lat)
            Names_to_download = np.append(Name_to_download, Names_to_download)

    return(Names_to_download)
    
def Collect_data(Names_to_download, output_folder):
    '''
    This function downloads all the needed JRC tiles from http://e4ftl01.cr.usgs.gov/MOLT/MOD13Q1.006/ as a hdf file.

    Keywords arguments:
    TilesHorizontal -- [TileMin,TileMax] max and min horizontal tile number	
    TilesVertical -- [TileMin,TileMax] max and min vertical tile number	
    Date -- 'yyyy-mm-dd' 				
    output_folder -- 'C:/file/to/path/'	
    '''
    import urllib
    
    for Name_to_download in Names_to_download:
        output_Trash = os.path.join(output_folder, "Trash")
        if not os.path.exists(output_Trash):
            os.mkdir(output_Trash)  
        
        filename = os.path.join(output_Trash, Name_to_download)
        if os.path.exists(filename):
            print "%s already exists" %(Name_to_download)
        else:
           times = 0
           size = 0
           while times < 10 and size < 10000:
               url = "http://storage.googleapis.com/global-surface-water/downloads/occurrence/" + Name_to_download
               code = urllib.urlopen(url).getcode()
               if (code != 404):
                  print "Downloading " + url
                  urllib.urlretrieve(url, filename)
                  times += 1
                  statinfo = os.stat(filename)																									
                  size = int(statinfo.st_size)
               else:
                  print url + " not found"
                  times = 10
        
    return()
    