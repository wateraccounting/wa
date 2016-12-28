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
from wa.General import raster_conversions as RC
from wa.General import data_conversions as DC
from wa.Products.ETref.SetPathETref import SetPaths
from wa.Products.ETref.CalcETref import calc_ETref


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
        DEMmap_str=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m.tif')
        dest, ulx, lry, lrx, uly, epsg_to = RC.reproject_dataset_epsg(DEMmap_str, pixel_spacing = pixel_size, epsg_to=4326, method = 2)			
        DEMmap_str=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m_reshaped_for_ETref.tif')
        DEM_data = dest.GetRasterBand(1).ReadAsArray()
        geo_dem = [ulx, pixel_size, 0.0, uly, 0.0, - pixel_size]            
        DC.Save_as_tiff(name=DEMmap_str, data=DEM_data, geo=geo_dem, projection='4326')

    # Calc ETref	
    ETref = calc_ETref(Dir, tmin_str, tmax_str, humid_str, press_str, wind_str, input1_str, input2_str, input3_str, DEMmap_str, DOY)

    # Make directory for the MODIS ET data
    output_folder=os.path.join(Dir,'ETref','Daily')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)    

    # Create the output names        
    NameETref='ETref_mm-day_'+Date.strftime('%Y.%m.%d') + '.tif'    
    NameEnd=os.path.join(output_folder,NameETref)
     
    # Collect geotiff information 					
    geo_out, proj, size_X, size_Y = RC.Open_array_info(DEMmap_str)	

    # Create daily ETref tiff files								
    DC.Save_as_tiff(name=NameEnd, data=ETref, geo=geo_out, projection=proj)




