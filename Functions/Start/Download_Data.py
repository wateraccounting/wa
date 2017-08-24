# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Start

Those function download the data that is not downloaded yet
"""
import os
import glob
import pandas as pd
import numpy as np
import calendar

def Precipitation(Dir, latlim, lonlim, Startdate, Enddate, Product = 'CHIRPS', Daily = 'y'):
    """
    This functions check the precipitation files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 
    Product (optional): str
        Defines the product that will be used (default is CHIRPS)    
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """ 
	
    if Product is 'CHIRPS':

        # monthly
        from wa.Collect import CHIRPS
        
        # Define data path 
        Data_Path = os.path.join('Precipitation','CHIRPS')
        Data_Path_Monthly = os.path.join('Precipitation','CHIRPS', 'Monthly')
        
        # Get start and enddates     
        Startdates, Enddates = Set_Start_End_Dates(Startdate,Enddate, Dir, Data_Path_Monthly, 'MS') 																								
        
        i = 1
        # Loop over the startdates																
        for Startdate_Download in Startdates:	

            # Define enddate															
            Enddate_download = Enddates[-i]
            
            # download data between startdate and enddate
            CHIRPS.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1												

        if Daily is 'y':
            # daily
            Data_Path_Daily = os.path.join('Precipitation','CHIRPS', 'Daily')
            Startdates, Enddates = Set_Start_End_Dates(Startdate,Enddate, Dir, Data_Path_Daily, 'D') 																								
    
            i = 1																
            for Startdate_Download in Startdates:	
    
                # Define enddate																	
                Enddate_download = Enddates[-i]
                
                # Download the daily data
                CHIRPS.daily(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
                i += 1	
						
    if Product is 'TRMM':
        from wa.Collect import TRMM
        
        # Define data path        
        Data_Path = os.path.join('Precipitation','TRMM')	
        Data_Path_Monthly = os.path.join('Precipitation','TRMM', 'Monthly')	
        
        # Get start and enddates        
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path_Monthly, 'MS') 																

        i = 1																
        for Startdate_Download in Startdates:	

            # Define enddate																	
            Enddate_download = Enddates[-i]
            
            # Download the daily data            
            TRMM.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1	

        if Daily is 'y':
            # daily
            Data_Path_Daily = os.path.join('Precipitation','TRMM', 'Daily')	        
            Startdates, Enddates = Set_Start_End_Dates(Startdate,Enddate, Dir, Data_Path_Daily, 'D') 																								
    
            i = 1																
            for Startdate_Download in Startdates:
    
                # Define enddate																	
                Enddate_download = Enddates[-i]
                
                # Download the daily data            
                TRMM.daily(Dir, Startdate_Download, Enddate_download, latlim, lonlim)	
                i += 1	

    if Product is 'RFE':
        from wa.Collect import RFE
        
        # Define data path        
        Data_Path = os.path.join('Precipitation','RFE')	
        Data_Path_Monthly = os.path.join('Precipitation','RFE', 'Monthly')	
        
        # Get start and enddates        
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path_Monthly, 'MS') 																

        i = 1																
        for Startdate_Download in Startdates:	

            # Define enddate																	
            Enddate_download = Enddates[-i]
            
            # Download the daily data            
            RFE.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1	

        if Daily is 'y':
            # daily
            Data_Path_Daily = os.path.join('Precipitation','RFE', 'Daily')	        
            Startdates, Enddates = Set_Start_End_Dates(Startdate,Enddate, Dir, Data_Path_Daily, 'D') 																								
    
            i = 1																
            for Startdate_Download in Startdates:
    
                # Define enddate																	
                Enddate_download = Enddates[-i]
                
                # Download the daily data            
                RFE.daily(Dir, Startdate_Download, Enddate_download, latlim, lonlim)	
                i += 1	
							
    return(Data_Path)	
							
def Evapotranspiration(Dir, latlim, lonlim, Startdate, Enddate, Product = 'MOD16'):
    """
    This functions check the evapotranspiration files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 
    Product (optional): str
        Defines the product that will be used (default is MOD16)    
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """ 
    if Product is 'ETensV1_0':
        
        from wa.Products import ETens
        
        # Define data path             
        Data_Path = os.path.join('Evaporation','ETensV1_0')
        
        # Get start and enddates             
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path, 'MS') 																  								

        i = 1																
        for Startdate_Download in Startdates:

            # Define enddate																	
            Enddate_download = Enddates[-i]
            
            # download data between startdate and enddate            
            ETens.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1												
								
    if Product is 'MOD16':
        from wa.Collect import MOD16
        
        # Define data path             
        Data_Path = os.path.join('Evaporation','MOD16')	
        
        # Get start and enddates             
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path, 'MS') 																							

        i = 1																
        for Startdate_Download in Startdates:

            # Define enddate																	
            Enddate_download = Enddates[-i]
            
            # download data between startdate and enddate            
            MOD16.ET_monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1

    if Product is 'GLEAM':
        from wa.Collect import GLEAM
        
        # Define data path             
        Data_Path = os.path.join('Evaporation','GLEAM','Monthly')	
        
        # Get start and enddates             
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path, 'MS') 																							

        i = 1																
        for Startdate_Download in Startdates:

            # Define enddate																	
            Enddate_download = Enddates[-i]
            
            # download data between startdate and enddate            
            GLEAM.ET_monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1
	   							
    return(Data_Path)		

def LAI(Dir, latlim, lonlim, Startdate, Enddate, Product = 'MOD15'):
    """
    This functions check the Leaf Area Index files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 
    Product (optional): str
        Defines the product that will be used (default is MOD15)    
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """ 
    if Product is 'MOD15':
        from wa.Collect import MOD15
        
        # Define data path             
        Data_Path = os.path.join('LAI','MOD15')
        
        # Get start and enddates             
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path, '8D') 																							

        i = 1																
        for Startdate_Download in Startdates:

            # Define enddate																	
            Enddate_download = Enddates[-i]
            
            # download data between startdate and enddate            
            MOD15.LAI_8daily(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1

    return(Data_Path)	

def NPP(Dir, latlim, lonlim, Startdate, Enddate, Product = 'MOD17'):
    """
    This functions check the NPP files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 
    Product (optional): str
        Defines the product that will be used (default is MOD17)    
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """ 
    if Product is 'MOD17':
        from wa.Collect import MOD17
        
        # Define data path             
        Data_Path = os.path.join('NPP','MOD17')	
        
        # Get start and enddates             
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path, 'AS') 																							

        i = 1																
        for Startdate_Download in Startdates:	

            # Define enddate																
            Enddate_download = Enddates[-i]
            
            # download data between startdate and enddate            
            MOD17.NPP_yearly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1

    return(Data_Path)	

def GPP(Dir, latlim, lonlim, Startdate, Enddate, Product = 'MOD17'):
    """
    This functions check the GPP files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 
    Product (optional): str
        Defines the product that will be used (default is MOD17)    
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """     
    if Product is 'MOD17':
        from wa.Collect import MOD17
        
        # Define data path             
        Data_Path = os.path.join('GPP','MOD17')
        
        # Get start and enddates             
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path, '8D') 																							

        i = 1																
        for Startdate_Download in Startdates:	

            # Define enddate																
            Enddate_download = Enddates[-i]
            
            # download data between startdate and enddate            
            MOD17.GPP_8daily(Dir, Startdate_Download, Enddate_download,latlim, lonlim)	
            i += 1

    return(Data_Path)	
    
def DEM(Dir, latlim, lonlim, Resolution):
    """
    This functions check the DEM file from SRTM that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    resolution (optional): 3s or 15s
        Defines the resolution of the product 
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """     
    from wa.Collect import DEM
    
    # download data between startdate and enddate    
    DEM.HydroSHED(Dir, latlim, lonlim, '%s' % Resolution)
    
    # Define data path         
    Data_Path = os.path.join('HydroSHED','DEM')	
					
    return(Data_Path)		

def DEM_Dir(Dir, latlim, lonlim, Resolution):
    """
    This functions check the DEM direction file from SRTM that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    resolution (optional): 3s or 15s
        Defines the resolution of the product 
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """      
    from wa.Collect import DEM
    
    # download data between startdate and enddate    
    DEM.HydroSHED_Dir(Dir, latlim, lonlim, '%s' % Resolution)
    
    # Define data path      
    Data_Path = os.path.join('HydroSHED','DIR')		
				
    return(Data_Path)		
    
def JRC_occurrence(Dir, latlim, lonlim):
    """
    This functions check the water occurrence file from JRC that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """     
    from wa.Collect import JRC
    
    # download data between startdate and enddate    
    JRC.Occurrence(Dir, latlim, lonlim)
    
    # Define data path         
    Data_Path = os.path.join('JRC','Occurrence')	
					
    return(Data_Path)			
			
def ETreference(Dir, latlim, lonlim, Startdate, Enddate):
    """
    This functions check the ET reference files that needs to be downloaded, and send the request to the product functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'  
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """     	
    from wa.Products import ETref
    
    # Define data path         
    Data_Path = os.path.join('ETref','Monthly')	
    
    # Get start and enddates         
    Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Dir, Data_Path, 'MS') 																
   					
    i = 1																
    for Startdate_Download in Startdates:																
        Enddate_download = Enddates[-i]
        
        # download data between startdate and enddate        
        ETref.monthly(Dir, Startdate_Download, Enddate_download, latlim, lonlim, pixel_size = 0.025)
        i += 1
    return(Data_Path)

def GWF(Dir, latlim, lonlim):
    """
    This functions check the Gray Water Footprint file from TWC that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
        
    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """     
    from wa.Collect import TWC
    
    # download data between startdate and enddate    
    TWC.Gray_Water_Footprint(Dir, latlim, lonlim)
    
    # Define data path         
    Data_Path = os.path.join('TWC','GWF')	
					
    return(Data_Path)	

				
def Set_Start_End_Dates(Startdate,Enddate, Dir, Data_Path, freq):	
    """
    This functions check all the files if they are already downloaded, or needs to be downloaded.

    Parameters
    ----------
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'  
    Dir : str
        Path to all the output data of the Basin
    Data_Path : str
        Path from the Dir to the downloaded data
    freq : 'D','8D','MS', or 'AS'
        Defines the frequenct of the dataset that must be downloaded
        
    Returns
    -------
    Startdates : str
        Contains all the start dates of data that needs to be downloaded
    Enddates : str
        Contains all the end dates of data that needs to be downloaded
    """  
	 # Defines the total data path		
    Data_Dir = os.path.join(Dir,Data_Path)	

    # Check if folder already exists							
    if os.path.exists(Data_Dir):
        os.chdir(Data_Dir)
        
        # Defines the dates of the 8 daily periods
        if freq == '8D':
            import wa.Collect.MOD15.DataAccess as TimeStamps_8D
            Dates = TimeStamps_8D.Make_TimeStamps(Startdate, Enddate)
        else:    
            Dates	= pd.date_range(Startdate,Enddate,freq=freq)	
        
        # Check if the dates already exists
        Date_Check = np.zeros([len(Dates)+2])
        Date_Check_end = np.zeros([len(Dates),2])										
        i = 0	
 
        # Loop over the dates								
        for Date in Dates:
            i += 1	
            
            # Define month, day, and year													
            month = Date.month
            year = Date.year
            day = Date.day
            
            # Get all the files that already exists in folder
            if freq == 'MS':						
                files =glob.glob('*monthly_%d.%02d.01.tif' %(year,month))	
            if freq == 'AS':						
                files =glob.glob('*yearly_%d.%02d.01.tif' %(year,month))	
            if freq == 'D':	     
                files =glob.glob('*daily_%d.%02d.%02d.tif' %(year,month, day))	
            if freq == '8D':				
                files =glob.glob('*8-daily_%d.%02d.%02d.tif' %(year,month, day))	 
            # If file exits put a 1 in the array    
            if len(files) == 1:
                Date_Check[i] = 1	
                          
        # Add additional numbers to the Date_Check array                
        Date_Check_end[:,0] = Date_Check[1:-1] + Date_Check[:-2]																		
        Date_Check_end[:,1] = Date_Check[1:-1] + Date_Check[2:]	

        # Find place where there is a startdate														
        Startdates_place = np.argwhere(np.logical_and(Date_Check_end[:,0] == 1,Date_Check_end[:,1] == 0))                   															
        # Find place where there is a enddate	
        Enddates_place = np.argwhere(np.logical_and(Date_Check_end[:,1] == 1,Date_Check_end[:,0] == 0))  

        # Add all the startdates and enddates in 1 array                 															
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
            day = Date.day
            
            # Define startdate
            Startdate_one = '%d-%02d-%02d' %(year,month, day)
            Startdates = np.append(Startdates,Startdate_one)            																

        for Enddate_number in np.flipud(Enddates_place):
            Date = Dates[Enddate_number]
            month = Date.month																
            year = Date.year
            dates_in_month = calendar.monthrange(year,month)
            # Define enddate													
            Enddate_one = '%d-%02d-%02d' %(year,month,int(dates_in_month[1]))
            Enddates = np.append(Enddates, Enddate_one)
            
    # If folder not exists than all dates must be downloaded         
    else:
        Startdates = [Startdate]
        Enddates = [Enddate]    								
											
    return(Startdates, Enddates)				