# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 08:18:23 2017

@author: tih
"""
import os
import numpy as np
import netCDF4 as Dataset

def Calc_runoff(Name_NC_ETref, Name_NC_P):

    Budyko, P = Calc_budyko(Name_NC_ETref, Name_NC_P	)	
    Runoff = (1-Budyko) * P  
    return(Runoff)  		
				
def Calc_ETgreen(Name_NC_ETref, Name_NC_P):

    Budyko, P = Calc_budyko(Name_NC_ETref, Name_NC_P)			
    ETgreen = Budyko * P  
    return(ETgreen)  						

def Calc_budyko(Name_NC_ETref, Name_NC_P):

    # Extract ETref data from NetCDF file
    nc_fid = Dataset.Dataset(Name_NC_ETref, 'r')  
    ETref = nc_fid.variables['ETref'][:]			

    # Extract ETref data from NetCDF file
    nc_fid = Dataset.Dataset(Name_NC_P, 'r')  
    P = nc_fid.variables['Prec'][:]	
    		
    P[P == 0]	= 0.0001			
    phi = ETref/P	
    Budyko = 	np.sqrt(phi * np.tanh(1/phi)*(1-np.exp(-phi)))
    return(Budyko, P)				