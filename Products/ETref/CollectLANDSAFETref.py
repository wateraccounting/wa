# -*- coding: utf-8 -*-
'''
Authors: Gert Mulder, Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
'''

# import general python modules
import os
import gdal
import numpy as np
import pandas as pd
import subprocess
import osr
import netCDF4
import glob

# import WA+ modules
from wa.General import data_conversions as DC
from wa.General import raster_conversions as RC
from wa.Products.ETref.SlopeInfluence_ETref import SlopeInfluence	

def CollectLANDSAF(SourceLANDSAF, Dir, Startdate, Enddate, latlim, lonlim):
    """
    This function collects and clip LANDSAF data
				
    Keyword arguments:
    SourceLANDSAF -- 'C:/'  path to the LANDSAF source data (The directory includes SIS and SID)
    Dir -- 'C:/' path to the WA map
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -60 and 60)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    """

    # Make an array of the days of which the ET is taken
    Dates = pd.date_range(Startdate,Enddate,freq = 'D')			
		
    # make directories
    SISdir = os.path.join(Dir,'Landsaf_Clipped','SIS')
    if os.path.exists(SISdir) is False:
        os.makedirs(SISdir)
        
    SIDdir= os.path.join(Dir,'Landsaf_Clipped','SID')
    if os.path.exists(SIDdir) is False:
        os.makedirs(SIDdir)
       
    ShortwaveBasin(SourceLANDSAF, Dir, latlim, lonlim, Dates=[Startdate,Enddate])
    DEMmap_str=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m_3s.tif') 
    geo_out, proj, size_X, size_Y = RC.Open_array_info(DEMmap_str)	

    # Open DEM map 
    demmap = RC.Open_tiff_array(DEMmap_str)
    demmap[demmap<0]=0
            
    # make lat and lon arrays)
    dlat = geo_out[5] 
    dlon = geo_out[1]
    lat = geo_out[3] + (np.arange(size_Y)+0.5)*dlat
    lon = geo_out[0] + (np.arange(size_X)+0.5)*dlon			
				
				
    for date in Dates:
        # day of year
        day=date.dayofyear
        Horizontal, Sloping, sinb, sinb_hor, fi, slope, ID  = SlopeInfluence(demmap,lat,lon,day)   
            
                      
        SIDname = os.path.join(SIDdir,'SAF_SID_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif')
        SISname = os.path.join(SISdir,'SAF_SIS_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif')
            
        #PREPARE SID MAPS
        SIDdest = RC.reproject_dataset_example(SIDname,DEMmap_str,method = 3)																				
        SIDdata=SIDdest.GetRasterBand(1).ReadAsArray()

        #PREPARE SIS MAPS
        SISdest = RC.reproject_dataset_example(SISname,DEMmap_str,method = 3)																				
        SISdata=SISdest.GetRasterBand(1).ReadAsArray()

        # Calculate ShortWave net
        Short_Wave_Net = SIDdata * (Sloping/Horizontal)+SISdata *86400/1e6
        
        # Calculate ShortWave Clear
        Short_Wave = Sloping
        Short_Wave_Clear = Short_Wave *(0.75 + demmap * 2 * 10**-5)
            
        # make directories
        PathClear= os.path.join(Dir,'Landsaf_Clipped','Shortwave_Clear_Sky')
        if os.path.exists(PathClear) is False:
            os.makedirs(PathClear)
            
        PathNet= os.path.join(Dir,'Landsaf_Clipped','Shortwave_Net')
        if os.path.exists(PathNet) is False:
            os.makedirs(PathNet)
                
        # name Shortwave Clear and Net
        nameFileNet='ShortWave_Net_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif' 
        nameNet= os.path.join(PathNet,nameFileNet)
            
        nameFileClear='ShortWave_Clear_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif'
        nameClear= os.path.join(PathClear,nameFileClear)
            
        # Save net and clear short wave radiation
        DC.Save_as_tiff(nameNet, Short_Wave_Net, geo_out, proj)
        DC.Save_as_tiff(nameClear, Short_Wave_Clear, geo_out, proj)							
    return


