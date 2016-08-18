# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 16:04:16 2016

@author: Tim Hessels
"""
# This function calculates the reference ET.
# You can use the CFSR dataset for net radiation by running the following:
# import ETrefv3
# ETrefv4.Daily(Startdate='2010-04-01',Enddate='2010-04-03',latlim = [9,10],lonlim = [9,10],Dir =r'C:\Users\tih\Documents\Water_Accounting\Tools\NDVI')

# You can use the Landsaf dataset for net radiation by running the following (only Europe and Africa):
# import ETrefv4
# ETrefv4.Daily(Startdate='2010-04-01',Enddate='2010-04-03',latlim = [35,37],lonlim = [27,30],Dir =r'C:\Users\tih\Documents\Water_Accounting\Tools\NDVI',Landsaf=0, Source=r'D:\FTP\Data_Satellite\SAF')

# IF YOU WANT TO USE LANDSAF DATA!!!!
# The Source variable is the path to the landsaf data. This path has to directories namely the SID and SIS.
# the SIS contains the surface incoming radiation
# the SID folder contains the direct incomming sohortwave.
# Both files can be downloaded from CMSAF.eu
# An example file is: DNIdm200002020000002231000101MA.nc.gz for a SID file
# and: SISdm201312300000002231000101MA.nc.gz for a SIS file

# Water Accounting modules
import CFSR2   # was eerst CFSR Converter is aangepast van wgrib2 naar gdal_translate
import CFSRv2
import GLDAS
import DEM
import Path_WA

# Basic modules
import numpy as np
import os
import gdal
import pandas as pd
import osr
import calendar
import netCDF4
import subprocess
import scipy.interpolate

def Monthly(Startdate,Enddate,latlim,lonlim,Dir,Landsaf='',Source=''):
    
    Dates = pd.date_range(Startdate,Enddate,freq = 'MS') 
    
    for Date in Dates:
       Y=Date.year
       M=Date.month
       Mday=calendar.monthrange(Y,M)[1]
       Days=pd.date_range(Date,Date+pd.Timedelta(days=Mday),freq='D')
       StartTime=Date.strftime('%Y')+'-'+Date.strftime('%m')+ '-01' 
       EndTime=Date.strftime('%Y')+'-'+Date.strftime('%m')+'-'+str(Mday)
                  
       # Get ETref on daily basis
       Daily(Startdate=StartTime,Enddate=EndTime,latlim=latlim, lonlim=lonlim,Dir=Dir,Landsaf=Landsaf)

       # Load DEM 
       nameDEM='DEM_HydroShed_m.tif'
       DEMmap=os.path.join(Dir,'HydroSHED','DEM',nameDEM )
       
       # Get some geo-data to save results
       NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(DEMmap)
       driver = gdal.GetDriverByName('GTiff')       
       
       dataMonth=np.zeros([ysize,xsize])
       
       for Day in Days[:-1]: 
           output_folder_day=os.path.join(Dir,'ETref','Daily')
           DirDay=output_folder_day + '\ETref_mm-day_' + Date.strftime('%Y.%m.%d') + '.tif'

           dataDay=gdal.Open(DirDay)
           Dval=dataDay.GetRasterBand(1).ReadAsArray().astype(np.float32)    
           Dval[Dval<0]=0
           dataMonth=dataMonth+Dval
           dataDay=None
        
       # make geotiff file 
       output_folder=os.path.join(Dir,'ETref','Monthly')
       if os.path.exists(output_folder)==False:       
           os.makedirs(output_folder)
       DirMonth=output_folder + '\ETref_mm-month_'+Date.strftime('%Y.%m.%d')
       
       CreateGeoTiff(DirMonth,dataMonth, driver, NDV, xsize, ysize, GeoT, Projection, DataType)

     

def Daily(Startdate,Enddate,latlim,lonlim,Dir,Landsaf='',Source=''):
    # Make an array of the days of which the ET is taken
    Dates = pd.date_range(Startdate,Enddate,freq = 'D') 
    
    # download DEM map
    DEM.HydroSHED(latlim=latlim,lonlim=lonlim,Dir=Dir,Resample=0)
    
    # Load DEM 
    nameDEM='DEM_HydroShed_m.tif'
    DEMmap=os.path.join(Dir,'HydroSHED','DEM',nameDEM )
    
    
    # Get some geo-data to save results
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(DEMmap)
    driver = gdal.GetDriverByName('GTiff')
    raster_shape = OpenAsArray(DEMmap).shape    
    
    if Landsaf==1:
        
       # make directories
       SISdir = os.path.join(Dir,'Landsaf_Clipped','SIS')
       if os.path.exists(SISdir) is False:
            os.makedirs(SISdir)
        
       SIDdir= os.path.join(Dir,'Landsaf_Clipped','SID')
       if os.path.exists(SIDdir) is False:
            os.makedirs(SIDdir)
       
       ShortwaveBasin(Source, Dir, latlim, lonlim, Dates=[Startdate,Enddate])
      
       for date in Dates:
            
            # Open DEM map 
            gdalDEM=gdal.Open(DEMmap)
            demmap = OpenAsArray(DEMmap)
            demmap[demmap<0]=0
            
            # make lat and lon arrays
            GeoTransform = gdalDEM.GetGeoTransform()
            dlat = GeoTransform[5] * -1
            dlon = GeoTransform[1]
            lat = GeoTransform[3] - (np.arange(gdalDEM.RasterYSize)+0.5)*dlat
            lon = GeoTransform[0] + (np.arange(gdalDEM.RasterXSize)+0.5)*dlon
            
            # day of year
            day=date.dayofyear
            Horizontal, Sloping, sinb, sinb_hor, fi, slope, ID  = SlopeInfluence(demmap,lat,lon,day)   
            
                      
            SIDname = Dir + '\\Landsaf_Clipped\\SID\\' + 'SAF_SID_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif'
            SISname = Dir + '\\Landsaf_Clipped\\SIS\\' + 'SAF_SIS_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif'
            
            #PREPARE SID MAPS
            ReprojectRaster(SIDname,DEMmap,overwrite=True,output=SIDname, method = 'lanczos')
            SIDname = Dir + '\\Landsaf_Clipped\\SID\\' + 'SAF_SID_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif'
            SID=gdal.Open(SIDname)
            SIDdata=SID.GetRasterBand(1).ReadAsArray()

            #PREPARE SIS MAPS
            ReprojectRaster(SISname,DEMmap,overwrite=True,output=SISname, method = 'lanczos')
            SISname = Dir + '\\Landsaf_Clipped\\SIS\\' + 'SAF_SIS_Daily_W-m2_' + date.strftime('%Y-%m-%d') + '.tif'
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
            CreateGeoTiff(nameNet,Short_Wave_Net, driver, NDV, xsize, ysize, GeoT, Projection, DataType)
            CreateGeoTiff(nameClear,Short_Wave_Clear, driver, NDV, xsize, ysize, GeoT, Projection, DataType)
            
    else:
        if Dates[0]<pd.Timestamp(pd.datetime(2011, 4, 1)) and Dates[-1]<pd.Timestamp(pd.datetime(2011, 4, 1)):
            # download CFSR data
            CFSR2.ULWR_Daily(Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
            CFSR2.DLWR_Daily(Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
            CFSR2.DSWR_Daily(Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
        
        if Dates[0]<pd.Timestamp(pd.datetime(2011, 4, 1)) and Dates[-1]>=pd.Timestamp(pd.datetime(2011, 4, 1)):
            
            EnddateCFSR=pd.Timestamp(pd.datetime(2011, 3, 1))
            StartdateCFSRv2=pd.Timestamp(pd.datetime(2011, 4, 1))
            
            # download CFSR data
            CFSR2.ULWR_Daily(Startdate=Startdate,Enddate=EnddateCFSR,latlim=latlim,lonlim=lonlim,Dir=Dir)
            CFSR2.DLWR_Daily(Startdate=Startdate,Enddate=EnddateCFSR,latlim=latlim,lonlim=lonlim,Dir=Dir)
            CFSR2.DSWR_Daily(Startdate=Startdate,Enddate=EnddateCFSR,latlim=latlim,lonlim=lonlim,Dir=Dir)
       
            # download CFSR data
            CFSRv2.ULWR_Daily(Startdate=StartdateCFSRv2,Enddate=EnddateCFSR,latlim=latlim,lonlim=lonlim,Dir=Dir)
            CFSRv2.DLWR_Daily(Startdate=StartdateCFSRv2,Enddate=EnddateCFSR,latlim=latlim,lonlim=lonlim,Dir=Dir)
            CFSRv2.DSWR_Daily(Startdate=StartdateCFSRv2,Enddate=EnddateCFSR,latlim=latlim,lonlim=lonlim,Dir=Dir)
     
        if Dates[0] >= pd.Timestamp(pd.datetime(2011, 4, 1)): 
              
            # download CFSR data
            CFSRv2.ULWR_Daily(Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
            CFSRv2.DLWR_Daily(Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
            CFSRv2.DSWR_Daily(Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
             
        
    # download GLDAS data
    GLDAS.GLDAS_daily(Var = 'tair',SumMean = 0, Min = 1, Max = 1, Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
    GLDAS.GLDAS_daily(Var = 'psurf',SumMean = 1, Min = 0, Max = 0, Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
    GLDAS.GLDAS_daily(Var = 'wind',SumMean = 1, Min = 0, Max = 0, Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
    GLDAS.GLDAS_daily(Var = 'qair',SumMean = 1, Min = 0, Max = 0, Startdate=Startdate,Enddate=Enddate,latlim=latlim,lonlim=lonlim,Dir=Dir)
    
    for Date in Dates:
    
        # Create array to store results
        ETref = np.zeros(raster_shape)
        
        # Set the paths
        nameTmin='Tair-min_GLDAS-NOAH_C_daily_' + Date.strftime('%Y.%m.%d') + ".tif"
        tmin=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','tair','min',nameTmin )
        
        nameTmax='Tair-max_GLDAS-NOAH_C_daily_' + Date.strftime('%Y.%m.%d') + ".tif"
        tmax=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','tair','max',nameTmax )
        
        nameHumid='Hum_GLDAS-NOAH_kg-kg_daily_'+ Date.strftime('%Y.%m.%d') + ".tif"
        humid=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','qair','mean',nameHumid )
        
        namePress='P_GLDAS-NOAH_kpa_daily_'+ Date.strftime('%Y.%m.%d') + ".tif"
        press=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','psurf','mean',namePress )
        
        nameWind='W_GLDAS-NOAH_m-s-1_daily_'+ Date.strftime('%Y.%m.%d') + ".tif"
        wind=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','wind','mean',nameWind )
        
        if Landsaf==1:
                
                nameShortClearname = 'ShortWave_Clear_Daily_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif'
                input2=os.path.join(Dir,'Landsaf_Clipped','Shortwave_Clear_Sky',nameShortClearname)
                
                nameShortNetname = 'ShortWave_Net_Daily_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif'
                input1=os.path.join(Dir,'Landsaf_Clipped','Shortwave_Net',nameShortNetname)
               
                input3=2
            
        else:
            if Date<pd.Timestamp(pd.datetime(2011, 4, 1)):
           
                nameDownLong='DLWR_CFSR_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
                input2=os.path.join(Dir,'Radiation','CFSR',nameDownLong)
                    
                nameDownShort='DSWR_CFSR_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
                input1=os.path.join(Dir,'Radiation','CFSR',nameDownShort)
                
                nameUpLong='ULWR_CFSR_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
                input3=os.path.join(Dir,'Radiation','CFSR',nameUpLong)
                
            else:         
                nameDownLong='DLWR_CFSRv2_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
                input2=os.path.join(Dir,'Radiation','CFSRv2',nameDownLong)
                    
                nameDownShort='DSWR_CFSRv2_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
                input1=os.path.join(Dir,'Radiation','CFSRv2',nameDownShort)
                
                nameUpLong='ULWR_CFSRv2_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
                input3=os.path.join(Dir,'Radiation','CFSRv2',nameUpLong)   
        
        DOY=Date.dayofyear
        
        # Run ETref
        ETref = calc_ETref(tmin, tmax, humid, press, wind, input1, input2, input3, DEMmap, DOY)
        
        # Make directory for the MODIS ET data
        output_folder=os.path.join(Dir,'ETref','Daily')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)    
        
        NameETref='ETref_mm-day_'+Date.strftime('%Y.%m.%d')    
        NameEnd=os.path.join(output_folder,NameETref)
        
        
        CreateGeoTiff(NameEnd,ETref, driver, NDV, xsize, ysize, GeoT, Projection, DataType)

############### Calculate Daily Reference ET #################################

"""
Created on Fri Mar 04 13:08:42 2016 by Bert Coerver

