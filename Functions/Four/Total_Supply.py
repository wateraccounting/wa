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
    This functions calculated monthly total supply based ETblue and fractions that are given in the get dictionary script

    Parameters
    ----------
    nc_outname : str
        Path to the NetCDF containing the data
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'

    Returns
    -------
    DataCube_Tot_Sup : Array
        Array containing the total supply [time,lat,lon]
    DataCube_Non_Consumed : Array
        Array containing the amount of non consumed water [time,lat,lon]
    """
    # import water accounting plus modules
    import wa.General.raster_conversions as RC
    import wa.Functions.Start as Start

    # import general modules
    import numpy as np

    # Open Arrays
    DataCube_LU = RC.Open_nc_array(nc_outname, "Landuse")
    DataCube_ETblue = RC.Open_nc_array(nc_outname, "Blue_Evapotranspiration", Startdate, Enddate)

    # Get Classes
    LU_Classes = Start.Get_Dictionaries.get_sheet5_classes()
    LU_Classes_Keys = LU_Classes.keys()

    # Get fractions
    consumed_fractions_dict = Start.Get_Dictionaries.consumed_fractions()

    # Create Array for consumed fractions
    DataCube_Consumed_Fractions = np.ones(DataCube_LU.shape) * np.nan

    # Create array with consumed_fractions
    for Classes_LULC in LU_Classes_Keys:
        Values_LULC = LU_Classes[Classes_LULC]
        for Value_LULC in Values_LULC:
            DataCube_Consumed_Fractions[DataCube_LU == Value_LULC] = consumed_fractions_dict[Classes_LULC]

    # Calculated Total Supply
    DataCube_Tot_Sup = DataCube_ETblue[:,:,:]/DataCube_Consumed_Fractions[None,:,:]

    # Calculated Non consumed
    DataCube_Non_Consumed = DataCube_Tot_Sup - DataCube_ETblue

    return(DataCube_Tot_Sup, DataCube_Non_Consumed)