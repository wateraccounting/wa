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
import datetime
import os
import matplotlib.pyplot as plt
   
def Blue_Green(Dir_Basin, Name_NC_ET, Name_NC_LAI, Name_NC_P, Name_NC_RD, Name_NC_NDM, Name_NC_LU, Startdate, Enddate, Simulation):
    """
    This functions split the evapotranspiration into green and blue evapotranspiration.

    Parameters
    ----------
    Dir_Basin : str
        Path to all the output data of the Basin
    Name_NC_ET : str
        Path to the .nc file containing ET data
    Name_NC_P : str
        Path to the .nc file containing P data
    Name_NC_ETref : str
        Path to the .nc file containing ETref data
    Moving_Averaging_Length: integer
        Number defines the amount of months that are taken into account
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 
    Simulation : int
        Defines the simulation    
        
    Returns
    -------
    ET_Blue : array
              Array[time, lat, lon] contains Blue Evapotranspiration
    ET_Green : array
              Array[time, lat, lon] contains Green Evapotranspiration
    """
    


    return(ET_Blue, ET_Green)



      