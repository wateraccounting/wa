# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 11:13:35 2017

@author: tih
"""
import os
import glob
import pandas as pd
import numpy as np
import calendar

def Precipitation(Dir, latlim, lonlim, Startdate, Enddate, Product = 'CHIRPS'):
	
    if Product is 'CHIRPS':
        from wa.Collect import CHIRPS
        Data_Path = os.path.join('Precipitation','CHIRPS')
        Startdates, Enddates = Set_Start_End_Dates(Startdate,Enddate, Dir, Data_Path) 																								

        i = 0																
        for Startdate_Download in Startdates:																
            Enddate_download = Enddates[i]
            CHIRPS.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1												
						
    if Product is 'TRMM':
        from wa.Collect import TRMM
        Data_Path = os.path.join('Precipitation','TRMM')	
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path) 																

        i = 0																
        for Startdate_Download in Startdates:																
            Enddate_download = Enddates[i]
            TRMM.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1												
    return(Data_Path)	
							
def Evapotranspiration(Dir, latlim, lonlim, Startdate, Enddate, Product = 'ETens'):

    if Product is 'ETensV1_0':
        from wa.Products import ETens
        Data_Path = os.path.join('Evaporation','ETensV1_0')
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path) 																  								

        i = 0																
        for Startdate_Download in Startdates:																
            Enddate_download = Enddates[i]
            ETens.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1												
								
    if Product is 'MOD16':
        from wa.Collect import MOD16
        Data_Path = os.path.join('Evaporation','MOD16')	
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path) 																							

        i = 0																
        for Startdate_Download in Startdates:																
            Enddate_download = Enddates[i]
            MOD16.ET_monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1
	   							
    return(Data_Path)		

def DEM(Dir, latlim, lonlim, Resolution):
    
    from wa.Collect import DEM
    DEM.HydroSHED(Dir, latlim, lonlim, '%s' % Resolution)
    Data_Path = os.path.join('HydroSHED','DEM')						
    return(Data_Path)		

def DEM_Dir(Dir, latlim, lonlim, Resolution):
    
    from wa.Collect import DEM
    DEM.HydroSHED_Dir(Dir, latlim, lonlim, '%s' % Resolution)
    Data_Path = os.path.join('HydroSHED','DIR')						
    return(Data_Path)		
				
def ETreference(Dir, latlim, lonlim, Startdate, Enddate):
   	
    from wa.Products import ETref
    Data_Path = os.path.join('ETref','Monthly')	
    Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path) 																
   					
    i = 0																
    for Startdate_Download in Startdates:																
        Enddate_download = Enddates[i]
        ETref.monthly(Dir, Startdate_Download, Enddate_download, latlim, lonlim, pixel_size = 0.025)
        i += 1
    return(Data_Path)


				
def Set_Start_End_Dates(Startdate,Enddate, Dir, Data_Path):				
    Data_Dir = os.path.join(Dir,Data_Path)								
    if os.path.exists(Data_Dir):
        os.chdir(Data_Dir)	
        Dates	= pd.date_range(Startdate,Enddate,freq='MS')	
        Date_Check = np.zeros([len(Dates)+2])
        Date_Check_end = np.zeros([len(Dates),2])										
        i = 0									
        for Date in Dates:
            i += 1														
            month = Date.month
            year = Date.year						
            files =glob.glob('*%d.%02d.01.tif' %(year,month))	
            if len(files) == 1:
                    Date_Check[i] = 1	
        Date_Check_end[:,0] = Date_Check[1:-1] + Date_Check[:-2]																		
        Date_Check_end[:,1] = Date_Check[1:-1] + Date_Check[2:]																		
        Startdates_place = np.argwhere(np.logical_and(Date_Check_end[:,0] == 1,Date_Check_end[:,1] == 0))                   															
        Enddates_place = np.argwhere(np.logical_and(Date_Check_end[:,1] == 1,Date_Check_end[:,0] == 0))                   															
        if Date_Check[1] != 1:
            Startdates = [Startdate]
        else:
            Startdates = []												
        if Date_Check[-2] != 1:												
            Enddates = [Enddate]	
        else:
            Enddates = []														
        for Startdate_number in Startdates_place:
            Date = Dates[Startdate_number]
            month = Date.month																
            year = Date.year
            Startdate_one = '%d-%02d-01' %(year,month)
            Startdates = np.append(Startdates,Startdate_one)            																
        for Enddate_number in np.flipud(Enddates_place):
            Date = Dates[Enddate_number]
            month = Date.month																
            year = Date.year
            dates_in_month = calendar.monthrange(year,month)													
            Enddate_one = '%d-%02d-%02d' %(year,month,int(dates_in_month[1]))
            Enddates = np.insert(Enddates,0,Enddate_one)
    else:
        Startdates = [Startdate]
        Enddates = [Enddate]    								
											
    return(Startdates, Enddates)				