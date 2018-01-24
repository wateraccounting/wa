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
from wa.Products.ETref.CalcETref import calc_ETref


def SetVariables(Dir, Startdate, Enddate, latlim, lonlim, pixel_size, cores, LANDSAF, Waitbar):
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
    Waitbar -- 1 (Default) will print the waitbar																									
    """	
    # Make an array of the days of which the ET is taken
    Dates = pd.date_range(Startdate,Enddate,freq = 'D')
	
    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as Waitbar
        total_amount = len(Dates)
        amount = 0
        Waitbar.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    # Pass variables to parallel function and run
    args = [Dir, lonlim, latlim, pixel_size, LANDSAF]
    if not cores:
        for Date in Dates:
            ETref(Date, args)
            if Waitbar == 1:
                amount += 1
                Waitbar.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
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

    # Set the paths
    nameTmin='Tair-min_GLDAS-NOAH_C_daily_' + Date.strftime('%Y.%m.%d') + ".tif"
    tmin_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','daily','tair_f_inst','min',nameTmin )
        
    nameTmax='Tair-max_GLDAS-NOAH_C_daily_' + Date.strftime('%Y.%m.%d') + ".tif"
    tmax_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','daily','tair_f_inst','max',nameTmax )
        
    nameHumid='Hum_GLDAS-NOAH_kg-kg_daily_'+ Date.strftime('%Y.%m.%d') + ".tif"
    humid_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','daily','qair_f_inst','mean',nameHumid )
        
    namePress='P_GLDAS-NOAH_kpa_daily_'+ Date.strftime('%Y.%m.%d') + ".tif"
    press_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','daily','psurf_f_inst','mean',namePress )
        
    nameWind='W_GLDAS-NOAH_m-s-1_daily_'+ Date.strftime('%Y.%m.%d') + ".tif"
    wind_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','daily','wind_f_inst','mean',nameWind )
        
    if LANDSAF==1:
                
        nameShortClearname = 'ShortWave_Clear_Daily_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif'
        input2_str=os.path.join(Dir,'Landsaf_Clipped','Shortwave_Clear_Sky',nameShortClearname)
                
        nameShortNetname = 'ShortWave_Net_Daily_W-m2_' + Date.strftime('%Y-%m-%d') + '.tif'
        input1_str=os.path.join(Dir,'Landsaf_Clipped','Shortwave_Net',nameShortNetname)
               
        input3_str='not' 
            
    else:
        if Date<pd.Timestamp(pd.datetime(2011, 4, 1)):
           
            nameDownLong='DLWR_CFSR_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
            input2_str=os.path.join(Dir,'Radiation','CFSR',nameDownLong)
                    
            nameDownShort='DSWR_CFSR_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
            input1_str=os.path.join(Dir,'Radiation','CFSR',nameDownShort)
                
            nameUpLong='ULWR_CFSR_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
            input3_str=os.path.join(Dir,'Radiation','CFSR',nameUpLong)
                
        else:         
            nameDownLong='DLWR_CFSRv2_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
            input2_str=os.path.join(Dir,'Radiation','CFSRv2',nameDownLong)
                    
            nameDownShort='DSWR_CFSRv2_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
            input1_str=os.path.join(Dir,'Radiation','CFSRv2',nameDownShort)
                
            nameUpLong='ULWR_CFSRv2_W-m2_' + Date.strftime('%Y.%m.%d') + ".tif"
            input3_str=os.path.join(Dir,'Radiation','CFSRv2',nameUpLong)  
 
   # The day of year
    DOY=Date.dayofyear

    # Load DEM 
    if not pixel_size:
        DEMmap_str=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m_3s.tif')
    else:
        DEMmap_str=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m_3s.tif')
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
    NameETref='ETref_mm-day-1_daily_'+Date.strftime('%Y.%m.%d') + '.tif'    
    NameEnd=os.path.join(output_folder,NameETref)
     
    # Collect geotiff information 					
    geo_out, proj, size_X, size_Y = RC.Open_array_info(DEMmap_str)	

    # Create daily ETref tiff files								
    DC.Save_as_tiff(name=NameEnd, data=ETref, geo=geo_out, projection=proj)




