# -*- coding: utf-8 -*-
"""
Created on Mon May 15 14:27:44 2017

@author: tih
"""

def Calc_surface_withdrawal(Dir_Basin, nc_outname, Startdate, Enddate, Example_dataset, ETref_Product, P_Product):

    from netCDF4 import Dataset

    import wa.Functions.Four as Four
    import wa.General.raster_conversions as RC

    # Open variables in netcdf
    fh = Dataset(nc_outname)
    Variables_NC = [var for var in fh.variables]
    fh.close()

    # Open or calculate Blue Evapotranspiration
    if not "Blue_Evapotranspiration" in Variables_NC:
        # Calc ET blue and green
        DataCube_ETblue, DataCube_ETgreen = Four.SplitET.Blue_Green(Dir_Basin, nc_outname, ETref_Product, P_Product, Startdate, Enddate)
    else:
        DataCube_ETblue = RC.Open_nc_array(nc_outname, "Blue_Evapotranspiration", Startdate, Enddate)

    # Open data array info based on example data
    geo_out, epsg, size_X, size_Y = RC.Open_array_info(Example_dataset)

    # Open array with surface water fractions
    DataCube_frac_sw = RC.Open_nc_array(nc_outname, "Fraction_Surface_Water_Supply")

    # Total amount of ETblue taken out of rivers
    DataCube_surface_withdrawal = DataCube_ETblue * DataCube_frac_sw[None,:,:]

    return(DataCube_surface_withdrawal)

def Calc_surface_runoff(Dir_Basin, nc_outname, Startdate, Enddate, Example_dataset, ETref_Product, P_Product):

    from netCDF4 import Dataset
    import numpy as np

    import wa.Functions.Four as Four
    import wa.General.raster_conversions as RC

    # Open variables in netcdf
    fh = Dataset(nc_outname)
    Variables_NC = [var for var in fh.variables]
    fh.close()

    # Open or calculate Blue Evapotranspiration
    if not "Green_Evapotranspiration" in Variables_NC:
        # Calc ET blue and green
        DataCube_ETblue, DataCube_ETgreen = Four.SplitET.Blue_Green(Dir_Basin, nc_outname, ETref_Product, P_Product, Startdate, Enddate)
    else:
        DataCube_ETgreen = RC.Open_nc_array(nc_outname, "Green_Evapotranspiration", Startdate, Enddate)

    # Open rainfall data
    DataCube_P = RC.Open_nc_array(nc_outname, "Precipitation", Startdate, Enddate)

    # Calculate Runoff
    DataCube_surface_runoff = DataCube_P - DataCube_ETgreen
    DataCube_surface_runoff[DataCube_surface_runoff<0] = 0

    return(DataCube_surface_runoff)