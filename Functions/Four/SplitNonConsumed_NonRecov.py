# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Four
"""

def GWF_Based(nc_outname, Startdate, Enddate):
    """
    This functions divides an the non consumed flow into non recovable flow and recovable flow by using the fractions that are given by the grey water footprint

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
    DataCube_NonRecovableFlow : Array
        Array containing the non recovable flow [time,lat,lon]
    DataCube_RecovableFlow : Array
        Array containing the recovable flow [time,lat,lon]
    """
    # import water accounting plus modules
    import wa.General.raster_conversions as RC
    import wa.Functions.Start as Start

    # General python modules
    import numpy as np

    # Open Arrays
    DataCube_GWF = RC.Open_nc_array(nc_outname, "Grey_Water_Footprint")
    DataCube_LU = RC.Open_nc_array(nc_outname, "Landuse")
    DataCube_Non_Consumed = RC.Open_nc_array(nc_outname, "Non_Consumed_Water", Startdate, Enddate)

    # Classes that are manmade in the LULC
    Manmade_Classes = ['Irrigated crops','Managed water bodies','Aquaculture','Residential','Greenhouses','Other']

    # Select the pixels that are manmade
    LU_Classes = Start.Get_Dictionaries.get_sheet5_classes()

    # Create Array for consumed fractions
    DataCube_GWF_Mask = np.zeros(DataCube_LU.shape)

    # Create array with consumed_fractions
    for Manmade_Class in Manmade_Classes:
        Values_LULC = LU_Classes[Manmade_Class]
        for Value_LULC in Values_LULC:
            DataCube_GWF_Mask[DataCube_LU == Value_LULC] = DataCube_GWF[DataCube_LU == Value_LULC]

    # Calculate the Surface water and groundwater components based on the fraction
    DataCube_NonRecovableFlow = DataCube_Non_Consumed[:,:,:] * DataCube_GWF_Mask[None,:,:]
    DataCube_RecovableFlow = DataCube_Non_Consumed - DataCube_NonRecovableFlow

    return(DataCube_NonRecovableFlow, DataCube_RecovableFlow)