@author: Bert Coerver and Tim Hessels
contact: b.coerver@unesco-ihe.org
"""

def calc_ETref(tmin_str, tmax_str, humid_str, press_str, wind_str, down_short_str, down_long_str, up_long_str, DEMmap, DOY):
# Calculate reference ET according to FAO standards
# see: http://www.fao.org/docrep/x0490e/x0490e08.htm#TopOfPage
#
# Inputs are (paths to) geotiffs, except DOY which is an integer referring to the Day of the Year:
# tmin, Minimum temperature,[degrees Celcius], e.g. from GLDAS
# tmax, maximum temperature,[degrees Celcius], e.g. from GLDAS
# humid,surface specific humidity [kg/kg], e.g. from GLDAS
# press,surface surface pressure [kPa], e.g. from GLDAS
# wind,windspeed [m/s], e.g. from GLDAS
# albedo, albedo [%], e.g. from CSFR
# down_short,downward longwave radiation [W*m-2], e.g. from CSFR
# down_long,downward shortwave radiation [W*m-2], e.g. from CSFR
# up_short,upward longwave radiation [W*m-2], e.g. from CSFR
# up_long,upward shortwave radiation [W*m-2], e.g. from CSFR
# DEM [m]

     
    # gap fill
    tmin_str_GF = gap_filling(tmin_str,-9999)
    tmax_str_GF = gap_filling(tmax_str,-9999)
    humid_str_GF = gap_filling(humid_str,-9999)
    press_str_GF = gap_filling(press_str,-9999)
    wind_str_GF = gap_filling(wind_str,-9999)
    down_short_str_GF = gap_filling(down_short_str,np.nan)
    down_long_str_GF = gap_filling(down_long_str,np.nan)
    up_long_str_GF = gap_filling(up_long_str,np.nan)
    
    
    #dictionary containing all tthe paths to the input-maps
    inputs = dict({'tmin':tmin_str_GF,'tmax':tmax_str_GF,'humid':humid_str_GF,'press':press_str_GF,'wind':wind_str_GF,'down_short':down_short_str_GF,'down_long':down_long_str_GF,'up_long':up_long_str_GF})
   
    
    #dictionary containing numpy arrays of al initial and intermediate variables    
    input_array = dict({'tmin':None,'tmax':None,'humid':None,'press':None,'wind':None,'albedo':None,'down_short':None,'down_long':None,'up_short':None,'up_long':None,'net_radiation':None,'ea':None,'es':None,'delta':None})
    
    #APPLY LAPSE RATE CORRECTION ON TEMPERATURE
    tmin = lapse_rate(inputs['tmin'], DEMmap)
    tmax = lapse_rate(inputs['tmax'], DEMmap)
    

    #PROCESS PRESSURE MAPS 
    press =adjust_P(inputs['press'], DEMmap)
    
    #PREPARE HUMIDITY MAPS
    dest = reproject_dataset(inputs['humid'], DEMmap,method = 'bilinear')
    band=dest.GetRasterBand(1)
    humid=band.ReadAsArray()
    dest = None
    
     
    #CORRECT WIND MAPS
    dest = reproject_dataset(inputs['wind'], DEMmap,method = 'bilinear')
    band=dest.GetRasterBand(1)
    wind=band.ReadAsArray()*0.75
    dest = None
   
    #PROCESS GLDAS DATA
    input_array['ea'], input_array['es'], input_array['delta'] = process_GLDAS(tmax,tmin,humid,press)
    
    ea=input_array['ea']
    es=input_array['es']
    delta=input_array['delta']
    
    if up_long_str == 2:
        
        #rename variables which are suitable for this option
        Short_Net = down_short_str
        Short_Clear = down_long_str
        
        #Open Arrays
        Short_Net_gdal=gdal.Open(Short_Net)
        Short_Net_data = Short_Net_gdal.GetRasterBand(1).ReadAsArray()
        
        Short_Clear_gdal=gdal.Open(Short_Clear)
        Short_Clear_data = Short_Clear_gdal.GetRasterBand(1).ReadAsArray()
        
        
        # Calculate Long wave Net radiation
        Rnl = 4.903e-9 * (((tmin + 273.16)**4+(tmax + 273.16)**4)/2)*(0.34 - 0.14 * np.sqrt(ea)) * (1.35 * Short_Net_data/Short_Clear_data -0.35)
        
        # Calulate Net Radiation and converted to MJ*d-1*m-2
        net_radiation = (Short_Net_data * 0.77 + Rnl)*86400/10**6
        
       
    else:
        #OPEN DOWNWARD SHORTWAVE RADIATION
        dest = reproject_dataset(inputs['down_short'], DEMmap,method = 'bilinear')
        band=dest.GetRasterBand(1)
        down_short=band.ReadAsArray()
        dest = None
        down_short, tau, bias = slope_correct(down_short,press,ea,DEMmap,DOY)
        
           
        #OPEN OTHER RADS
        up_short = down_short*0.23
        
        
        dest = reproject_dataset(inputs['down_long'], DEMmap,method = 'bilinear')
        band=dest.GetRasterBand(1)
        down_long=band.ReadAsArray()
        dest = None
                
        dest = reproject_dataset(inputs['up_long'], DEMmap,method = 'bilinear')
        band=dest.GetRasterBand(1)
        up_long=band.ReadAsArray()
        dest = None
               
        #OPEN NET RADIATION AND CONVERT W*m-2 TO MJ*d-1*m-2
        net_radiation = ((down_short-up_short) + (down_long-up_long))*86400/10**6
    
        
    #CALCULATE ETref
    ETref = (0.408 * delta * net_radiation + 0.665*10**-3 * 
        press * (900/((tmax+tmin)/2 + 273)) *
        wind * (es - ea)) / (delta + 0.665*10**-3 * 
        press * (1 + 0.34 * wind))
        
    ETref[ETref<0]=0
    
    #return a reference ET map (numpy array), a dictionary containing all intermediate information and a bias of the slope correction on down_short
    return ETref

def process_GLDAS(Tmax, Tmin, humidity, surface_pressure):
    
    T_mean = (Tmax + Tmin) / 2   
    
    delta = 4098 * (0.6108  * np.exp(17.27 * T_mean / (T_mean + 237.3))) / (T_mean + 237.3)**2
    
    e0_max = 0.6108 * np.exp(17.27 * Tmax / (Tmax + 237.3))
    e0_min = 0.6108 * np.exp(17.27 * Tmin / (Tmin + 237.3))
    es = (e0_max + e0_min) / 2
    
    RH_max = np.minimum((1/0.622) * humidity * surface_pressure / e0_min, 1)*100
    RH_min = np.minimum((1/0.622) * humidity * surface_pressure / e0_max, 1)*100
    
    ea = (e0_min * RH_max/100 + e0_max * RH_min/100) / 2
    
    return ea, es, delta

def lapse_rate(temperature_map, DEMmap):    
    
    # calculate average altitudes corresponding to T resolution
    DEM_avg = ReprojectRaster(DEMmap, temperature_map, overwrite=False, output='DEM_avg.tif')
    
    # determine lapse-rate [degress Celcius per meter]
    lapse_rate_number = 0.0065
    
    # open maps as numpy arrays
    dest = reproject_dataset(DEM_avg, DEMmap,method = 'bilinear')
    band=dest.GetRasterBand(1)
    dem_avg=band.ReadAsArray()
    dem_avg[dem_avg<0]=0
    dest = None

    # Open the temperature dataset
    dest = reproject_dataset(temperature_map, DEMmap, method = 'bilinear')
    band=dest.GetRasterBand(1)
    T=band.ReadAsArray()
    dest = None
    
    # Open Demmap
    demmap = OpenAsArray(DEMmap)
    dem_avg[demmap<=0]=0
    demmap[demmap==-32768]=np.nan
    
    # calculate first part
    T = T + ((dem_avg-demmap) * lapse_rate_number)
    
    return T
    
def adjust_P(pressure_map, DEMmap):
    
    # calculate average latitudes
    DEM_avg = ReprojectRaster(DEMmap, pressure_map, overwrite=False, output='DEM_avg.tif')
    
    # open maps as numpy arrays
    dest = reproject_dataset(DEM_avg, DEMmap,method = 'bilinear')
    band=dest.GetRasterBand(1)
    dem_avg=band.ReadAsArray()
    dest = None
    
    # open maps as numpy arrays
    dest = reproject_dataset(pressure_map, DEMmap, method = 'bilinear')
    band=dest.GetRasterBand(1)
    P=band.ReadAsArray()
    dest = None
    
  
    demmap = OpenAsArray(DEMmap)
    dem_avg[demmap<=0]=0
    demmap[demmap==-32768]=np.nan
    
    # calculate second part
    P = P + (101.3*((293-0.0065*(demmap-dem_avg))/293)**5.26 - 101.3)

    os.remove('DEM_avg.tif')

    return P

def slope_correct(down_short_hor, pressure, ea, demmap, DOY):

# Slope correction based on Allen et al. (2006)
# 'Analytical integrated functions for daily solar radiation on slopen'    
    
    #####
    ## Get Geo Info
    #####
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(demmap)
    
    minx = GeoT[0]
    miny = GeoT[3] + xsize*GeoT[4] + ysize*GeoT[5] 
    
    x = np.flipud(np.arange(xsize)*GeoT[1] + minx + GeoT[1]/2)
    y = np.flipud(np.arange(ysize)*-GeoT[5] + miny + -GeoT[5]/2)
    
    ####
    ## Calculate Extraterrestrial Solar Radiation [W m-2]
    ####
    DEMmap = OpenAsArray(demmap)   
    DEMmap[DEMmap<0]=0
    
    Ra_hor, Ra_slp, sinb, sinb_hor, fi, slope, ID = SlopeInfluence(DEMmap,y,x,DOY)
    
    ####
    ## Calculate atmospheric transmissivity
    ####
    
    Rs_hor = down_short_hor
    
    # EQ 39
    tau = Rs_hor/Ra_hor
    
    #EQ 41
    KB_hor = np.zeros(tau.shape) * np.nan
    
    indice = np.where(tau.flat >= 0.42)
    KB_hor.flat[indice] = 1.56*tau.flat[indice] -0.55
    
    indice = np.logical_and(tau.flat > 0.175, tau.flat < 0.42)
    KB_hor.flat[indice] = 0.022 - 0.280*tau.flat[indice] + 0.828*tau.flat[indice]**2 + 0.765*tau.flat[indice]**3
    
    indice = np.where(tau.flat <= 0.175)
    KB_hor.flat[indice] = 0.016*tau.flat[indice]
    
    # EQ 42
    KD_hor = tau - KB_hor
    
    Kt=0.7
    
    #EQ 18
    W = 0.14*ea*pressure + 2.1
    
    KB0 = 0.98*np.exp((-0.00146*pressure/Kt/sinb)-0.075*(W/sinb)**0.4)
    KB0_hor = 0.98*np.exp((-0.00146*pressure/Kt/sinb_hor)-0.075*(W/sinb_hor)**0.4)
    
    #EQ 34
    fB = KB0/KB0_hor * Ra_slp/Ra_hor
    fia = (1-KB_hor) * (1 + (KB_hor/(KB_hor+KD_hor))**0.5 * np.sin(slope/2)**3)*fi + fB*KB_hor
    
    Rs = Rs_hor*(fB*(KB_hor/tau) + fia*(KD_hor/tau) + 0.23*(1-fi))
    
    Rs[np.isnan(Rs)] = Rs_hor[np.isnan(Rs)]
    
    Rs_equiv = Rs / np.cos(slope)

    print('bias: '+str(np.nansum(Rs_hor)/np.nansum(Rs_equiv)))

    bias = np.nansum(Rs_hor)/np.nansum(Rs_equiv)

    return Rs_equiv, tau, bias
    
############### Function Slope Correction ####################################
"""
Created on Fri Jun 12 14:46:00 2015 by Gert Mulder
Adjustd on Fri Mar 16 by Bert Coerver

