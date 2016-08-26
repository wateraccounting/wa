# -*- coding: utf-8 -*-
'''
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
'''
# import general python modules
import os
import pandas as pd
from joblib import Parallel, delayed

# import WA+ modules
from StandardDef_ETref import GetGeoInfo, CreateGeoTiff
from Reshape_DEM_ETref import Reshape_DEM
from SetPathETref import SetPaths
from CalcETref import calc_ETref


def SetVariables(Dir, Startdate, Enddate, latlim, lonlim, pixel_size, cores, LANDSAF):
    """
    This function starts to calculate ETref (daily) data based on Hydroshed, GLDAS, and (CFSR/LANDSAF) in parallel or single core

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -60 and 60)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    pixel_size -- The output pixel size																
    cores -- The number of cores used to run the routine.
             It can be 'False' to avoid using parallel computing
			routines.
    LANDSAF -- if LANDSAF data must be used it is 1
    SourceLANDSAF -- the path to the LANDSAF files																									
    """	
    # Make an array of the days of which the ET is taken
    Dates = pd.date_range(Startdate,Enddate,freq = 'D')
	
    # Pass variables to parallel function and run
    args = [Dir, lonlim, latlim, pixel_size, LANDSAF]
    if not cores:
        for Date in Dates:
            ETref(Date, args)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(ETref)(Date, args)
                                         for Date in Dates)
    return results
				
def ETref(Date, args):
    """
    This function starts to calculate ETref (daily) data based on Hydroshed, GLDAS, and (CFSR/LANDSAF) in parallel or single core

    Keyword arguments:
    Date -- panda timestamp
    args -- includes all the parameters that are needed for the ETref
	"""
	
	# unpack the arguments
    [Dir, lonlim, latlim, pixel_size, LANDSAF] = args

    # Set path to all the input for ETref
    tmin_str, tmax_str, humid_str, press_str, wind_str, input1_str, input2_str, input3_str = SetPaths(Dir, Date, LANDSAF)

    # The day of year
    DOY=Date.dayofyear

    # Load DEM 
    if not pixel_size:
        DEMmap_str=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m.tif')
    else:
        DEMmap_str=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m_reshaped_for_ETref.tif')
        Reshape_DEM(Dir, pixel_size, DEMmap_str)

    # Calc ETref	
    ETref = calc_ETref(tmin_str, tmax_str, humid_str, press_str, wind_str, input1_str, input2_str, input3_str, DEMmap_str, DOY)

    # Make directory for the MODIS ET data
    output_folder=os.path.join(Dir,'ETref','Daily')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)    

    # Create the output names        
    NameETref='ETref_mm-day_'+Date.strftime('%Y.%m.%d')    
    NameEnd=os.path.join(output_folder,NameETref)
     
    # Collect geotiff information 					
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(DEMmap_str)	

    # Create daily ETref tiff files								
    CreateGeoTiff(NameEnd,ETref, NDV, xsize, ysize, GeoT, Projection)



