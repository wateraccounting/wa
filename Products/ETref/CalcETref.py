# -*- coding: utf-8 -*-
'''
Authors: Bert Coerver, Tim Hessels
         UNESCO-IHE 2016
Contact: b.coerver@unesco-ihe.org
         t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
'''
# import general python modules
import gdal
import numpy as np

# import WA+ modules
from StandardDef_ETref import reproject_dataset, OpenAsArray, GetGeoInfo
from GLDAS_gap_filling_ETref import gap_filling
from Interpolate_Meteo_ETref import process_GLDAS, lapse_rate, adjust_P, slope_correct

def calc_ETref(tmin_str, tmax_str, humid_str, press_str, wind_str, down_short_str, down_long_str, up_long_str, DEMmap_str, DOY):
    """
    This function calculates the ETref by using all the input parameters (path)
    according to FAO standards
    see: http://www.fao.org/docrep/x0490e/x0490e08.htm#TopOfPage
 	
    Keyword arguments:
    tmin_str -- 'C:/'  path to the minimal temperature tiff file [degrees Celcius], e.g. from GLDAS
    tmax_str -- 'C:/'  path to the maximal temperature tiff file [degrees Celcius], e.g. from GLDAS
    humid_str -- 'C:/'  path to the humidity tiff file [kg/kg], e.g. from GLDAS
    press_str -- 'C:/'  path to the air pressure tiff file [kPa], e.g. from GLDAS
    wind_str -- 'C:/'  path to the wind velocity tiff file [m/s], e.g. from GLDAS
    down_short_str -- 'C:/'  path to the downward shortwave radiation tiff file [W*m-2], e.g. from CFSR/LANDSAF
    down_long_str -- 'C:/'  path to the downward longwave radiation tiff file [W*m-2], e.g. from CFSR/LANDSAF
    up_long_str -- 'C:/'  path to the upward longwave radiation tiff file [W*m-2], e.g. from CFSR/LANDSAF			
    DEMmap_str -- 'C:/'  path to the DEM tiff file [m] e.g. from HydroSHED
    DOY -- Day of the year				
    """

    # Get some geo-data to save results
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(DEMmap_str)
    raster_shape = OpenAsArray(DEMmap_str).shape 

    # Create array to store results
    ETref = np.zeros(raster_shape)
								
    # gap fill
    tmin_str_GF = gap_filling(tmin_str,-9999)
    tmax_str_GF = gap_filling(tmax_str,-9999)
    humid_str_GF = gap_filling(humid_str,-9999)
    press_str_GF = gap_filling(press_str,-9999)
    wind_str_GF = gap_filling(wind_str,-9999)
    down_short_str_GF = gap_filling(down_short_str,np.nan)
    down_long_str_GF = gap_filling(down_long_str,np.nan)
    if up_long_str is not 2:				
        up_long_str_GF = gap_filling(up_long_str,np.nan)
    else:
        up_long_str_GF = 'nan'							
    
    
    #dictionary containing all tthe paths to the input-maps
    inputs = dict({'tmin':tmin_str_GF,'tmax':tmax_str_GF,'humid':humid_str_GF,'press':press_str_GF,'wind':wind_str_GF,'down_short':down_short_str_GF,'down_long':down_long_str_GF,'up_long':up_long_str_GF})
   
    
    #dictionary containing numpy arrays of al initial and intermediate variables    
    input_array = dict({'tmin':None,'tmax':None,'humid':None,'press':None,'wind':None,'albedo':None,'down_short':None,'down_long':None,'up_short':None,'up_long':None,'net_radiation':None,'ea':None,'es':None,'delta':None})
    
    #APPLY LAPSE RATE CORRECTION ON TEMPERATURE
    tmin = lapse_rate(inputs['tmin'], DEMmap_str)
    tmax = lapse_rate(inputs['tmax'], DEMmap_str)
    

    #PROCESS PRESSURE MAPS 
    press =adjust_P(inputs['press'], DEMmap_str)
    
    #PREPARE HUMIDITY MAPS
    dest = reproject_dataset(inputs['humid'], DEMmap_str,method = 'bilinear')
    band=dest.GetRasterBand(1)
    humid=band.ReadAsArray()
    dest = None
    
     
    #CORRECT WIND MAPS
    dest = reproject_dataset(inputs['wind'], DEMmap_str,method = 'bilinear')
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
        dest = reproject_dataset(inputs['down_short'], DEMmap_str,method = 'bilinear')
        band=dest.GetRasterBand(1)
        down_short=band.ReadAsArray()
        dest = None
        down_short, tau, bias = slope_correct(down_short,press,ea,DEMmap_str,DOY)
        
           
        #OPEN OTHER RADS
        up_short = down_short*0.23
        
        
        dest = reproject_dataset(inputs['down_long'], DEMmap_str,method = 'bilinear')
        band=dest.GetRasterBand(1)
        down_long=band.ReadAsArray()
        dest = None
                
        dest = reproject_dataset(inputs['up_long'], DEMmap_str,method = 'bilinear')
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
    
    # Set limits ETref      
    ETref[ETref<0]=0
    ETref[ETref>400]=np.nan			
    
    #return a reference ET map (numpy array), a dictionary containing all intermediate information and a bias of the slope correction on down_short
    return ETref
				
				
				
				
				
				
				
				
				

   
			
				
				
				
				
				
				
				
				