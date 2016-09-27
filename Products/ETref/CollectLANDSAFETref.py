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

# import WA+ modules
from SlopeInfluence_ETref import SlopeInfluence	
from StandardDef_ETref import GetGeoInfo, OpenAsArray, ReprojectRaster
from StandardDef_ETref import CreateGeoTiff
from wa import WA_Paths

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
    DEMmap_str=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m.tif') 
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(DEMmap_str)	

    # Open DEM map 
    gdalDEM=gdal.Open(DEMmap_str)
    demmap = OpenAsArray(DEMmap_str)
    demmap[demmap<0]=0
            
    # make lat and lon arrays
    GeoTransform = gdalDEM.GetGeoTransform()
    dlat = GeoTransform[5] * -1
    dlon = GeoTransform[1]
    lat = GeoTransform[3] - (np.arange(gdalDEM.RasterYSize)+0.5)*dlat
    lon = GeoTransform[0] + (np.arange(gdalDEM.RasterXSize)+0.5)*dlon			
				
				
    for date in Dates:
                    # day of year
        day=date.dayofyear
        Horizontal, Sloping, sinb, sinb_hor, fi, slope, ID  = SlopeInfluence(demmap,lat,lon,day)   
            
                      
        SIDname = os.path.join(SIDdir,'SAF_SID_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif')
        SISname = os.path.join(SISdir,'SAF_SIS_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif')
            
        #PREPARE SID MAPS
        ReprojectRaster(SIDname,DEMmap_str,overwrite=True,output=SIDname, method = 'lanczos')
        SID=gdal.Open(SIDname)
        SIDdata=SID.GetRasterBand(1).ReadAsArray()

        #PREPARE SIS MAPS
        ReprojectRaster(SISname,DEMmap_str,overwrite=True,output=SISname, method = 'lanczos')
        SIS=gdal.Open(SISname)
        SISdata=SIS.GetRasterBand(1).ReadAsArray()
        
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
        nameFileNet='ShortWave_Net_Daily_W-m2_' + date.strftime('%Y-%m-%d')
        nameNet= os.path.join(PathNet,nameFileNet)
            
        nameFileClear='ShortWave_Clear_Daily_W-m2_' + date.strftime('%Y-%m-%d')
        nameClear= os.path.join(PathClear,nameFileClear)
            
        # Save net and clear short wave radiation
        CreateGeoTiff(nameNet,Short_Wave_Net, NDV, xsize, ysize, GeoT, Projection, DataType)
        CreateGeoTiff(nameClear,Short_Wave_Clear, NDV, xsize, ysize, GeoT, Projection, DataType)

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
            
            SAFdir = SourceLANDSAF + os.sep + Type + os.sep
            OutPath =  os.path.join(Dir, 'Landsaf_Clipped', Type, 'SAF_' + Type + '_EuropeAfrica_day_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif')
            
            if os.path.exists(SAFdir) is False:
                os.mkdir(SAFdir)
            
            # Convert nc to tiff files
            Transform(SourceLANDSAF, OutPath, Type, Dates = [Date.strftime('%Y-%m-%d'),Date.strftime('%Y-%m-%d')])

            # find path to the executable
            path = WA_Paths.Paths(Type = 'GDAL')
            nameOut= os.path.join(Dir,'Landsaf_Clipped',Type,'SAF_' + Type + '_daily_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif')
            
			# clip data										
            if path is '':
                fullCmd = ' '.join(['gdal_translate -projwin %s %s %s %s' % (lonlim[0]-0.1, latlim[1]+0.1, lonlim[1]+0.1, latlim[0]-0.1), '-of GTiff', OutPath, nameOut])  # -r {nearest}
            
            else:
                gdal_translate_path = os.path.join(path,'gdal_translate.exe')
                fullCmd = ' '.join(['"%s" -projwin %s %s %s %s' % (gdal_translate_path, lonlim[0]-0.1, latlim[1]+0.1, lonlim[1]+0.1, latlim[0]-0.1), '-of GTiff', OutPath, nameOut])  # -r {nearest}
           
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
			

    path = SourceLANDSAF + os.sep + Type + os.sep

    
    Dates = pd.date_range(Dates[0],Dates[1],freq='D')
    
    geotransform = [-65.025,0.05,0,65.025,0,-0.05]
    size = [2601,2601]
   
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")  
    projection = srs.ExportToWkt() 
    driver = gdal.GetDriverByName("GTiff")
    
    
    for Date in Dates:
        if Type == 'SIS':        
            ZipFile = path + 'SISdm' + Date.strftime('%Y%m%d') + '0000002231000101MA.nc.gz'
            File = path + 'SISdm' + Date.strftime('%Y%m%d') + '0000002231000101MA.nc'
        elif Type == 'SID':
            ZipFile = path + 'DNIdm' + Date.strftime('%Y%m%d') + '0000002231000101MA.nc.gz'
            File = path + 'DNIdm' + Date.strftime('%Y%m%d') + '0000002231000101MA.nc'

        # find path to the executable
        zip_path = WA_Paths.Paths(Type = '7z.exe')
        
        if zip_path is '':		
            os.system("7z x " + ZipFile + " -o" + path + ' -aoa')  
        else: 
            os.system("%s x " %(zip_path) + ZipFile + " -o" + path + ' -aoa')  
        
        NC = netCDF4.Dataset(File,'r+',format='NETCDF4')
        Data = NC[Type][0,:,:]
       
        dst_ds = driver.Create(OutPath, size[1], size[0],  1, gdal.GDT_Float32,  ['COMPRESS=DEFLATE'])
        # set the reference info 
        dst_ds.SetProjection(projection)
        dst_ds.SetGeoTransform(geotransform)
        dst_ds.GetRasterBand(1).SetNoDataValue(-1)
        dst_ds.GetRasterBand(1).WriteArray(np.flipud(Data))
        NC.close()        
        del dst_ds, NC, Data
        
        os.remove(File)
