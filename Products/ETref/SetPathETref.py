# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
"""

# import general python modules
import pandas as pd
import os


def SetPaths(Dir, Date, LANDSAF):
    '''
	This function set all the paths to the maps that are needed to calculate the ETref

    Dir -- The directory of all the files
    Date -- panda timestring 
    LANDSAF -- 1 if LANDSAF data must be used							
    '''
    # Set the paths
    nameTmin='Tair-min_GLDAS-NOAH_C_daily_' + Date.strftime('%Y.%m.%d') + ".tif"
    tmin_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','tair','min',nameTmin )
        
    nameTmax='Tair-max_GLDAS-NOAH_C_daily_' + Date.strftime('%Y.%m.%d') + ".tif"
    tmax_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','tair','max',nameTmax )
        
    nameHumid='Hum_GLDAS-NOAH_kg-kg_daily_'+ Date.strftime('%Y.%m.%d') + ".tif"
    humid_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','qair','mean',nameHumid )
        
    namePress='P_GLDAS-NOAH_kpa_daily_'+ Date.strftime('%Y.%m.%d') + ".tif"
    press_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','psurf','mean',namePress )
        
    nameWind='W_GLDAS-NOAH_m-s-1_daily_'+ Date.strftime('%Y.%m.%d') + ".tif"
    wind_str=os.path.join(Dir,'Weather_Data','Model','GLDAS','Daily','wind','mean',nameWind )
        
    if LANDSAF==1:
                
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
																
	return(tmin_str, tmax_str, humid_str, press_str, wind_str, input1, input2, input3)