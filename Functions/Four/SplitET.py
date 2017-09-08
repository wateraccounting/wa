# -*- coding: utf-8 -*-
"""
Authors: Bert Coerver, Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Four
"""

# import general python modules
import pandas as pd
import numpy as np
   
def Blue_Green(Name_NC_ET, Name_NC_P, Name_NC_ETref, Startdate, Enddate, Additional_Months):
    """
    This functions split the evapotranspiration into green and blue evapotranspiration.
    Parameters
    ----------
    Dir_Basin : str
        Path to all the output data of the Basin
    Name_NC_ET : str
        Path to the .nc file containing ET data 
    Name_NC_P : str
        Path to the .nc file containing P data (including moving average period)
    Name_NC_ETref : str
        Path to the .nc file containing ETref data (including moving average period)
    Moving_Averaging_Length: integer
        Number defines the amount of months that are taken into account
    Returns
    -------
    ET_Blue : array
              Array[time, lat, lon] contains Blue Evapotranspiration
    ET_Green : array
              Array[time, lat, lon] contains Green Evapotranspiration
    """
    import wa.General.raster_conversions as RC

    # Define startdate and enddate with moving average
    Startdate_Moving_Average = pd.Timestamp(Startdate) - pd.DateOffset(months = Additional_Months)
    Enddate_Moving_Average = pd.Timestamp(Enddate) + pd.DateOffset(months = Additional_Months)
    Startdate_Moving_Average_String = '%d-%02d-%02d' %(Startdate_Moving_Average.year, Startdate_Moving_Average.month, Startdate_Moving_Average.day)
    Enddate_Moving_Average_String = '%d-%02d-%02d' %(Enddate_Moving_Average.year, Enddate_Moving_Average.month, Enddate_Moving_Average.day)

    # Extract ETref data from NetCDF file
    ETref = RC.Open_nc_array(Name_NC_ETref, Startdate = Startdate_Moving_Average_String, Enddate = Enddate_Moving_Average_String)		

    # Extract P data from NetCDF file
    P = RC.Open_nc_array(Name_NC_P, Startdate = Startdate_Moving_Average_String, Enddate = Enddate_Moving_Average_String)		

    # Extract ET data from NetCDF file
    ET = RC.Open_nc_array(Name_NC_ET, Startdate = Startdate, Enddate = Enddate)	
	
    # Apply moving average over 3 months
    Pavg = RC.Moving_average(P, Additional_Months, Additional_Months)		
    ETrefavg = RC.Moving_average(ETref, Additional_Months, Additional_Months)	

    # Calculate aridity index
    Pavg[Pavg == 0] = 0.0001
    phi = ETrefavg/Pavg
	
    # Calculate Budyko
    Budyko = Calc_budyko(phi)
	
    # Calculate ETgreen
    ETgreen = np.minimum(Budyko * P[Additional_Months:-Additional_Months,:,:], ET)
	
    # Calculate ETblue
    ETblue = ET - ETgreen
	
    return(ETblue, ETgreen)


def Calc_budyko(phi):
    """
    This functions calculate the budyko number based on the aridity index
    Parameters
    ----------
    phi : Array
              Array[time, lat, lon] containing phi        
        
    Returns
    -------
    Budyko : array
              Array[time, lat, lon] containing Budyko number
    """
  
    Budyko = np.sqrt(phi * np.tanh(1/phi) * (1-np.exp(-phi)))
    
    return(Budyko)		
      
      