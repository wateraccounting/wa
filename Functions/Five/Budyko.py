# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 08:18:23 2017

@author: tih
"""
import numpy as np

def Calc_runoff(Name_NC_ETref, Name_NC_P):
        
    Budyko, P, Pavg = Calc_budyko(Name_NC_ETref, Name_NC_P)	

    Runoff = (1-Budyko) * P  
             
    return(Runoff)  		
				
def Calc_ETgreen(Name_NC_ETref, Name_NC_P, Name_NC_ET, Startdate, Enddate):
    
    import wa.General.raster_conversions as RC
    
    Budyko, P, Pavg = Calc_budyko(Name_NC_ETref, Name_NC_P)		
    ET = RC.Open_nc_array(Name_NC_ET, Startdate = Startdate, Enddate = Enddate)
    ETgreen = np.where(np.greater_equal(P, Pavg), np.minimum(1.1 * Budyko * P, ET), np.minimum(1.1 * Budyko * Pavg, ET))

    return(ETgreen)  						

def Calc_budyko(Name_NC_ETref, Name_NC_P):

    import wa.General.raster_conversions as RC
    
    # Extract ETref data from NetCDF file
    ETref = RC.Open_nc_array(Name_NC_ETref)		

    # Extract ETref data from NetCDF file
    P = RC.Open_nc_array(Name_NC_P)		
 
    # Apply moving average over 3 months
    Pavg = RC.Moving_average(P, 2, 0)		
    ETrefavg = RC.Moving_average(ETref, 2, 0)	    

    # remove moving average period 
    P = P[2:,:,:]
    ETref = ETref[2:,:,:]
    
    mask = np.any([np.isnan(ETref), np.isnan(P), np.isnan(Pavg), np.isnan(ETrefavg)], axis=0)
    ETref[mask] = ETrefavg[mask] = P[mask] = Pavg[mask] = np.nan    
    
    P[P == 0] = 0.0001
    Pavg[Pavg == 0] = 0.0001				
    phi = np.where(np.greater_equal(P, Pavg), ETref/P, ETrefavg/Pavg)

    import wa.Functions.Four.SplitET as Budyko
    Budyko = Budyko.Calc_budyko(phi)
    
    return(Budyko, P, Pavg)		

