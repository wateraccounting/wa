# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
"""

# import general python modules
import os
import numpy as np

# import WA+ modules
from StandardDef_ETref import ReprojectRaster, reproject_dataset, OpenAsArray, GetGeoInfo
from SlopeInfluence_ETref import SlopeInfluence				
					
def process_GLDAS(Tmax, Tmin, humidity, surface_pressure):
    """
    This function calculates the actual and saturated vapour pressure by using GLDAS data
  				
    Keyword arguments:
    Tmax -- [] numpy array with the maximal temperature
    Tmin -- [] numpy array with the minimal temperature
    humidity -- [] numpy array with the humidity
    surface_pressure -- [] numpy array with the surface pressure	
    """
	# calculate the average temparature based on FAO 			
    T_mean = (Tmax + Tmin) / 2   
    
	# calculate the slope of saturation
    delta = 4098 * (0.6108  * np.exp(17.27 * T_mean / (T_mean + 237.3))) / (T_mean + 237.3)**2
    
    # calculate the saturation vapour pressure by using the max and min temparature				
    e0_max = 0.6108 * np.exp(17.27 * Tmax / (Tmax + 237.3))
    e0_min = 0.6108 * np.exp(17.27 * Tmin / (Tmin + 237.3))
    
    # calculate the saturated vapour pressure				
    es = (e0_max + e0_min) / 2
    
    # calculate the max and min relative humidity				
    RH_max = np.minimum((1/0.622) * humidity * surface_pressure / e0_min, 1)*100
    RH_min = np.minimum((1/0.622) * humidity * surface_pressure / e0_max, 1)*100
    
    # calculate the actual vapour pressure				
    ea = (e0_min * RH_max/100 + e0_max * RH_min/100) / 2
    
    return ea, es, delta

def lapse_rate(temperature_map, DEMmap):    
    """
    This function downscales the GLDAS temperature map by using the DEM map
  				
    Keyword arguments:
    temperature_map -- 'C:/' path to the temperature map
    DEMmap -- 'C:/' path to the DEM map
    """
				
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
    """
    This function downscales the GLDAS air pressure map by using the DEM map
  				
    Keyword arguments:
    pressure_map -- 'C:/' path to the pressure map
    DEMmap -- 'C:/' path to the DEM map
    """	

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

def slope_correct(down_short_hor, pressure, ea, DEMmap, DOY):
    """
    This function downscales the CFSR solar radiation by using the DEM map
    The Slope correction is based on Allen et al. (2006)
    'Analytical integrated functions for daily solar radiation on slope'  		
				
    Keyword arguments:
    down_short_hor -- numpy array with the horizontal downwards shortwave radiation
    pressure -- numpy array with the air pressure
    ea -- numpy array with the actual vapour pressure
    DEMmap -- 'C:/' path to the DEM map
    DOY -- day of the year
    """	

    # Get Geo Info
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(DEMmap)
    
    minx = GeoT[0]
    miny = GeoT[3] + xsize*GeoT[4] + ysize*GeoT[5] 
    
    x = np.flipud(np.arange(xsize)*GeoT[1] + minx + GeoT[1]/2)
    y = np.flipud(np.arange(ysize)*-GeoT[5] + miny + -GeoT[5]/2)
    
    # Calculate Extraterrestrial Solar Radiation [W m-2]
    demmap = OpenAsArray(DEMmap)   
    demmap[demmap<0]=0
    
	# apply the slope correction			
    Ra_hor, Ra_slp, sinb, sinb_hor, fi, slope, ID = SlopeInfluence(demmap,y,x,DOY)
    

    # Calculate atmospheric transmissivity
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
				