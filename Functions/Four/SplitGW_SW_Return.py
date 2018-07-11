# -*- coding: utf-8 -*-
"""
Created on Fri Sep 08 15:49:13 2017

@author: tih
"""

def Fraction_Based(nc_outname, Var, Startdate, Enddate):
    """
    This functions divides an array into groundwater and surface water return flows based by using the fractions that are given in the get dictionary script

    Parameters
    ----------
    nc_outname : str
        Path to the NetCDF containing the data
    Var : str
        Name of variable that will be splitted
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'

    Returns
    -------
    DataCube_SW : Array
        Array containing the total supply [time,lat,lon]
    DataCube_GW : Array
        Array containing the amount of non consumed water [time,lat,lon]
    """

     # import water accounting plus modules
    import wa.General.raster_conversions as RC
    import wa.Functions.Start as Start

    # import general modules
    import numpy as np

    # Open Arrays
    DataCube_LU = RC.Open_nc_array(nc_outname, "Landuse")
    DataCube_Parameter = RC.Open_nc_array(nc_outname, Var, Startdate, Enddate)

    # Get Classes
    LU_Classes = Start.Get_Dictionaries.get_sheet5_classes()
    LU_Classes_Keys = LU_Classes.keys()

    # Get fractions
    sw_return_dict = Start.Get_Dictionaries.sw_return_fractions()

    # Create Array for consumed fractions
    DataCube_Parameter_Fractions = np.ones(DataCube_LU.shape) * np.nan

    # Create array with consumed_fractions
    for Classes_LULC in LU_Classes_Keys:
        Values_LULC = LU_Classes[Classes_LULC]
        for Value_LULC in Values_LULC:
            DataCube_Parameter_Fractions[DataCube_LU == Value_LULC] = sw_return_dict[Classes_LULC]

    # Calculate the Surface water and groundwater components based on the fraction
    DataCube_SW_Parameter = DataCube_Parameter[:,:,:] * DataCube_Parameter_Fractions[None,:,:]
    DataCube_GW_Parameter = DataCube_Parameter - DataCube_SW_Parameter

    return(DataCube_SW_Parameter, DataCube_GW_Parameter)