@author: Gert Mulder & Bert Coerver
"""
def SlopeInfluence(DEMmap,latitude,longitude,day):
    # This model calculates the amount of sunlight on a particular day for a sloping
    # terrain. The needed inputs are:
    # DEM > a DEM map
    # lat/lon > either as 2 vectors or 2 matrices
    # day > the day of the year
    # Because we do not know the height of neigbouring cells at the border of the
    # grid, these values can deviate from real values.
    # Be carefull with high latitudes (>66, polar circle)! Calculations for regions without sunset
    # (all day sun) are not calculated correctly.
    
    # Solar constant
    G = 1367.0
    
    # If lat/lon are not a matrix but a vector create matrixes
    if not latitude.shape == longitude.shape:
        latitude = np.tile(latitude.reshape(len(latitude),1),[1,len(longitude)])
        longitude = np.tile(longitude.reshape(1,len(longitude)),[len(latitude),1])
    elif len(latitude.shape) == 1 and len(longitude.shape) == 1:
        latitude = np.tile(latitude.reshape(len(latitude),1),[1,len(longitude)])
        longitude = np.tile(longitude.reshape(1,len(longitude)),[len(longitude),1])
    
    # Convert lat/lon to radians
    lat = np.radians(latitude)
    lon = np.radians(longitude)
           
    # Calculate dlat/dlon assuming a regular grid
    latdiff = np.diff(lat,axis=0) 
    dlat = np.vstack((latdiff[0,:][None,:],(latdiff[1:,:] + latdiff[0:-1,:])/2,latdiff[-1,:][None,:]))
    londiff = np.diff(lon,axis=1) 
    dlon = np.hstack((londiff[:,0][:,None],(londiff[:,1:] + londiff[:,0:-1])/2,londiff[:,-1][:,None]))
    
    # And convert to meters
    lons = np.cos(lat) * np.cos(lat) * np.sin(dlon/2) ** 2
    lats = np.sin(dlat / 2) ** 2
    dlon = 2 * np.arcsin(np.sqrt(lons)) * 6371000
    dlat = 2 * np.arcsin(np.sqrt(lats)) * 6371000
    del lats, lons
    
    # Calculate dy_lat and dy_lon, height differences in latitude and longitude directions.
    latdiff = np.diff(DEMmap,axis=0) 
    dy_lat = np.vstack((latdiff[0,:][None,:],(latdiff[1:,:] + latdiff[0:-1,:])/2,latdiff[-1,:][None,:]))
    londiff = -np.diff(DEMmap,axis=1) 
    dy_lon = np.hstack((londiff[:,0][:,None],(londiff[:,1:] + londiff[:,0:-1])/2,londiff[:,-1][:,None]))    
    
    # Calculate slope
    slope = np.arctan((np.abs(dy_lat) + np.abs(dy_lon)) / np.sqrt(dlon**2+dlat**2))
    
    # declination of earth
    delta = np.arcsin(np.sin(23.45/360*2*np.pi)*np.sin((360.0/365.0)*(day-81)/360*2*np.pi))
    # EQ 2
    D2 = 1 / (1 + 0.033* np.cos(day/365*2*np.pi))
    
    constant =  G / D2 / (2*np.pi) 
    
    # Slope direction
    with np.errstate(divide='ignore'):
        slopedir = np.arctan(dy_lon/dy_lat) 
        
        # Exception if divided by zero    
        slopedir[np.logical_and(dy_lat == 0 , dy_lon <= 0)] = np.pi / 2
        slopedir[np.logical_and(dy_lat == 0, dy_lon > 0)] = -np.pi / 2
        
        # Correction ip dy_lat > 0
        slopedir[np.logical_and(dy_lat > 0, dy_lon < 0)] = np.pi + slopedir[np.logical_and(dy_lat > 0, dy_lon < 0)]
        slopedir[np.logical_and(dy_lat > 0, dy_lon >= 0)] = -np.pi + slopedir[np.logical_and(dy_lat > 0, dy_lon >= 0)]
    
    # Now calculate the expected clear sky radiance day by day for:
    # - A horizontal surface
    # - A mountaneous surface (slopes)
    
    # Define grids
    Horizontal = np.zeros(slope.shape) * np.nan
    Sloping = np.zeros(slope.shape) * np.nan
    
    sinb = np.zeros(slope.shape) *np.nan
    sinb_hor = np.zeros(slope.shape) *np.nan
    
    f1 = np.zeros(slope.shape) *np.nan
    f2 = np.zeros(slope.shape) *np.nan
    f3 = np.zeros(slope.shape) *np.nan
    f4 = np.zeros(slope.shape) *np.nan
    f5 = np.zeros(slope.shape) *np.nan
    
    #######
    ## Horizontal (EQ 35)
    #######
    
    # Check where there is no sunrise and assign values
    Horizontal[np.abs(delta-lat) > np.pi/2] = 0 
    
    # Check whether there are areas without sunset
    ID = np.where(np.ravel(np.abs(delta+lat)) > np.pi/2)    
    sunrise = -np.pi
    sunset = np.pi
    Horizontal.flat[ID] = IntegrateHorizontal((G/(np.pi*D2)),sunrise,sunset,delta,lat.flat[ID])    

    # Calculate sunset and sunrise for all other cells    
    ID = np.where(np.isnan(np.ravel(Horizontal)))    
    bound = BoundsHorizontal(delta,lat.flat[ID])     
    Horizontal.flat[ID] = IntegrateHorizontal((G/(np.pi*D2)),-bound,bound,delta,lat.flat[ID])
    
    ws = np.arccos(-np.tan(delta)*np.tan(lat))
    a,b,c,g,h = Table2(delta,lat,slope,slopedir) 
    sinb_hor = (2*g**2*ws + 4*g*h*np.sin(ws) + h**2*(ws+0.5*np.sin(2*ws))) / (2*(g*ws+h*np.sin(ws)))    
    
    #######
    ## Sloping (EQ )
    #######
    A1,A2,B1,B2 = TwoPeriodSunnyTimes(constant,delta,slope,slopedir,lat)    

    # Check whether we have one or two periods of sunlight.
    TwoPeriod = TwoPeriods(delta,slope,lat) 
    
    ID = np.where(np.ravel(TwoPeriod == True))
    Sloping.flat[ID] = TwoPeriodSun(constant,delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    f1.flat[ID],f2.flat[ID],f3.flat[ID],f4.flat[ID],f5.flat[ID] = Table1b(A1.flat[ID],A2.flat[ID],B1.flat[ID],B2.flat[ID]) 
    
    ID = np.where(np.ravel(TwoPeriod == False))
    Sloping.flat[ID] = OnePeriodSun(constant,delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    f1.flat[ID],f2.flat[ID],f3.flat[ID],f4.flat[ID],f5.flat[ID] = Table1a(A1.flat[ID],A2.flat[ID])  

    sinb = (b*g-a*h*f1 - c*g*f2 + (0.5*b*h - a*g)*f3 + 0.25*b*h*f4 + 0.5*c*h*f5) / b*f1 - c*f2 - a*f3
    #sinb[sinb[~np.isnan(sinb)] < 0.0] = 0.0
    
    fi = 0.75 + 0.25*np.cos(slope) - (0.5*slope/np.pi)

    return(Horizontal,Sloping, sinb, sinb_hor, fi, slope, np.where(np.ravel(TwoPeriod == True)))

def Table1a(sunrise,sunset):
    f1 = np.sin(sunset) - np.sin(sunrise)
    f2 = np.cos(sunset) - np.cos(sunrise)
    f3 = sunset - sunrise
    f4 = np.sin(2*sunset) - np.sin(2*sunrise)
    f5 = np.sin(sunset)**2 - np.sin(sunrise)**2
    return f1, f2, f3, f4, f5
    
def Table1b(w1,w2,w1b,w2b):
    f1 = np.sin(w2b) - np.sin(w1) + np.sin(w2) - np.sin(w1b)
    f2 = np.cos(w2b) - np.cos(w1) + np.cos(w2) - np.cos(w1b)
    f3 = w2b - w1 + w2 - w1b
    f4 = np.sin(2*w2b) - np.sin(2*w1) + np.sin(2*w2) - np.sin(2*w1b)
    f5 = np.sin(w2b)**2 - np.sin(w1)**2 + np.sin(w2)**2 - np.sin(w1b)**2
    return f1, f2, f3, f4, f5

def Table2(delta,lat,slope,slopedir):
    a = np.sin(delta)*np.cos(lat)*np.sin(slope)*np.cos(slopedir) - np.sin(delta)*np.sin(lat)*np.cos(slope)
    b = np.cos(delta)*np.cos(lat)*np.cos(slope) + np.cos(delta)*np.sin(lat)*np.sin(slope)*np.cos(slopedir)
    c = np.cos(delta)*np.sin(slopedir)*np.sin(slope)
    g = np.sin(delta)*np.sin(lat)
    h = np.cos(delta)*np.cos(lat)
    
    return a,b,c,g,h

def SunHours(delta,slope,slopedir,lat):
    # Define sun hours in case of one sunlight period
    
    a,b,c = Constants(delta,slope,slopedir,lat)
    riseSlope, setSlope = BoundsSlope(a,b,c)  
    bound = BoundsHorizontal(delta,lat)  

    Calculated = np.zeros(slope.shape, dtype = bool)    
    RiseFinal = np.zeros(slope.shape)    
    SetFinal = np.zeros(slope.shape)
    
    # First check sunrise is not nan
    # This means that their is either no sunrise (whole day night) or no sunset (whole day light)
    # For whole day light, use the horizontal sunrise and whole day night a zero..
    Angle4 = AngleSlope(a,b,c,-bound)    
    RiseFinal[np.logical_and(np.isnan(riseSlope),Angle4 >= 0)] = -bound[np.logical_and(np.isnan(riseSlope),Angle4 >= 0)]
    Calculated[np.isnan(riseSlope)] = True 
    
    # Step 1 > 4    
    Angle1 = AngleSlope(a,b,c,riseSlope)
    Angle2 = AngleSlope(a,b,c,-bound)    
    
    ID = np.ravel_multi_index(np.where(np.logical_and(np.logical_and(Angle2 < Angle1+0.001 ,Angle1 < 0.001),Calculated == False) == True),a.shape)
    RiseFinal.flat[ID] = riseSlope.flat[ID]
    Calculated.flat[ID] = True
    # step 5 > 7
    Angle3 = AngleSlope(a,b,c,-np.pi - riseSlope)
    
    ID = np.ravel_multi_index(np.where(np.logical_and(np.logical_and(-bound<(-np.pi-riseSlope),Angle3 <= 0.001),Calculated == False) == True),a.shape) 
    RiseFinal.flat[ID] = -np.pi -riseSlope.flat[ID]
    Calculated.flat[ID] = True
    
    # For all other values we use the horizontal sunset if it is positive, otherwise keep a zero   
    RiseFinal[Calculated == False] = -bound[Calculated == False] 
    
    # Then check sunset is not nan or < 0 
    Calculated = np.zeros(slope.shape, dtype = bool)     
    
    Angle4 = AngleSlope(a,b,c,bound)    
    SetFinal[np.logical_and(np.isnan(setSlope),Angle4 >= 0)] = bound[np.logical_and(np.isnan(setSlope),Angle4 >= 0)]
    Calculated[np.isnan(setSlope)] = True     
    
    # Step 1 > 4    
    Angle1 = AngleSlope(a,b,c,setSlope)
    Angle2 = AngleSlope(a,b,c,bound)    
    
    ID = np.ravel_multi_index(np.where(np.logical_and(np.logical_and(Angle2 < Angle1+0.001,Angle1 < 0.001),Calculated == False) == True),a.shape)
    SetFinal.flat[ID] = setSlope.flat[ID]
    Calculated.flat[ID] = True
    # step 5 > 7
    Angle3 = AngleSlope(a,b,c,np.pi - setSlope)
    
    ID = np.ravel_multi_index(np.where(np.logical_and(np.logical_and(bound>(np.pi-setSlope),Angle3 <= 0.001),Calculated == False) == True),a.shape) 
    SetFinal.flat[ID] = np.pi - setSlope.flat[ID]
    Calculated.flat[ID] = True
    
    # For all other values we use the horizontal sunset if it is positive, otherwise keep a zero   
    SetFinal[Calculated == False] = bound[Calculated == False]   
    
    #    Angle4 = AngleSlope(a,b,c,bound)    
    #    SetFinal[np.logical_and(Calculated == False,Angle4 >= 0)] = bound[np.logical_and(Calculated == False,Angle4 >= 0)]

    # If Sunrise is after Sunset there is no sunlight during the day
    SetFinal[SetFinal <= RiseFinal] = 0
    RiseFinal[SetFinal <= RiseFinal] = 0
    
    return(RiseFinal,SetFinal)

def OnePeriodSun(constant,delta,slope,slopedir,lat):
    # Initialize function 
    sunrise,sunset = SunHours(delta,slope,slopedir,lat) 
    
    # Finally calculate resulting values
    Vals = IntegrateSlope(constant,sunrise,sunset,delta,slope,slopedir,lat)    
    
    return(Vals)

def TwoPeriodSunnyTimes(constant,delta,slope,slopedir,lat):
    # First derive A1 and A2 from the normal procedure    
    A1,A2 = SunHours(delta,slope,slopedir,lat)
    
    # Then calculate the other two functions.
    # Initialize function    
    
    a,b,c = Constants(delta,slope,slopedir,lat)
    riseSlope, setSlope = BoundsSlope(a,b,c)  
    
    B1 = np.maximum(riseSlope,setSlope)
    B2 = np.minimum(riseSlope,setSlope)
    
    Angle_B1 = AngleSlope(a,b,c,B1)
    Angle_B2 = AngleSlope(a,b,c,B2) 
    
    B1[abs(Angle_B1) > 0.001] = np.pi - B1[abs(Angle_B1) > 0.001]
    B2[abs(Angle_B2) > 0.001] = -np.pi - B2[abs(Angle_B2) > 0.001]    
    
    # Check if two periods really exist
    ID = np.ravel_multi_index(np.where(np.logical_and(B2 >= A1, B1 <= A2) == True),a.shape)
    Val = IntegrateSlope(constant,B2.flat[ID],B1.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    ID = ID[Val < 0]
    
    return A1,A2,B1,B2

def TwoPeriodSun(constant,delta,slope,slopedir,lat):
    # First derive A1 and A2 from the normal procedure    
    A1,A2 = SunHours(delta,slope,slopedir,lat)
    
    # Then calculate the other two functions.
    # Initialize function    
    
    a,b,c = Constants(delta,slope,slopedir,lat)
    riseSlope, setSlope = BoundsSlope(a,b,c)  
    
    B1 = np.maximum(riseSlope,setSlope)
    B2 = np.minimum(riseSlope,setSlope)
    
    Angle_B1 = AngleSlope(a,b,c,B1)
    Angle_B2 = AngleSlope(a,b,c,B2) 
    
    B1[abs(Angle_B1) > 0.001] = np.pi - B1[abs(Angle_B1) > 0.001]
    B2[abs(Angle_B2) > 0.001] = -np.pi - B2[abs(Angle_B2) > 0.001]    
    
    # Check if two periods really exist
    ID = np.ravel_multi_index(np.where(np.logical_and(B2 >= A1, B1 >= A2) == True),a.shape)
    Val = IntegrateSlope(constant,B2.flat[ID],B1.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    ID = ID[Val < 0]
    
    # Finally calculate resulting values
    Vals = np.zeros(B1.shape)

    Vals.flat[ID] = (IntegrateSlope(constant,A1.flat[ID],B2.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])  + 
                       IntegrateSlope(constant,B1.flat[ID],A2.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID]))
    ID = np.ravel_multi_index(np.where(Vals == 0),a.shape)   
    Vals.flat[ID] = IntegrateSlope(constant,A1.flat[ID],A2.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    
    return(Vals)

def Constants(delta,slope,slopedir,lat):
    # Equation 11
    a = np.sin(delta)*np.cos(lat)*np.sin(slope)*np.cos(slopedir) - np.sin(delta)*np.sin(lat)*np.cos(slope)
    b = np.cos(delta)*np.cos(lat)*np.cos(slope) + np.cos(delta)*np.sin(lat)*np.sin(slope)*np.cos(slopedir)
    c = np.cos(delta)*np.sin(slope)*np.sin(slopedir)
    return(a,b,c)

def AngleSlope(a,b,c,time):
    angle = -a + b*np.cos(time) + c*np.sin(time)
    return(angle)
    
def AngleHorizontal(delta,lat,time):
    angle = np.sin(delta)*np.sin(lat)+np.cos(delta)*np.cos(lat)*np.cos(time)
    return(angle)

def BoundsSlope(a,b,c):
    #Equation 13
    Div = (b**2+c**2)   
    Div[Div <= 0] = 0.00001
    sinB = (a*c + b*np.sqrt(b**2+c**2-a**2)) / Div
    sinA = (a*c - b*np.sqrt(b**2+c**2-a**2)) / Div
    
    sinB[sinB < -1] = -1; sinB[sinB > 1] = 1
    sinA[sinA < -1] = -1; sinA[sinA > 1] = 1
    
    sunrise = np.arcsin(sinA)
    sunset = np.arcsin(sinB)
    return(sunrise,sunset)
    
def TwoPeriods(delta,slope,lat):
    # Equation 7
    TwoPeriod = (np.sin(slope) > np.ones(slope.shape)*np.sin(lat)*np.sin(delta)+np.cos(lat)*np.cos(delta))
    return(TwoPeriod)
    
def BoundsHorizontal(delta,lat):
    # This function calculates sunrise hours based on earth inclination and latitude
    # If there is no sunset or sunrise hours the values are either set to 0 (polar night)
    # or pi (polar day)    
    bound = np.arccos(-np.tan(delta)*np.tan(lat))
    bound[abs(delta+lat) > np.pi/2] = np.pi
    bound[abs(delta-lat) > np.pi/2] = 0
    
    return(bound)

def IntegrateHorizontal(constant,sunrise,sunset,delta,lat):
    # Equation 4 & 6
    ws = np.arccos(-np.tan(delta)*np.tan(lat))
    integral = constant * (np.sin(delta)*np.sin(lat)*ws + np.cos(delta)*np.cos(lat)*np.sin(ws))
#    integral = constant * (np.sin(delta)*np.sin(lat)*(sunset-sunrise) 
#                + np.cos(delta)*np.cos(lat)*(np.sin(sunset)-np.sin(sunrise)))
    return(integral)

def IntegrateNormal(constant,sunrise,sunset):
    integral = constant * (sunset - sunrise)
    return(integral)

def IntegrateSlope(constant,sunrise,sunset,delta,slope,slopedir,lat):
    # Equation 5 & 6
    integral = constant * (np.sin(delta)*np.sin(lat)*np.cos(slope)*(sunset-sunrise) 
                - np.sin(delta)*np.cos(lat)*np.sin(slope)*np.cos(slopedir)*(sunset-sunrise)
                + np.cos(delta)*np.cos(lat)*np.cos(slope)*(np.sin(sunset)-np.sin(sunrise))
                + np.cos(delta)*np.sin(lat)*np.sin(slope)*np.cos(slopedir)*(np.sin(sunset)-np.sin(sunrise))
                - np.cos(delta)*np.sin(slope)*np.sin(slopedir)*(np.cos(sunset)-np.cos(sunrise)))
    return(integral)
    
################################ Standard Functions GIS #######################
    
def ReprojectRaster(Source, Example, overwrite = True, output = None, method = 'average', nc_layername = None):
    
    extension = os.path.splitext(Source)[1]
    if extension == '.nc':
        assert nc_layername != None, 'Specify nc-layername'
        src_filename = 'NETCDF:"'+Source+'":'+nc_layername
    else:
        src_filename = Source
    src = gdal.Open(src_filename, gdal.GA_ReadOnly)
    src_proj = src.GetProjection()
    NDV = src.GetRasterBand(1).GetNoDataValue()
    
    # We want a section of source that matches this:
    match_filename = Example
    match_ds = gdal.Open(match_filename, gdal.GA_ReadOnly)
    match_proj = match_ds.GetProjection()
    match_geotrans = match_ds.GetGeoTransform()
    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize
    
    # Output / destination
    
    if overwrite:
        dst = gdal.GetDriverByName('GTiff').Create(Source[:-4], wide, high, 1, gdal.GDT_Float32)
    else:
        assert output != None, 'Specify output'
        dst = gdal.GetDriverByName('GTiff').Create(output, wide, high, 1, gdal.GDT_Float32)   
    dst.SetGeoTransform( match_geotrans )
    dst.SetProjection( match_proj)
    dst.GetRasterBand(1).SetNoDataValue(NDV)
    
    # Do the work
    if method == 'lanczos':
        gdal.ReprojectImage(src, dst, src_proj, match_proj, gdal.GRA_Lanczos)
    if method == 'average':
        gdal.ReprojectImage(src, dst, src_proj, match_proj, gdal.GRA_Average)
    if method == 'bilinear':
        gdal.ReprojectImage(src, dst, src_proj, match_proj, gdal.GRA_Bilinear)
    
    if output == None:
        output = Source
    
    del src    
    del dst
    
    if overwrite:
        os.remove(Source)
        os.rename(Source[:-4],Source)

    return output
    
def GetGeoInfo(FileName):
    # Function to read the original file's projection:
    SourceDS = gdal.Open(FileName, gdal.GA_ReadOnly)
    NDV = SourceDS.GetRasterBand(1).GetNoDataValue()
    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize
    GeoT = SourceDS.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())
    DataType = SourceDS.GetRasterBand(1).DataType
    DataType = gdal.GetDataTypeName(DataType)
    return NDV, xsize, ysize, GeoT, Projection, DataType

def CreateGeoTiff(Name, Array, driver, NDV, 
                  xsize, ysize, GeoT, Projection, DataType):
     
    # save as a geotiff file with a resolution of 0.001 degree
    NewFileName = Name+'.tif'            
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(NewFileName, int(Array.shape[1]), int(Array.shape[0]), 1, gdal.GDT_Float32, ['COMPRESS=LZW'])                    
    srse = osr.SpatialReference()
    srse.SetWellKnownGeogCS("WGS84")
    dst_ds.SetProjection(srse.ExportToWkt())
    Array[np.isnan(Array)]=NDV
    dst_ds.GetRasterBand(1).SetNoDataValue(NDV)
    dst_ds.SetGeoTransform(GeoT)
    dst_ds.GetRasterBand(1).WriteArray(Array)
    dst_ds = None   

def OpenAsArray(FileName, Bandnumber = 1):
    # Open a geo-map as a numpy array
    DataSet = gdal.Open(FileName, gdal.GA_ReadOnly)
    # Get the band, default is 1.
    Band = DataSet.GetRasterBand(Bandnumber)
    # Open as an array.
    Array = Band.ReadAsArray()
    # Get the No Data Value
    NDV = Band.GetNoDataValue()
    # Convert No Data Points to nans
    Array[Array == NDV] = np.nan
    return Array
    
################### Collect SID and SIS data from landsaf #####################
"""
Created on Fri Jun 12 14:46:00 2015 by Gert Mulder
Adjusted on Thu Apr 4 by Tim Hessels

