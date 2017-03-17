# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 10:07:52 2017

@author: tih
"""
import os
import gdal
import numpy as np

from wa import WA_Paths
from wa.General import raster_conversions as RC
from wa.General import data_conversions as DC
import wa.Functions.Five as Five
import wa.Functions.Start as Start

def Calculate(Basin, P_Product, ET_Product, Startdate, Enddate, Resolution, Simulation):

    ######################### Set General Parameters ##############################

    # Create the Basin folder
    Dir_Home = WA_Paths.Paths(Type = 'Home')
    Dir_Basin = os.path.join(Dir_Home, Basin)
    if not os.path.exists(Dir_Basin):
        os.makedirs(Dir_Basin)	

    # Get the boundaries of the basin based on the shapefile of the watershed
    Boundaries, Shape_file_name_shp = Start.Boundaries.Determine(Basin)

    ############################# Download Data ###################################

    # Download data
    Data_Path_P = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, P_Product) 
    Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, ET_Product)
    Data_Path_DEM = Start.Download_Data.DEM(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution) 
    Data_Path_DEM_Dir = Start.Download_Data.DEM_Dir(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution) 
    Data_Path_ETref = Start.Download_Data.ETreference(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate) 

    ###################### Save Data as netCDF files ##############################

    # Get the data of DEM and save as nc, This dataset is also used as reference for others
    Example_dataset = os.path.join(Dir_Basin, Data_Path_DEM, 'DEM_HydroShed_m_%s.tif' %Resolution)
    DEMdest = gdal.Open(Example_dataset)
    DataCube_DEM = DEMdest.GetRasterBand(1).ReadAsArray()

    Name_NC_DEM = DC.Create_NC_name('DEM', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_DEM):
        DC.Save_as_NC(Name_NC_DEM, DataCube_DEM, 'DEM', Example_dataset)

    DEMdest = None
    del DataCube_DEM

    # Get the data of flow direction and save as nc.
    Dir_dataset = os.path.join(Dir_Basin, Data_Path_DEM_Dir, 'DIR_HydroShed_-_%s.tif' %Resolution)
    DEMDirdest = gdal.Open(Dir_dataset)
    DataCube_DEM_Dir = DEMDirdest.GetRasterBand(1).ReadAsArray()

    Name_NC_DEM_Dir = DC.Create_NC_name('DEM_Dir', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_DEM_Dir):
        DC.Save_as_NC(Name_NC_DEM_Dir, DataCube_DEM_Dir, 'DEM_Dir', Example_dataset)
    DEMDirdest = None
    del DataCube_DEM_Dir

    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    # Precipitation data
    Name_NC_Prec = DC.Create_NC_name('Prec', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_Prec):
	
        # Get the data of Precipitation and save as nc
        DataCube_Prec = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_P, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_Prec, DataCube_Prec, 'Prec', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_Prec

    # Evapotranspiration data
    Name_NC_ET = DC.Create_NC_name('ET', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_ET):

        # Get the data of Evaporation and save as nc
        DataCube_ET = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ET, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ET, DataCube_ET, 'ET', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ET

    # Reference Evapotranspiration data
    Name_NC_ETref = DC.Create_NC_name('ETref', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_ETref):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_ETref = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ETref, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ETref, DataCube_ETref, 'ETref', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ETref

    ##################### Rasterize the basin shapefile ###########################

    Name_NC_Basin = DC.Create_NC_name('Basin', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_Basin):

        Raster_Basin = RC.Vector_to_Raster(Dir_Basin, Shape_file_name_shp, Example_dataset)
        Raster_Basin = np.clip(Raster_Basin, 0, 1)
        DC.Save_as_NC(Name_NC_Basin, Raster_Basin, 'Basin', Example_dataset)
        #del Raster_Basin

    ###################### Calculate Runoff with Budyko ###########################

    Name_NC_Runoff = DC.Create_NC_name('Runoff', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_Runoff):

        DataCube_Runoff = Five.Budyko.Calc_runoff(Name_NC_ETref, Name_NC_Prec)
        DC.Save_as_NC(Name_NC_Runoff, DataCube_Runoff, 'Runoff', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_Runoff

    ######################### Apply Channel Routing ###############################

    info = ['monthly','pixels', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_NC_Acc_Pixels = DC.Create_NC_name('Acc_Pixels', Simulation, Dir_Basin)
    info = ['monthly','m3', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_NC_Routed_Discharge = DC.Create_NC_name('Routed_Discharge', Simulation, Dir_Basin, info)

    if not (os.path.exists(Name_NC_Acc_Pixels) and os.path.exists(Name_NC_Routed_Discharge)):
        Accumulated_Pixels, Routed_Discharge = Five.Channel_Routing.Channel_Routing(Name_NC_DEM_Dir, Name_NC_Runoff, Name_NC_Basin, Example_dataset, Degrees = 1)

        # Save Results
        DC.Save_as_NC(Name_NC_Acc_Pixels, Accumulated_Pixels, 'Acc_Pixels', Example_dataset)
        DC.Save_as_NC(Name_NC_Routed_Discharge, Routed_Discharge, 'Routed_Discharge', Example_dataset, Startdate, Enddate, 'monthly',)

    #################### Calculate the river and river zones ######################
    
    Name_NC_Rivers = DC.Create_NC_name('Rivers', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_Rivers):

        # Open routed discharge array
        Routed_Discharge = RC.Open_nc_array(Name_NC_Routed_Discharge, Var='Routed_Discharge')
        Raster_Basin = RC.Open_nc_array(Name_NC_Basin, Var='Basin')

        # Calculate mean average over the period
        Routed_Discharge_Ave = np.nanmean(Routed_Discharge, axis=0)

        # Define the 2% highest pixels as rivers
        Rivers = np.zeros([np.size(Routed_Discharge_Ave,0),np.size(Routed_Discharge_Ave,1)])
        Routed_Discharge_Ave[Raster_Basin != 1] = np.nan
        Routed_Discharge_Ave_number = np.nanpercentile(Routed_Discharge_Ave,98)
        Rivers[Routed_Discharge_Ave > Routed_Discharge_Ave_number] = 1  # if yearly average is larger than 5000km3/month that it is a river

        # Save the river file as netcdf file
        DC.Save_as_NC(Name_NC_Rivers, Rivers, 'Rivers', Example_dataset)

    ################################# Plot graph ##################################

    # Draw graph
    Five.Channel_Routing.Graph_DEM_Distance_Discharge(Name_NC_DEM, Name_NC_DEM_Dir, Name_NC_Acc_Pixels, Name_NC_Rivers, Name_NC_Routed_Discharge, Startdate, Enddate, Example_dataset)

    return()






















