# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 10:07:52 2017

@author: tih
"""

def Calculate(Basin, P_Product, ET_Product, Inflow_Text_Files, WaterPIX_filename, Reservoirs_GEE_on_off, Supply_method, Startdate, Enddate, Simulation):
    '''
    This functions consists of the following sections:
    1. Set General Parameters
    2. Download Data
    3. Convert the RAW data to NETCDF files
    4. Create Mask based on LU map
    5. Calculate Runoff based on Budyko or WaterPIX
    6. Add inflow in Runoff
    7. Calculate River flow
       7.1  Route Runoff
       7.2  Add Reservoirs
       7.3  Add surface water withdrawals BlueET or WaterPIX
    ''' 
    # import General modules
    import os
    import gdal
    import numpy as np
    import pandas as pd
    import copy

    # import WA plus modules
    from wa.General import raster_conversions as RC
    from wa.General import data_conversions as DC
    import wa.Functions.Five as Five
    import wa.Functions.Start as Start
   
    ######################### 1. Set General Parameters ##############################

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
    geo_out_LU, proj_LU, size_X_LU, size_Y_LU = RC.Open_array_info(LU_dataset)
        
    # Define resolution of SRTM
    Resolution = '15s'
    
    # Get the amount of months
    Amount_months = len(pd.date_range(Startdate,Enddate,freq='MS'))
    Amount_months_reservoirs = Amount_months + 1

    # Startdate for moving window Budyko
    Startdate_2months_Timestamp = pd.Timestamp(Startdate) - pd.DateOffset(months=2)
    Startdate_2months = Startdate_2months_Timestamp.strftime('%Y-%m-%d')
    
    ############################# 2. Download Data ###################################

    # Download data
    Data_Path_P = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_2months, Enddate, P_Product) 
    Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_2months, Enddate, ET_Product)
    Data_Path_DEM = Start.Download_Data.DEM(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution) 
    if Resolution is not '3s':
        Data_Path_DEM = Start.Download_Data.DEM(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution) 
    Data_Path_DEM_Dir = Start.Download_Data.DEM_Dir(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution) 
    
    if (WaterPIX_filename == "" or Supply_method == "Fraction"):
        Data_Path_ETref = Start.Download_Data.ETreference(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_2months, Enddate) 
    if Reservoirs_GEE_on_off == 1:
        Data_Path_JRC_occurrence = Start.Download_Data.JRC_occurrence(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']]) 
    Data_Path_P_Monthly = os.path.join(Data_Path_P, 'Monthly')
    
    ###################### 3. Convert the RAW data to NETCDF files ##############################
    # The sequence of converting the data is:
    # DEM
    # DEM flow directions
    # Precipitation
    # Evapotranspiration
    # Reference Evapotranspiration 

    #_____________________________________DEM__________________________________
    # Get the data of DEM and save as nc, This dataset is also used as reference for others
    Example_dataset = os.path.join(Dir_Basin, Data_Path_DEM, 'DEM_HydroShed_m_%s.tif' %Resolution)
    DEMdest = gdal.Open(Example_dataset)
    Xsize_CR = int(DEMdest.RasterXSize)
    Ysize_CR = int(DEMdest.RasterYSize)  
    DataCube_DEM_CR = DEMdest.GetRasterBand(1).ReadAsArray()

    Name_NC_DEM_CR = DC.Create_NC_name('DEM_CR', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_DEM_CR):
        DC.Save_as_NC(Name_NC_DEM_CR, DataCube_DEM_CR, 'DEM_CR', Example_dataset)
    DEMdest = None

    #___________________________________DEM Dir________________________________
    # Get the data of flow direction and save as nc.
    Dir_dataset = os.path.join(Dir_Basin, Data_Path_DEM_Dir, 'DIR_HydroShed_-_%s.tif' %Resolution)
    DEMDirdest = gdal.Open(Dir_dataset)
    DataCube_DEM_Dir_CR = DEMDirdest.GetRasterBand(1).ReadAsArray()

    Name_NC_DEM_Dir_CR = DC.Create_NC_name('DEM_Dir_CR', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_DEM_Dir_CR):
        DC.Save_as_NC(Name_NC_DEM_Dir_CR, DataCube_DEM_Dir_CR, 'DEM_Dir_CR', Example_dataset)
    DEMDirdest = None
    del DataCube_DEM_Dir_CR

    #______________________________ Precipitation______________________________
    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate_2months[5:7], Startdate_2months[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    # Precipitation data
    Name_NC_Prec_CR = DC.Create_NC_name('Prec_CR', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_Prec_CR):
	
        # Get the data of Precipitation and save as nc
        DataCube_Prec_CR = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_P_Monthly, Startdate_2months, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_Prec_CR, DataCube_Prec_CR, 'Prec_CR', Example_dataset, Startdate_2months, Enddate, 'monthly', 0.01)
        del DataCube_Prec_CR

    #____________________________ Evapotranspiration___________________________
    # Evapotranspiration data
    info = ['monthly','mm', ''.join([Startdate_2months[5:7], Startdate_2months[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_NC_ET_CR = DC.Create_NC_name('ET_CR', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_ET_CR):

        # Get the data of Evaporation and save as nc
        DataCube_ET_CR = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ET, Startdate_2months, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ET_CR, DataCube_ET_CR, 'ET_CR', Example_dataset, Startdate_2months, Enddate, 'monthly', 0.01)
        del DataCube_ET_CR
    
    if (WaterPIX_filename == "" or Supply_method == "Fraction"):
        
        #_______________________Reference Evapotranspiration_______________________
        # Reference Evapotranspiration data
        Name_NC_ETref_CR = DC.Create_NC_name('ETref_CR', Simulation, Dir_Basin, 5, info)
        if not os.path.exists(Name_NC_ETref_CR):
    
            # Get the data of Reference Evapotranspiration and save as nc
            DataCube_ETref_CR = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ETref, Startdate_2months, Enddate, Example_data = Example_dataset)
            DC.Save_as_NC(Name_NC_ETref_CR, DataCube_ETref_CR, 'ETref_CR', Example_dataset, Startdate_2months, Enddate, 'monthly', 0.01)
            del DataCube_ETref_CR

    #_______________________fraction surface water _______________________
    if Supply_method == "Fraction":
        
        Name_NC_frac_sw_CR = DC.Create_NC_name('Fraction_SW_CR', Simulation, Dir_Basin, 5)
        if not os.path.exists(Name_NC_frac_sw_CR):
            DataCube_frac_sw = np.ones_like(LU_data) * np.nan
        
            import wa.Functions.Start.Get_Dictionaries as GD
            
            # Get dictionaries and keys
            lulc = GD.get_sheet5_classes()
            lulc_dict = GD.get_sheet5_classes().keys()
            consumed_frac_dict = GD.sw_supply_fractions()
    
            for key in lulc_dict:
                Numbers = lulc[key]
                for LU_nmbr in Numbers:
                    Mask = np.zeros_like(LU_data)
                    Mask[LU_data==LU_nmbr] = 1
                    DataCube_frac_sw[Mask == 1] = consumed_frac_dict[key]
        
            dest_frac_sw = DC.Save_as_MEM(DataCube_frac_sw, geo_out_LU, proj_LU)
            dest_frac_sw_CR = RC.reproject_dataset_example(dest_frac_sw, Example_dataset)
            DataCube_frac_sw_CR = dest_frac_sw_CR.ReadAsArray()
            DataCube_frac_sw_CR[DataCube_frac_sw_CR == 0] = np.nan
            
            DC.Save_as_NC(Name_NC_frac_sw_CR, DataCube_frac_sw_CR, 'Fraction_SW_CR', Example_dataset, Scaling_factor = 0.01)   
            del DataCube_frac_sw_CR
            
        del DataCube_DEM_CR
    ##################### 4. Create Mask based on LU map ###########################
    
    # Now a mask will be created to define the area of interest (pixels where there is a landuse defined)
    
    #_____________________________________LU___________________________________
    destLU = RC.reproject_dataset_example(LU_dataset, Example_dataset, method=1)
    DataCube_LU_CR = destLU.GetRasterBand(1).ReadAsArray() 	   
    
    Raster_Basin_CR = np.zeros([Ysize_CR, Xsize_CR])
    Raster_Basin_CR[DataCube_LU_CR > 0] = 1
    Name_NC_Basin_CR = DC.Create_NC_name('Basin_CR', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_Basin_CR):
        DC.Save_as_NC(Name_NC_Basin_CR, Raster_Basin_CR, 'Basin_CR', Example_dataset)
        #del Raster_Basin

    '''
    Name_NC_Basin = DC.Create_NC_name('Basin_CR', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_Basin):

        Raster_Basin = RC.Vector_to_Raster(Dir_Basin, Shape_file_name_shp, Example_dataset)
        Raster_Basin = np.clip(Raster_Basin, 0, 1)
        DC.Save_as_NC(Name_NC_Basin, Raster_Basin, 'Basin_CR', Example_dataset)
        #del Raster_Basin
    '''
    ################### 5. Calculate Runoff (2 methods: a = Budyko and b = WaterPIX) #####################    
    
    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    # Define the output names of section 5 and 6
    Name_NC_Runoff_CR = DC.Create_NC_name('Runoff_CR', Simulation, Dir_Basin, 5, info)
    Name_NC_Runoff_for_Routing_CR = Name_NC_Runoff_CR
    
    ###################### 5a. Calculate Runoff based on Budyko ###########################
    if WaterPIX_filename == "":
        
        if not os.path.exists(Name_NC_Runoff_CR):
            
            # Calculate runoff based on Budyko
            DataCube_Runoff_CR = Five.Budyko.Calc_runoff(Name_NC_ETref_CR, Name_NC_Prec_CR)
            
    ###################### 5b. Get Runoff from WaterPIX ###########################
    if WaterPIX_filename != "": 

        # Get WaterPIX data
        WaterPIX_Var = 'TotalRunoff_M'
        DataCube_Runoff_CR = Five.Read_WaterPIX.Get_Array(WaterPIX_filename, WaterPIX_Var, Example_dataset, Startdate, Enddate)
                  
              
    # Save the runoff as netcdf
    DC.Save_as_NC(Name_NC_Runoff_for_Routing_CR, DataCube_Runoff_CR, 'Runoff_CR', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
    del DataCube_Runoff_CR    
     
    '''  
    ###################### Calculate Runoff with P min ET ###########################
  
    Name_NC_Runoff_CR = DC.Create_NC_name('Runoff_CR', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_Runoff_CR):

        ET = RC.Open_nc_array(Name_NC_ET_CR)
        P = RC.Open_nc_array(Name_NC_Prec_CR) 
        DataCube_Runoff_CR = P - ET
        DataCube_Runoff_CR[:,:,:][DataCube_Runoff_CR<=0.1] = 0
        DataCube_Runoff_CR[:,:,:][np.isnan(DataCube_Runoff_CR)] = 0                          
        DC.Save_as_NC(Name_NC_Runoff_CR, DataCube_Runoff_CR, 'Runoff_CR', Example_dataset, Startdate, Enddate, 'monthly')
        del DataCube_Runoff_CR

     '''      
    ############### 6. Add inflow in basin by using textfile #########################       
    
    # add inlets if there are textfiles defined
    if len(Inflow_Text_Files) > 0:
        
        # Create name of the Runoff with inlets
        Name_NC_Runoff_with_Inlets_CR = DC.Create_NC_name('Runoff_with_Inlets_CR', Simulation, Dir_Basin, 5, info)
        
        # Use this runoff name for the routing (it will overwrite the runoff without inlets)
        Name_NC_Runoff_for_Routing_CR = Name_NC_Runoff_with_Inlets_CR
  
        # Create the file if it not exists
        if not os.path.exists(Name_NC_Runoff_with_Inlets_CR):      
            
            # Calculate the runoff that will be routed by including the inlets
            DataCube_Runoff_with_Inlets_CR = Five.Inlets.Add_Inlets(Name_NC_Runoff_CR, Inflow_Text_Files)
            
            # Save this runoff as netcdf
            DC.Save_as_NC(Name_NC_Runoff_with_Inlets_CR, DataCube_Runoff_with_Inlets_CR, 'Runoff_with_Inlets_CR', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
            del DataCube_Runoff_with_Inlets_CR

    ######################### 7. Now the surface water is calculated #################

    # Names for dicionaries and nc files
    # CR1 = Natural_flow with only green water
    # CR2 = Natural_flow with only green water and reservoirs
    # CR3 = Flow with green, blue and reservoirs

    ######################### 7.1 Apply Channel Routing ###############################

    # Create the name for the netcdf outputs for section 7.1
    info = ['monthly','pixels', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_NC_Acc_Pixels_CR = DC.Create_NC_name('Acc_Pixels_CR', Simulation, Dir_Basin, 5)
    info = ['monthly','m3', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_NC_Discharge_CR1 = DC.Create_NC_name('Discharge_CR1', Simulation, Dir_Basin, 5, info)

    # If one of the outputs does not exists, run this part
    if not (os.path.exists(Name_NC_Acc_Pixels_CR) and os.path.exists(Name_NC_Discharge_CR1)):

        Accumulated_Pixels_CR, Discharge_CR1 = Five.Channel_Routing.Channel_Routing(Name_NC_DEM_Dir_CR, Name_NC_Runoff_for_Routing_CR, Name_NC_Basin_CR, Example_dataset, Degrees = 1)

        # Save Results
        DC.Save_as_NC(Name_NC_Acc_Pixels_CR, Accumulated_Pixels_CR, 'Acc_Pixels_CR', Example_dataset)
        DC.Save_as_NC(Name_NC_Discharge_CR1, Discharge_CR1, 'Discharge_CR1', Example_dataset, Startdate, Enddate, 'monthly')

    ################# Calculate the natural river and river zones #################
    
    Name_NC_Rivers_CR = DC.Create_NC_name('Rivers_CR', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_Rivers_CR):

        # Open routed discharge array
        Discharge_CR1 = RC.Open_nc_array(Name_NC_Discharge_CR1)
        Raster_Basin = RC.Open_nc_array(Name_NC_Basin_CR)

        # Calculate mean average over the period
        if len(np.shape(Discharge_CR1))>2:
            Routed_Discharge_Ave = np.nanmean(Discharge_CR1, axis=0)
        else:
            Routed_Discharge_Ave = Discharge_CR1

        # Define the 2% highest pixels as rivers
        Rivers = np.zeros([np.size(Routed_Discharge_Ave,0),np.size(Routed_Discharge_Ave,1)])
        Routed_Discharge_Ave[Raster_Basin != 1] = np.nan
        Routed_Discharge_Ave_number = np.nanpercentile(Routed_Discharge_Ave,90)
        Rivers[Routed_Discharge_Ave > Routed_Discharge_Ave_number] = 1  # if yearly average is larger than 5000km3/month that it is a river

        # Save the river file as netcdf file
        DC.Save_as_NC(Name_NC_Rivers_CR, Rivers, 'Rivers_CR', Example_dataset)

    ########################## Create river directories ###########################  
    
    Name_py_River_dict_CR1 = os.path.join(Dir_Basin,'Simulations','Simulation_%d' %Simulation, 'Sheet_5','River_dict_CR1_simulation%d.npy' %(Simulation)) 
    Name_py_DEM_dict_CR1 = os.path.join(Dir_Basin,'Simulations','Simulation_%d' %Simulation, 'Sheet_5','DEM_dict_CR1_simulation%d.npy' %(Simulation))    
    Name_py_Distance_dict_CR1 = os.path.join(Dir_Basin,'Simulations','Simulation_%d' %Simulation, 'Sheet_5','Distance_dict_CR1_simulation%d.npy' %(Simulation))

    if not (os.path.exists(Name_py_River_dict_CR1) and os.path.exists(Name_py_DEM_dict_CR1) and os.path.exists(Name_py_Distance_dict_CR1)):

        # Get river and DEM dict
        River_dict_CR1, DEM_dict_CR1, Distance_dict_CR1 = Five.Create_Dict.Rivers_General(Name_NC_DEM_CR, Name_NC_DEM_Dir_CR, Name_NC_Acc_Pixels_CR, Name_NC_Rivers_CR, Example_dataset)
        np.save(Name_py_River_dict_CR1, River_dict_CR1) 
        np.save(Name_py_DEM_dict_CR1, DEM_dict_CR1) 
        np.save(Name_py_Distance_dict_CR1, Distance_dict_CR1) 
    else:
        # Load
        River_dict_CR1 = np.load(Name_py_River_dict_CR1).item()         
        DEM_dict_CR1 = np.load(Name_py_DEM_dict_CR1).item()  
        Distance_dict_CR1 = np.load(Name_py_Distance_dict_CR1).item()  
        
    Name_py_Discharge_dict_CR1 = os.path.join(Dir_Basin,'Simulations','Simulation_%d' %Simulation, 'Sheet_5','Discharge_dict_CR1_simulation%d.npy' %(Simulation))

    if not os.path.exists(Name_py_Discharge_dict_CR1):
        # Get discharge dict
        Discharge_dict_CR1 = Five.Create_Dict.Discharge(Name_NC_Discharge_CR1, River_dict_CR1, Amount_months, Example_dataset)
        np.save(Name_py_Discharge_dict_CR1, Discharge_dict_CR1) 
    else:
        # Load
        Discharge_dict_CR1 = np.load(Name_py_Discharge_dict_CR1).item() 
    
    ###################### 7.2 Calculate surface water storage characteristics ######################  

    # Define names
    Name_py_Discharge_dict_CR2 = os.path.join(Dir_Basin, 'Simulations', 'Simulation_%d' %Simulation, 'Sheet_5', 'Discharge_dict_CR2_simulation%d.npy' %(Simulation))    
    Name_py_River_dict_CR2 = os.path.join(Dir_Basin, 'Simulations', 'Simulation_%d' %Simulation, 'Sheet_5', 'River_dict_CR2_simulation%d.npy' %(Simulation))
    Name_py_DEM_dict_CR2 = os.path.join(Dir_Basin, 'Simulations', 'Simulation_%d' %Simulation, 'Sheet_5', 'DEM_dict_CR2_simulation%d.npy' %(Simulation))    
    Name_py_Distance_dict_CR2 = os.path.join(Dir_Basin, 'Simulations', 'Simulation_%d' %Simulation, 'Sheet_5', 'Distance_dict_CR2_simulation%d.npy' %(Simulation))
    
    if not (os.path.exists(Name_py_Discharge_dict_CR2) and os.path.exists(Name_py_River_dict_CR2) and os.path.exists(Name_py_DEM_dict_CR2) and os.path.exists(Name_py_Distance_dict_CR2)):      

        # Copy dicts as starting adding reservoir 
        Discharge_dict_CR2 = copy.deepcopy(Discharge_dict_CR1)
        River_dict_CR2 = copy.deepcopy(River_dict_CR1)
        DEM_dict_CR2 = copy.deepcopy(DEM_dict_CR1)
        Distance_dict_CR2 = copy.deepcopy(Distance_dict_CR1)
        
        # If reservoirs calculations needs to be included than calculate reservoir storage using GEE    
        if Reservoirs_GEE_on_off == 1:    
            
            # Define names for reservoirs calculations
            Name_py_Diff_Water_Volume =  os.path.join(Dir_Basin,'Simulations','Simulation_%d' %Simulation, 'Sheet_5','Diff_Water_Volume_CR2_simulation%d.npy' %(Simulation))
            Name_py_Regions =  os.path.join(Dir_Basin,'Simulations','Simulation_%d' %Simulation, 'Sheet_5','Regions_simulation%d.npy' %(Simulation))
        
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

            ################# 7.3 Add storage reservoirs and change outflows ##################
            Discharge_dict_CR2, River_dict_CR2, DEM_dict_CR2, Distance_dict_CR2 = Five.Reservoirs.Add_Reservoirs(Name_NC_Rivers_CR, Name_NC_Acc_Pixels_CR, Diff_Water_Volume, River_dict_CR2, Discharge_dict_CR2, DEM_dict_CR2, Distance_dict_CR2, Regions, Example_dataset)       
    
            np.save(Name_py_Regions, Regions)
            np.save(Name_py_Diff_Water_Volume, Diff_Water_Volume)
       
        # Save variables    
        np.save(Name_py_Discharge_dict_CR2, Discharge_dict_CR2)
        np.save(Name_py_River_dict_CR2, River_dict_CR2)
        np.save(Name_py_DEM_dict_CR2, DEM_dict_CR2)
        np.save(Name_py_Distance_dict_CR2, Distance_dict_CR2)
            
    else:
        
        # Load
        Discharge_dict_CR2 = np.load(Name_py_Discharge_dict_CR2).item() 
        River_dict_CR2 = np.load(Name_py_River_dict_CR2).item() 
        DEM_dict_CR2 = np.load(Name_py_DEM_dict_CR2).item() 
        Distance_dict_CR2 = np.load(Name_py_Distance_dict_CR2).item() 
          
    ####################### 7.3 Add surface water withdrawals ############################# 
   
    Name_py_Discharge_dict_CR3 = os.path.join(Dir_Basin,'Simulations','Simulation_%d' %Simulation, 'Sheet_5','Discharge_dict_CR3_simulation%d.npy' %(Simulation))    
    Name_NC_Supply = DC.Create_NC_name('Supply', Simulation, Dir_Basin, 5, info)
    Name_NC_ETblue =  DC.Create_NC_name('ETblue', Simulation, Dir_Basin, 5, info)

    if not os.path.exists(Name_py_Discharge_dict_CR3):

        if Supply_method == "Fraction":
            DataCube_Supply_m3, DataCube_ETblue_m3 = Five.Irrigation.Calc_Supply_Budyko(Discharge_dict_CR2, Name_NC_Rivers_CR, Name_NC_ET_CR, Name_NC_ETref_CR, Name_NC_Prec_CR, Name_NC_Basin_CR, Name_NC_frac_sw_CR, Startdate, Enddate, Example_dataset)
            DC.Save_as_NC(Name_NC_Supply, DataCube_Supply_m3, 'Supply', Example_dataset, Startdate, Enddate, 'monthly')
            DC.Save_as_NC(Name_NC_ETblue, DataCube_ETblue_m3, 'ETblue', Example_dataset, Startdate, Enddate, 'monthly') 
            del DataCube_ETblue_m3, DataCube_Supply_m3
            Discharge_dict_CR3 = Five.Irrigation.Add_irrigation(Discharge_dict_CR2, River_dict_CR2, Name_NC_Rivers_CR,  Name_NC_Supply, Name_NC_ETblue, Name_NC_Basin_CR, Startdate, Enddate, Example_dataset)
            np.save(Name_py_Discharge_dict_CR3, Discharge_dict_CR3)
            

        if Supply_method == "WaterPIX":
            
            # MOET NOG AFGEMAAKT WORDEN
            DataCube_Supply_m3 = 2
            Discharge_dict_CR3, DataCube_ETblue_m3 = Five.Irrigation.Add_irrigation(Discharge_dict_CR2, River_dict_CR2, Name_NC_Rivers_CR, Name_NC_ET_CR, Name_NC_ETref_CR, Name_NC_Prec_CR, Name_NC_Basin_CR, Name_NC_frac_sw_CR, Startdate, Enddate, Example_dataset)
            np.save(Name_py_Discharge_dict_CR3, Discharge_dict_CR3)

            # save ETblue as nc
            info = ['monthly','m3-month-1', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
            Name_NC_ETblue = DC.Create_NC_name('ETblue', Simulation, Dir_Basin, 5, info)
            DC.Save_as_NC(Name_NC_ETblue, DataCube_ETblue_m3, 'ETblue', Example_dataset, Startdate, Enddate, 'monthly')

    else:
        Discharge_dict_CR3 = np.load(Name_py_Discharge_dict_CR3).item() 
    
    ################################# Plot graph ##################################

    # Draw graph
    Five.Channel_Routing.Graph_DEM_Distance_Discharge(Discharge_dict_CR3, Distance_dict_CR2, DEM_dict_CR2, River_dict_CR2, Startdate, Enddate, Example_dataset)




    ######################## Change data to fit the LU data #######################

    # Discharge
    # Define info for the nc files
    info = ['monthly','m3-month-1', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_Discharge = DC.Create_NC_name('DischargeEnd', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_Discharge):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_Discharge_CR = DC.Convert_dict_to_array(Discharge_dict_CR3, Discharge_dict_CR3, Example_dataset)
        DC.Save_as_NC(Name_NC_Discharge, DataCube_Discharge_CR, 'Discharge_End_CR', Example_dataset, Startdate, Enddate, 'monthly')
        del DataCube_Discharge_CR       
   



    '''













    # DEM
    Name_NC_DEM = DC.Create_NC_name('DEM', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_DEM):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_DEM_CR = RC.Open_nc_array(Name_NC_DEM_CR)
        DataCube_DEM = RC.resize_array_example(DataCube_DEM_CR, LU_data, method=1)
        DC.Save_as_NC(Name_NC_DEM, DataCube_DEM, 'DEM', LU_dataset)
        del DataCube_DEM

    # flow direction
    Name_NC_DEM_Dir = DC.Create_NC_name('DEM_Dir', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_DEM_Dir):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_DEM_Dir_CR = RC.Open_nc_array(Name_NC_DEM_Dir_CR)
        DataCube_DEM_Dir = RC.resize_array_example(DataCube_DEM_Dir_CR, LU_data, method=1)
        DC.Save_as_NC(Name_NC_DEM_Dir, DataCube_DEM_Dir, 'DEM_Dir', LU_dataset)
        del DataCube_DEM_Dir
        
    # Precipitation
    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_Prec = DC.Create_NC_name('Prec', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_Prec):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_Prec = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_P_Monthly, Startdate, Enddate, LU_dataset)
        DC.Save_as_NC(Name_NC_Prec, DataCube_Prec, 'Prec', LU_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_Prec

    # Evapotranspiration
    Name_NC_ET = DC.Create_NC_name('ET', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_ET):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_ET = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ET, Startdate, Enddate, LU_dataset)
        DC.Save_as_NC(Name_NC_ET, DataCube_ET, 'ET', LU_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ET    
        
    # Reference Evapotranspiration data
    Name_NC_ETref = DC.Create_NC_name('ETref', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_ETref):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_ETref = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ETref, Startdate, Enddate, LU_dataset)
        DC.Save_as_NC(Name_NC_ETref, DataCube_ETref, 'ETref', LU_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ETref

    # Rivers
    Name_NC_Rivers = DC.Create_NC_name('Rivers', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_Rivers):

        # Get the data of Reference Evapotranspiration and save as nc
        Rivers_CR = RC.Open_nc_array(Name_NC_Rivers_CR)
        DataCube_Rivers = RC.resize_array_example(Rivers_CR, LU_data)
        DC.Save_as_NC(Name_NC_Rivers, DataCube_Rivers, 'Rivers', LU_dataset)
        del DataCube_Rivers, Rivers_CR

    # Discharge
    # Define info for the nc files
    info = ['monthly','m3', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_Routed_Discharge = DC.Create_NC_name('Routed_Discharge', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_Routed_Discharge):

        # Get the data of Reference Evapotranspiration and save as nc
        Routed_Discharge_CR = RC.Open_nc_array(Name_NC_Discharge)
        DataCube_Routed_Discharge = RC.resize_array_example(Routed_Discharge_CR, LU_data)
        DC.Save_as_NC(Name_NC_Routed_Discharge, DataCube_Routed_Discharge, 'Routed_Discharge', LU_dataset, Startdate, Enddate, 'monthly')
        del DataCube_Routed_Discharge, Routed_Discharge_CR        
 
    
    
    

    # Get raster information 
    geo_out, proj, size_X, size_Y = RC.Open_array_info(Example_dataset)
    
    Rivers = RC.Open_nc_array(Name_NC_Rivers_CR)
    
    # Create ID Matrix
    y,x = np.indices((size_Y, size_X))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y,size_X),mode='clip').reshape(x.shape)) + 1

    # Get tiff array time dimension:
    time_dimension = int(np.shape(Discharge_dict_CR3[0])[0])
    
    # create an empty array
    Result = np.zeros([time_dimension, size_Y, size_X])
 
    for river_part in range(0,len(River_dict_CR2)):
        for river_pixel in range(1,len(River_dict_CR2[river_part])):
            river_pixel_ID = River_dict_CR2[river_part][river_pixel]
            if len(np.argwhere(ID_Matrix == river_pixel_ID))>0:
                row, col = np.argwhere(ID_Matrix == river_pixel_ID)[0][:] 
                Result[:,row,col] = Discharge_dict_CR3[river_part][:,river_pixel]
        print(river_part)
     
        
    Outflow = Discharge_dict_CR3[0][:,1]   
        
    for i in range(0,time_dimension):    
        output_name = r'C:/testmap/rtest_%s.tif' %i
        Result_one = Result[i, :, :]
        DC.Save_as_tiff(output_name, Result_one, geo_out, "WGS84")       

    import os

    # Get environmental variable for the Home folder
    WA_env_paths = os.environ["WA_HOME"].split(';')
    Dir_Home = WA_env_paths[0]
	
    # Create the Basin folder
    Dir_Basin = os.path.join(Dir_Home, Basin)
    info = ['monthly','m3-month-1', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_Result = DC.Create_NC_name('DischargeEnd', Simulation, Dir_Basin, 5, info)
    Result[np.logical_and(Result == 0.0, Rivers == 0.0)] = np.nan
          
    DC.Save_as_NC(Name_Result, Result, 'DischargeEnd', Example_dataset, Startdate, Enddate, 'monthly')



    '''


    return()






