@author: Gert Mulder &  Tim Hessels
"""
def ShortwaveBasin(Source, SAFpath, latlim, lonlim, Dates = ['2000-01-01','2013-12-31']):
    # Produces shortwave radiation grids for a particular basin or particular bounds    
    Types = ['SIS','SID'] 
    Dates = pd.date_range(Dates[0],Dates[1],freq='D')    
    
    for Type in Types:
        for Date in Dates:
            
            SourcePath = SAFpath + '\\Landsaf\\' + Type + '\\' + 'SAF_' + Type + '_EuropeAfrica_day_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif'
            SAFdir = SAFpath + '\\Landsaf_Clipped\\' + Type + '\\'
            OutPath =  SAFpath + '\\Landsaf_Clipped\\' + Type + '\\' + 'SAF_' + Type + '_EuropeAfrica_day_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif'
            
            if os.path.exists(SAFdir) is False:
                os.mkdir(SAFdir)
            

            Transform(Source, Type, OutPath=OutPath, Dates = [Date.strftime('%Y-%m-%d'),Date.strftime('%Y-%m-%d')])
            nameOut= SAFdir+'SAF_' + Type + '_daily_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif'
            gdal_Translate=Path_WA.Path(Type='gdal_translate')
            fullCmd = ' '.join([gdal_Translate, '-projwin %s %s %s %s' % (lonlim[0]-0.1, latlim[1]+0.1, lonlim[1]+0.1, latlim[0]-0.1), '-of GTiff', OutPath, nameOut])  # -r {nearest}
            process = subprocess.Popen(fullCmd)
            process.wait() 
            print 'Landsaf ' + Type + ' file for ' + Date.strftime('%Y-%m-%d') + ' created.'
            os.remove(OutPath)
            

def Transform(Source, Type, path = '', OutPath = '', Dates = ['2000-01-01','2013-12-31']):
    # This function converts packed nc files to gtiff file of comparable file size
    # Options are:
    # Datatype > 'SIS','SID' or others
    # Dates > Start and end dates
    # Outpath (optional) > Path where the final files will be stored

    if len(path) == 0:
        path = Source + '\\' + Type + '\\EuropeAfrica\\'
    if len(OutPath) == 0:
        OutPath = path
    
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
            
        os.system(Path_WA.Path(Type='7zip') + " x " + ZipFile + " -o" + path + ' -aoa')  
        
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


#------------------------------------------------------------------------------
def reproject_dataset(dataset_in, dataset_example,method):
    """
    A sample function to reproject and resample a dataset from within
    Python. 
    """
    # open dataset that must be transformed    
    g = gdal.Open(dataset_in)
    
    # Get the some information from the example dataset
    gdem=gdal.Open(dataset_example)
    raster_shape = OpenAsArray(dataset_example).shape 
    geo_example = gdem.GetGeoTransform()
    
    # Create new data set
    mem_drv = gdal.GetDriverByName('MEM')
    dest = mem_drv.Create('', int(raster_shape[1]), int(raster_shape[0]), 1, gdal.GDT_Float32)
    
    # Set the new geotransform
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(int(4326))
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(int(4326))
    
    # Set the geotransform
    dest.SetGeoTransform(geo_example)
    dest.SetProjection(osng.ExportToWkt())
    
    # Do the work
    if method == 'lanczos':
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Lanczos)
    if method == 'average':
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Average)
    if method == 'bilinear':
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Bilinear)
    return dest
#------------------------------------------------------------------------------
def gap_filling(dataset,NoDataValue):
    t = gdal.Open(dataset)
    data = t.ReadAsArray()

    if NoDataValue is np.nan:
        mask = ~(np.isnan(data))
    else:
        mask = ~(data==NoDataValue)
    xx, yy = np.meshgrid(np.arange(data.shape[1]), np.arange(data.shape[0]))
    xym = np.vstack( (np.ravel(xx[mask]), np.ravel(yy[mask])) ).T
    data0 = np.ravel( data[:,:][mask] )
    interp0 = scipy.interpolate.NearestNDInterpolator( xym, data0 )
    data_end = interp0(np.ravel(xx), np.ravel(yy)).reshape( xx.shape )
    dataset_GF=dataset[:-4] + '_GF'
    driver = gdal.GetDriverByName('GTiff')
    NDV_data, xsize_data, ysize_data, GeoT_data, Projection_data, DataType_data = GetGeoInfo(dataset)
    CreateGeoTiff(dataset_GF,data_end, driver, NDV_data, xsize_data, ysize_data, GeoT_data, Projection_data, DataType_data)
    EndProduct=dataset[:-4] + '_GF.tif'   
    return (EndProduct)