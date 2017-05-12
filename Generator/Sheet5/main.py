# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 10:07:52 2017

@author: tih
"""
import os
import gdal
import numpy as np
import pandas as pd

from wa.General import raster_conversions as RC
from wa.General import data_conversions as DC
import wa.Functions.Five as Five
import wa.Functions.Start as Start

def Calculate(Basin, P_Product, ET_Product, Inflow_Text_Files, Startdate, Enddate, Simulation):

    ######################### Set General Parameters ##############################

    # Get environmental variable for the Home folder
    WA_env_paths = os.environ["WA_HOME"].split(';')
    Dir_Home = WA_env_paths[0]
	
    # Create the Basin folder
    Dir_Basin = os.path.join(Dir_Home, Basin)
    if not os.path.exists(Dir_Basin):
        os.makedirs(Dir_Basin)	

    # Get the boundaries of the basin based on the shapefile of the watershed
    # Boundaries, Shape_file_name_shp = Start.Boundaries.Determine(Basin)
    Boundaries, LU_dataset = Start.Boundaries.Determine_LU_Based(Basin)
    LU_data = RC.Open_tiff_array(LU_dataset)
    
    # Define resolution of SRTM
    Resolution = '15s'

    ############################# Download Data ###################################

    # Download data
    Data_Path_P = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, P_Product) 
    Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, ET_Product)
    Data_Path_DEM = Start.Download_Data.DEM(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution) 
    if Resolution is not '3s':
        Data_Path_DEM = Start.Download_Data.DEM(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution) 
    Data_Path_DEM_Dir = Start.Download_Data.DEM_Dir(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution) 
    Data_Path_ETref = Start.Download_Data.ETreference(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate) 
    Data_Path_JRC_occurrence = Start.Download_Data.JRC_occurrence(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']]) 

    ###################### Save Data as netCDF files ##############################

    #_____________________________________DEM__________________________________
    # Get the data of DEM and save as nc, This dataset is also used as reference for others
    Example_dataset = os.path.join(Dir_Basin, Data_Path_DEM, 'DEM_HydroShed_m_%s.tif' %Resolution)
    DEMdest = gdal.Open(Example_dataset)
    Xsize_CR = int(DEMdest.RasterXSize)
    Ysize_CR = int(DEMdest.RasterYSize)  
    DataCube_DEM_CR = DEMdest.GetRasterBand(1).ReadAsArray()

    Name_NC_DEM_CR = DC.Create_NC_name('DEM_CR', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_DEM_CR):
        DC.Save_as_NC(Name_NC_DEM_CR, DataCube_DEM_CR, 'DEM_CR', Example_dataset)
    DEMdest = None
    del DataCube_DEM_CR

    #___________________________________DEM Dir________________________________
    # Get the data of flow direction and save as nc.
    Dir_dataset = os.path.join(Dir_Basin, Data_Path_DEM_Dir, 'DIR_HydroShed_-_%s.tif' %Resolution)
    DEMDirdest = gdal.Open(Dir_dataset)
    DataCube_DEM_Dir_CR = DEMDirdest.GetRasterBand(1).ReadAsArray()

    Name_NC_DEM_Dir_CR = DC.Create_NC_name('DEM_Dir_CR', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_DEM_Dir_CR):
        DC.Save_as_NC(Name_NC_DEM_Dir_CR, DataCube_DEM_Dir_CR, 'DEM_Dir_CR', Example_dataset)
    DEMDirdest = None
    del DataCube_DEM_Dir_CR

    #______________________________ Precipitation______________________________
    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    # Precipitation data
    Name_NC_Prec_CR = DC.Create_NC_name('Prec_CR', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_Prec_CR):
	
        # Get the data of Precipitation and save as nc
        DataCube_Prec_CR = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_P, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_Prec_CR, DataCube_Prec_CR, 'Prec_CR', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_Prec_CR

    #____________________________ Evapotranspiration___________________________
    # Evapotranspiration data
    Name_NC_ET_CR = DC.Create_NC_name('ET_CR', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_ET_CR):

        # Get the data of Evaporation and save as nc
        DataCube_ET_CR = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ET, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ET_CR, DataCube_ET_CR, 'ET_CR', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ET_CR

    #_______________________Reference Evapotranspiration_______________________
    # Reference Evapotranspiration data
    Name_NC_ETref_CR = DC.Create_NC_name('ETref_CR', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_ETref_CR):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_ETref_CR = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ETref, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ETref_CR, DataCube_ETref_CR, 'ETref_CR', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ETref_CR

    ##################### Rasterize the basin shapefile ###########################
    
    #_____________________________________LU___________________________________
    destLU = RC.reproject_dataset_example(LU_dataset, Example_dataset, method=1)
    DataCube_LU_CR = destLU.GetRasterBand(1).ReadAsArray() 	   
    
    Raster_Basin_CR = np.zeros([Ysize_CR, Xsize_CR])
    Raster_Basin_CR[DataCube_LU_CR > 0] = 1
    Name_NC_Basin_CR = DC.Create_NC_name('Basin_CR', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_Basin_CR):
        DC.Save_as_NC(Name_NC_Basin_CR, Raster_Basin_CR, 'Basin_CR', Example_dataset)
        #del Raster_Basin

    '''
    Name_NC_Basin = DC.Create_NC_name('Basin_CR', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_Basin):

        Raster_Basin = RC.Vector_to_Raster(Dir_Basin, Shape_file_name_shp, Example_dataset)
        Raster_Basin = np.clip(Raster_Basin, 0, 1)
        DC.Save_as_NC(Name_NC_Basin, Raster_Basin, 'Basin_CR', Example_dataset)
        #del Raster_Basin
    '''
    ###################### Calculate Runoff with Budyko ###########################

    Name_NC_Runoff_CR = DC.Create_NC_name('Runoff_CR', Simulation, Dir_Basin, info)
    Name_NC_Runoff_for_Routing_CR = Name_NC_Runoff_CR
    if not os.path.exists(Name_NC_Runoff_CR):

        DataCube_Runoff_CR = Five.Budyko.Calc_runoff(Name_NC_ETref_CR, Name_NC_Prec_CR)
        DC.Save_as_NC(Name_NC_Runoff_CR, DataCube_Runoff_CR, 'Runoff_CR', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_Runoff_CR
        
    '''  
    ###################### Calculate Runoff with P min ET ###########################
  
    Name_NC_Runoff_CR = DC.Create_NC_name('Runoff_CR', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_Runoff_CR):

        ET = RC.Open_nc_array(Name_NC_ET_CR)
        P = RC.Open_nc_array(Name_NC_Prec_CR) 
        DataCube_Runoff_CR = P - ET
        DataCube_Runoff_CR[:,:,:][DataCube_Runoff_CR<=0.1] = 0
        DataCube_Runoff_CR[:,:,:][np.isnan(DataCube_Runoff_CR)] = 0                          
        DC.Save_as_NC(Name_NC_Runoff_CR, DataCube_Runoff_CR, 'Runoff_CR', Example_dataset, Startdate, Enddate, 'monthly')
        del DataCube_Runoff_CR

     '''      
    ############### Add inflow in basin by using textfile #########################       
    
    if len(Inflow_Text_Files) > 0:
        Name_NC_Runoff_with_Inlets_CR = DC.Create_NC_name('Runoff_with_Inlets_CR', Simulation, Dir_Basin, info)
        Name_NC_Runoff_for_Routing_CR = Name_NC_Runoff_with_Inlets_CR

        if not os.path.exists(Name_NC_Runoff_with_Inlets_CR):       
            DataCube_Runoff_with_Inlets_CR = Five.Inlets.Add_Inlets(Name_NC_Runoff_CR, Inflow_Text_Files)
            DC.Save_as_NC(Name_NC_Runoff_with_Inlets_CR, DataCube_Runoff_with_Inlets_CR, 'Runoff_with_Inlets_CR', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
            del DataCube_Runoff_with_Inlets_CR

    ######################### Apply Channel Routing ###############################

    info = ['monthly','pixels', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_NC_Acc_Pixels_CR = DC.Create_NC_name('Acc_Pixels_CR', Simulation, Dir_Basin)
    info = ['monthly','m3', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_NC_Routed_Discharge_CR = DC.Create_NC_name('Routed_Discharge_CR', Simulation, Dir_Basin, info)

    if not (os.path.exists(Name_NC_Acc_Pixels_CR) and os.path.exists(Name_NC_Routed_Discharge_CR)):
        Accumulated_Pixels_CR, Routed_Discharge_CR = Five.Channel_Routing.Channel_Routing(Name_NC_DEM_Dir_CR, Name_NC_Runoff_for_Routing_CR, Name_NC_Basin_CR, Example_dataset, Degrees = 1)

        # Save Results
        DC.Save_as_NC(Name_NC_Acc_Pixels_CR, Accumulated_Pixels_CR, 'Acc_Pixels_CR', Example_dataset)
        DC.Save_as_NC(Name_NC_Routed_Discharge_CR, Routed_Discharge_CR, 'Routed_Discharge_CR', Example_dataset, Startdate, Enddate, 'monthly')

    ################# Calculate the natural river and river zones #################
    
    Name_NC_Rivers_CR = DC.Create_NC_name('Rivers_CR', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_Rivers_CR):

        # Open routed discharge array
        Routed_Discharge_CR = RC.Open_nc_array(Name_NC_Routed_Discharge_CR)
        Raster_Basin = RC.Open_nc_array(Name_NC_Basin_CR)

        # Calculate mean average over the period
        Routed_Discharge_Ave = np.nanmean(Routed_Discharge_CR, axis=0)

        # Define the 2% highest pixels as rivers
        Rivers = np.zeros([np.size(Routed_Discharge_Ave,0),np.size(Routed_Discharge_Ave,1)])
        Routed_Discharge_Ave[Raster_Basin != 1] = np.nan
        Routed_Discharge_Ave_number = np.nanpercentile(Routed_Discharge_Ave,98)
        Rivers[Routed_Discharge_Ave > Routed_Discharge_Ave_number] = 1  # if yearly average is larger than 5000km3/month that it is a river

        # Save the river file as netcdf file
        DC.Save_as_NC(Name_NC_Rivers_CR, Rivers, 'Rivers_CR', Example_dataset)

    ########################## Create river directories ###########################  

    Amount_months = len(pd.date_range(Startdate,Enddate,freq='MS'))
    Amount_months_reservoirs = Amount_months + 1

    # Get river and DEM dict
    River_dict, DEM_dict, Distance_dict = Five.Create_Dict.Rivers_General(Name_NC_DEM_CR, Name_NC_DEM_Dir_CR, Name_NC_Acc_Pixels_CR, Name_NC_Rivers_CR, Example_dataset)

    # Get discharge dict
    Discharge_dict = Five.Create_Dict.Discharge(Name_NC_Routed_Discharge_CR, River_dict, Amount_months, Example_dataset)

    ###################### Calculate surface water storage characteristics ######################  
      
    # define input tiffs for surface water calculations 
    input_JRC = os.path.join(Dir_Basin, Data_Path_JRC_occurrence, 'JRC_Occurrence_percent.tif')
    DEM_dataset = os.path.join(Dir_Basin, Data_Path_DEM, 'DEM_HydroShed_m_3s.tif')
    
    sensitivity = 700 # 900 is less sensitive 1 is very sensitive
    Regions = Five.Reservoirs.Calc_Regions(Name_NC_Basin_CR, input_JRC, sensitivity, Boundaries)
    
    Diff_Water_Volume = np.zeros([len(Regions), Amount_months_reservoirs -1, 3])
    reservoir=0
    
    for region in Regions:

        popt = Five.Reservoirs.Find_Area_Volume_Relation(region, input_JRC, DEM_dataset)

        Area_Reservoir_Values = Five.Reservoirs.GEE_calc_reservoir_area(region, Startdate, Enddate)
        
        Diff_Water_Volume[reservoir,:,:] = Five.Reservoirs.Calc_Diff_Storage(Area_Reservoir_Values, popt)
        reservoir+=1

    ################# Add storage reservoirs and change outflows ##################

    Discharge_dict, River_dict = Five.Reservoirs.Add_Reservoirs(Name_NC_Rivers_CR, Name_NC_Acc_Pixels_CR, Diff_Water_Volume, River_dict, Discharge_dict, Regions, Example_dataset)       
     
    # Create array again




    ################################# Plot graph ##################################

    # Draw graph
    Five.Channel_Routing.Graph_DEM_Distance_Discharge(Name_NC_DEM_CR, Name_NC_DEM_Dir_CR, Name_NC_Acc_Pixels_CR, Name_NC_Rivers_CR, Name_NC_Routed_Discharge_CR, Startdate, Enddate, Example_dataset)

    ######################## Change data to fit the LU data #######################

    # DEM
    Name_NC_DEM = DC.Create_NC_name('DEM', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_DEM):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_DEM_CR = RC.Open_nc_array(Name_NC_DEM_CR)
        DataCube_DEM = RC.resize_array_example(DataCube_DEM_CR, LU_data, method=1)
        DC.Save_as_NC(Name_NC_DEM, DataCube_DEM, 'DEM', LU_dataset)
        del DataCube_DEM

    # flow direction
    Name_NC_DEM_Dir = DC.Create_NC_name('DEM_Dir', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_DEM_Dir):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_DEM_Dir_CR = RC.Open_nc_array(Name_NC_DEM_Dir_CR)
        DataCube_DEM_Dir = RC.resize_array_example(DataCube_DEM_Dir_CR, LU_data, method=1)
        DC.Save_as_NC(Name_NC_DEM_Dir, DataCube_DEM_Dir, 'DEM_Dir', LU_dataset)
        del DataCube_DEM_Dir
        
    # Precipitation
    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_Prec = DC.Create_NC_name('Prec', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_Prec):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_Prec = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_P, Startdate, Enddate, LU_dataset)
        DC.Save_as_NC(Name_NC_Prec, DataCube_Prec, 'Prec', LU_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_Prec

    # Evapotranspiration
    Name_NC_ET = DC.Create_NC_name('ET', Simulation, Dir_Basin)
    if not os.path.exists(Name_NC_ET):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_ET = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ET, Startdate, Enddate, LU_dataset)
        DC.Save_as_NC(Name_NC_ET, DataCube_ET, 'ET', LU_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ET    
        
    # Reference Evapotranspiration data
    Name_NC_ETref = DC.Create_NC_name('ETref', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_ETref):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_ETref = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ETref, Startdate, Enddate, LU_dataset)
        DC.Save_as_NC(Name_NC_ETref, DataCube_ETref, 'ETref', LU_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ETref

    # Rivers
    Name_NC_Rivers = DC.Create_NC_name('Rivers', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_Rivers):

        # Get the data of Reference Evapotranspiration and save as nc
        Rivers_CR = RC.Open_nc_array(Name_NC_Rivers_CR)
        DataCube_Rivers = RC.resize_array_example(Rivers_CR, LU_data)
        DC.Save_as_NC(Name_NC_Rivers, DataCube_Rivers, 'Rivers', LU_dataset)
        del DataCube_Rivers, Rivers_CR

    # Discharge
    # Define info for the nc files
    info = ['monthly','m3', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_Routed_Discharge = DC.Create_NC_name('Routed_Discharge', Simulation, Dir_Basin, info)
    if not os.path.exists(Name_NC_Routed_Discharge):

        # Get the data of Reference Evapotranspiration and save as nc
        Routed_Discharge_CR = RC.Open_nc_array(Name_NC_Routed_Discharge_CR)
        DataCube_Routed_Discharge = RC.resize_array_example(Routed_Discharge_CR, LU_data)
        DC.Save_as_NC(Name_NC_Routed_Discharge, DataCube_Routed_Discharge, 'Routed_Discharge', LU_dataset, Startdate, Enddate, 'monthly')
        del DataCube_Routed_Discharge, Routed_Discharge_CR        
    
    return()






