def ShortwaveBasin(SourceLANDSAF, Dir, latlim, lonlim, Dates = ['2000-01-01','2013-12-31']):
    """
    This function creates short wave maps based on the SIS and SID 
				
    Keyword arguments:
    SourceLANDSAF -- 'C:/'  path to the LANDSAF source data (The directory includes SIS and SID)
    Dir -- 'C:/' path to the WA map
    latlim -- [ymin, ymax] (values must be between -60 and 60)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    Dates -- ['yyyy-mm-dd','yyyy-mm-dd']
    """

    # Produces shortwave radiation grids for a particular basin or particular bounds    
    Types = ['SIS','SID'] 
    Dates = pd.date_range(Dates[0],Dates[1],freq='D')    
    
    for Type in Types:
        for Date in Dates:
            
            SAFdir = os.path.join(SourceLANDSAF, Type)
            OutPath =  os.path.join(Dir, 'Landsaf_Clipped', Type, 'SAF_' + Type + '_EuropeAfrica_day_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif')
            
            if os.path.exists(SAFdir) is False:
                os.mkdir(SAFdir)
            
            # Convert nc to tiff files
            Transform(SourceLANDSAF, OutPath, Type, Dates = [Date.strftime('%Y-%m-%d'),Date.strftime('%Y-%m-%d')])

            # Get environmental variable
            WA_env_paths = os.environ["WA_PATHS"].split(';')
            GDAL_env_path = WA_env_paths[0]
            GDAL_TRANSLATE_PATH = os.path.join(GDAL_env_path, 'gdal_translate.exe')
            
            # Define output name
            nameOut= os.path.join(Dir,'Landsaf_Clipped',Type,'SAF_' + Type + '_daily_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif')
            
            # Create command for cmd
            fullCmd = ' '.join(['"%s" -projwin %s %s %s %s' % (GDAL_TRANSLATE_PATH, lonlim[0]-0.1, latlim[1]+0.1, lonlim[1]+0.1, latlim[0]-0.1), '-of GTiff', OutPath, nameOut])  # -r {nearest}
           
            # Run command prompt in cmd
            process = subprocess.Popen(fullCmd)
            process.wait() 
            print 'Landsaf ' + Type + ' file for ' + Date.strftime('%Y-%m-%d') + ' created.'
            os.remove(OutPath)
            

def Transform(SourceLANDSAF, OutPath, Type, Dates = ['2000-01-01','2013-12-31']):
    """
    This function creates short wave maps based on the SIS and SID 
    This function converts packed nc files to gtiff file of comparable file size
  		
    Keyword arguments:
    SourceLANDSAF -- 'C:/'  path to the LANDSAF source data (The directory includes SIS and SID)
    Dir -- 'C:/' path to the WA map
    latlim -- [ymin, ymax] (values must be between -60 and 60)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    Dates -- ['yyyy-mm-dd','yyyy-mm-dd']
    """
			
    path = os.path.join(SourceLANDSAF,Type)

    os.chdir(path)
    Dates = pd.date_range(Dates[0],Dates[1],freq='D')

    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")  
    projection = srs.ExportToWkt() 
    driver = gdal.GetDriverByName("GTiff")
    
    
    for Date in Dates:
        if Type == 'SIS': 
            ZipFile = glob.glob('SISdm%s*.nc.gz' % Date.strftime('%Y%m%d'))[0]		
            File = os.path.splitext(ZipFile)[0] 
        elif Type == 'SID':
            ZipFile = glob.glob('*dm%s*.nc.gz' % Date.strftime('%Y%m%d'))[0]		
            File = os.path.splitext(ZipFile)[0]
        
        # find path to the executable 	 
        fullCmd = ''.join("7z x %s -o%s -aoa"  %(os.path.join(path,ZipFile),path))   
        process = subprocess.Popen(fullCmd)
        process.wait()
	
        NC = netCDF4.Dataset(File,'r+',format='NETCDF4')
        Data = NC[Type][0,:,:]
        lon = NC.variables['lon'][:][0]	- 0.025	
        lat = NC.variables['lat'][:][-1] + 0.025					
        geotransform = [lon,0.05,0,lat,0,-0.05]								
								
        dst_ds = driver.Create(OutPath, int(np.size(Data,1)), int(np.size(Data,0)),  1, gdal.GDT_Float32,  ['COMPRESS=DEFLATE'])
        # set the reference info 
        dst_ds.SetProjection(projection)
        dst_ds.SetGeoTransform(geotransform)
        dst_ds.GetRasterBand(1).SetNoDataValue(-1)
        dst_ds.GetRasterBand(1).WriteArray(np.flipud(Data))
        NC.close()        
        del dst_ds, NC, Data
        
        os.remove(File)
