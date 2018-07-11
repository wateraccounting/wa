# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Four
"""

def Fraction_Based(nc_outname, Startdate, Enddate):
    """
    This functions divides an array into groundwater and surface water based by using the fractions that are given in the get dictionary script

    Parameters
    ----------
    Name_NC_Parameter : str
        Path to the NetCDF that must be splitted
    Name_NC_LU : str
        Path to the NetCDF containing the LU data
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
    DataCube_Parameter = RC.Open_nc_array(nc_outname, "Total_Supply", Startdate, Enddate)

    # Get Classes
    LU_Classes = Start.Get_Dictionaries.get_sheet5_classes()
    LU_Classes_Keys = LU_Classes.keys()

    # Get fractions
    sw_supply_dict = Start.Get_Dictionaries.sw_supply_fractions()

    # Create Array for consumed fractions
    DataCube_Parameter_Fractions = np.ones(DataCube_LU.shape) * np.nan

    # Create array with consumed_fractions
    for Classes_LULC in LU_Classes_Keys:
        Values_LULC = LU_Classes[Classes_LULC]
        for Value_LULC in Values_LULC:
            DataCube_Parameter_Fractions[DataCube_LU == Value_LULC] = sw_supply_dict[Classes_LULC]

    # Calculate the Surface water and groundwater components based on the fraction
    DataCube_SW_Parameter = DataCube_Parameter[:,:,:] * DataCube_Parameter_Fractions[None,:,:]
    DataCube_GW_Parameter = DataCube_Parameter - DataCube_SW_Parameter

    return(DataCube_SW_Parameter, DataCube_GW_Parameter)