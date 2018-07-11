# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Generator/Sheet4
"""
# import general modules
import os
import pandas as pd
import numpy as np
import csv

def Create(Dir_Basin, Simulation, Basin, Startdate, Enddate, nc_outname):
    """
    This functions create the CSV files for the sheets

    Parameters
    ----------
    Dir_Basin : str
        Path to all the output data of the Basin
    Simulation : int
        Defines the simulation
    Basin : str
        Name of the basin
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    nc_outname : str
        Path to the .nc file containing the data

    Returns
    -------
    Data_Path_CSV : str
        Data path pointing to the CSV output files

    """
    # import WA modules
    import wa.General.raster_conversions as RC
    import wa.Functions.Start as Start
    from wa.Functions import Start

    # Create output folder for CSV files
    Data_Path_CSV = os.path.join(Dir_Basin, "Simulations", "Simulation_%d" %Simulation, "CSV")
    if not os.path.exists(Data_Path_CSV):
        os.mkdir(Data_Path_CSV)

    # Open LULC map
    DataCube_LU = RC.Open_nc_array(nc_outname, 'Landuse')

    # Open all needed layers
    DataCube_Total_Supply_GW = RC.Open_nc_array(nc_outname, "Total_Supply_Ground_Water", Startdate, Enddate)
    DataCube_Total_Supply_SW = RC.Open_nc_array(nc_outname, "Total_Supply_Surface_Water", Startdate, Enddate)
    DataCube_Consumed_ET = RC.Open_nc_array(nc_outname, "Total_Supply", Startdate, Enddate)
    DataCube_Non_Consumed = RC.Open_nc_array(nc_outname, "Non_Consumed_Water", Startdate, Enddate)
    DataCube_RecovableFlow_Return_GW = RC.Open_nc_array(nc_outname, "Recovable_Flow_Ground_Water", Startdate, Enddate)
    DataCube_RecovableFlow_Return_SW = RC.Open_nc_array(nc_outname,"Recovable_Flow_Surface_Water", Startdate, Enddate)
    DataCube_NonRecovableFlow_Return_GW = RC.Open_nc_array(nc_outname, "Non_Recovable_Flow_Ground_Water" , Startdate, Enddate)
    DataCube_NonRecovableFlow_Return_SW = RC.Open_nc_array(nc_outname, "Non_Recovable_Flow_Surface_Water", Startdate, Enddate)

    # Set the months
    Dates = pd.date_range(Startdate, Enddate, freq = "MS")

    # Define whole years
    YearsStart = pd.date_range(Startdate, Enddate, freq = "AS")
    YearsEnd = pd.date_range(Startdate, Enddate, freq = "A")
    if len(YearsStart) > 0 and len(YearsEnd) > 0:
        Years = range(int(YearsStart[0].year), int(YearsEnd[-1].year + 1))
        Start_Year = np.argwhere(str(YearsStart[0])[0:10]==Dates)[0][0]
    else:
        Years = []

    # Calculate the area for each pixel in square meters
    area_in_m2 = Start.Area_converter.Degrees_to_m2(nc_outname)

     # Get all the LULC types that are defined for sheet 4
    LU_Classes = Start.Get_Dictionaries.get_sheet5_classes()
    LU_Classes_Keys = LU_Classes.keys()
    Required_LU_Classes = np.append(LU_Classes_Keys,['Industry','Power and Energy'])

    # Convert data from mm/month to km3/month
    Total_Supply_GW_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_Total_Supply_GW)/ 1e12
    Total_Supply_SW_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_Total_Supply_SW)/ 1e12
    Non_Consumed_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_Non_Consumed)/ 1e12
    Consumed_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_Consumed_ET)/ 1e12
    RecovableFlow_Return_GW_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_RecovableFlow_Return_GW)/ 1e12
    RecovableFlow_Return_SW_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_RecovableFlow_Return_SW)/ 1e12
    NonRecovableFlow_Return_GW_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_NonRecovableFlow_Return_GW)/ 1e12
    NonRecovableFlow_Return_SW_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_NonRecovableFlow_Return_SW)/ 1e12

    # Create mask for all LU classes
    All_mask = dict()

    # Create masks
    for Required_LU_Class in Required_LU_Classes[:-2]:
        Mask_Class = np.zeros(DataCube_LU.shape)
        Values_LULC = LU_Classes[Required_LU_Class]
        for Value_LULC in Values_LULC:
            Mask_Class[DataCube_LU == Value_LULC] = 1

        All_mask[Required_LU_Class] = Mask_Class

    # Enter additional map for industry and power and energy
    All_mask['Industry'] = np.zeros(DataCube_LU.shape)
    All_mask['Power and Energy'] = np.zeros(DataCube_LU.shape)

    # Create empty arrays for the values
    Values_Total_Supply_GW_km3 = np.zeros([len(Required_LU_Classes),len(Dates)])
    Values_Total_Supply_SW_km3 = np.zeros([len(Required_LU_Classes),len(Dates)])
    Values_Non_Consumed_km3 = np.zeros([len(Required_LU_Classes),len(Dates)])
    Values_Consumed_km3 = np.zeros([len(Required_LU_Classes),len(Dates)])
    Values_RecovableFlow_Return_GW_km3 = np.zeros([len(Required_LU_Classes),len(Dates)])
    Values_RecovableFlow_Return_SW_km3 = np.zeros([len(Required_LU_Classes),len(Dates)])
    Values_NonRecovableFlow_Return_GW_km3 = np.zeros([len(Required_LU_Classes),len(Dates)])
    Values_NonRecovableFlow_Return_SW_km3 = np.zeros([len(Required_LU_Classes),len(Dates)])

    # zero values for now
    Values_Consumed_Others = np.zeros([len(Required_LU_Classes),len(Dates)])
    Values_Demand = np.zeros([len(Required_LU_Classes),len(Dates)])

    i = 0
    Max_value = 0

    # Calculate sum by applying mask over the data
    for Required_LU_Class in Required_LU_Classes:
        Mask_one_class = All_mask[Required_LU_Class]
        Values_Total_Supply_GW_km3[i,:] = np.nansum(np.nansum(Total_Supply_GW_km3 * Mask_one_class,2),1)
        Values_Total_Supply_SW_km3[i,:] = np.nansum(np.nansum(Total_Supply_SW_km3 * Mask_one_class,2),1)
        Values_Non_Consumed_km3[i,:] = np.nansum(np.nansum(Non_Consumed_km3 * Mask_one_class,2),1)
        Values_Consumed_km3[i,:] = np.nansum(np.nansum(Consumed_km3 * Mask_one_class,2),1)
        Values_RecovableFlow_Return_GW_km3[i,:] = np.nansum(np.nansum(RecovableFlow_Return_GW_km3 * Mask_one_class,2),1)
        Values_RecovableFlow_Return_SW_km3[i,:] = np.nansum(np.nansum(RecovableFlow_Return_SW_km3 * Mask_one_class,2),1)
        Values_NonRecovableFlow_Return_GW_km3[i,:] = np.nansum(np.nansum(NonRecovableFlow_Return_GW_km3 * Mask_one_class,2),1)
        Values_NonRecovableFlow_Return_SW_km3[i,:] = np.nansum(np.nansum(NonRecovableFlow_Return_SW_km3 * Mask_one_class,2),1)
        i += 1

        Max_value_one_LU = np.nanmax(np.nanmax(Values_Total_Supply_GW_km3+Values_Total_Supply_SW_km3))

        if Max_value_one_LU > Max_value:
            Max_value = Max_value_one_LU

    # Check if scaling is needed
    scaling = 1
    Max_value_str = str(Max_value)
    Values = Max_value_str.split('.')
    if int(Values[0]) > 10:
        exponent = len(Values[0])-1
        scaling = float(np.power(10.,-1.*exponent))
    if int(Values[0]) == 0:
        Values_all = Values[1].split('0')
        exponent = 1
        Values_now = Values_all[0]
        while len(Values_now) == 0:
            exponent += 1
            Values_now = Values_all[exponent - 1]

        scaling = np.power(10,exponent)

    if scaling is not 1:
        Unit_front = '1x10^%d ' %(-1 * exponent)
    else:
        Unit_front = ''

    # Create CSV

    # First row of the CSV file
    first_row = ['LANDUSE_TYPE','SUPPLY_GROUNDWATER','NON_RECOVERABLE_GROUNDWATER','SUPPLY_SURFACEWATER','NON_CONVENTIONAL_ET','RECOVERABLE_GROUNDWATER','CONSUMED_OTHER','CONSUMED_ET','DEMAND','RECOVERABLE_SURFACEWATER','NON_RECOVERABLE_SURFACEWATER']

    # Counter for dates
    i = 0

    # Create monthly CSV
    for Date in Dates:

        # Create csv-file.
        csv_filename = os.path.join(Data_Path_CSV, 'Sheet4_Sim%d_%s_%d_%02d.csv' %(Simulation, Basin, Date.year, Date.month))
        csv_file = open(csv_filename, 'wb')
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(first_row)

        # Counter for landuse types
        j = 0

        # Loop over landuse and class
        for LAND_USE in Required_LU_Classes:

            # Get the value of the current class and landuse
            Value_Total_Supply_GW_km3 = Values_Total_Supply_GW_km3[j,i] * scaling
            Value_Total_Supply_SW_km3 = Values_Total_Supply_SW_km3[j,i] * scaling
            Value_Non_Consumed_km3 = Values_Non_Consumed_km3[j,i] * scaling
            Value_Consumed_km3 = Values_Consumed_km3[j,i] * scaling
            Value_RecovableFlow_Return_GW_km3 = Values_RecovableFlow_Return_GW_km3[j,i] * scaling
            Value_RecovableFlow_Return_SW_km3 = Values_RecovableFlow_Return_SW_km3[j,i] * scaling
            Value_NonRecovableFlow_Return_GW_km3 = Values_NonRecovableFlow_Return_GW_km3[j,i] * scaling
            Value_NonRecovableFlow_Return_SW_km3 = Values_NonRecovableFlow_Return_SW_km3[j,i] * scaling
            Value_Consumed_Others = Values_Consumed_Others[j,i] * scaling
            Value_Demand = Values_Demand[j,i] * scaling

            # Set special cases.
            # not defined yet

            # Create the row to be written
            row = [LAND_USE, "{0:.2f}".format(np.nansum([0, Value_Total_Supply_GW_km3])), "{0:.2f}".format(np.nansum([0, Value_NonRecovableFlow_Return_GW_km3])), "{0:.2f}".format(np.nansum([0, Value_Total_Supply_SW_km3])), "{0:.2f}".format(np.nansum([0, Value_Non_Consumed_km3])), "{0:.2f}".format(np.nansum([0, Value_RecovableFlow_Return_GW_km3])), "{0:.2f}".format(np.nansum([0, Value_Consumed_Others])), "{0:.2f}".format(np.nansum([0, Value_Consumed_km3])), "{0:.2f}".format(np.nansum([0, Value_Demand])), "{0:.2f}".format(np.nansum([0, Value_RecovableFlow_Return_SW_km3])), "{0:.2f}".format(np.nansum([0, Value_NonRecovableFlow_Return_SW_km3]))]

            # Write the row.
            writer.writerow(row)

            # Add one LU counter
            j += 1

        # Close the csv-file.
        csv_file.close()

        # Add one date counter
        i += 1

    # Create yearly CSV
    i = 0
    for Year in Years:

        # Create csv-file.
        csv_filename = os.path.join(Data_Path_CSV, 'Sheet4_Sim%d_%s_%d.csv' %(Simulation, Basin, Year))
        csv_file = open(csv_filename, 'wb')
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(first_row)

        j = 0

        # Loop over landuse and class
        for LAND_USE in Required_LU_Classes:

            # Get the value of the current class and landuse
            Value_Total_Supply_GW_km3 = np.sum(Values_Total_Supply_GW_km3[j,Start_Year:Start_Year+12]) * scaling
            Value_Total_Supply_SW_km3 = np.sum(Values_Total_Supply_SW_km3[j,Start_Year:Start_Year+12]) * scaling
            Value_Non_Consumed_km3 = np.sum(Values_Non_Consumed_km3[j,Start_Year:Start_Year+12]) * scaling
            Value_Consumed_km3 = np.sum(Values_Consumed_km3[j,Start_Year:Start_Year+12]) * scaling
            Value_RecovableFlow_Return_GW_km3 = np.sum(Values_RecovableFlow_Return_GW_km3[j,Start_Year:Start_Year+12]) * scaling
            Value_RecovableFlow_Return_SW_km3 = np.sum(Values_RecovableFlow_Return_SW_km3[j,Start_Year:Start_Year+12]) * scaling
            Value_NonRecovableFlow_Return_GW_km3 = np.sum(Values_NonRecovableFlow_Return_GW_km3[j,Start_Year:Start_Year+12]) * scaling
            Value_NonRecovableFlow_Return_SW_km3 = np.sum(Values_NonRecovableFlow_Return_SW_km3[j,Start_Year:Start_Year+12]) * scaling
            Value_Consumed_Others = np.sum(Values_Consumed_Others[j,Start_Year:Start_Year+12]) * scaling
            Value_Demand = np.sum(Values_Demand[j,Start_Year:Start_Year+12]) * scaling

            # Set special cases.
            # not defined yet

            # Create the row to be written
            row = [LAND_USE, "{0:.2f}".format(np.nansum([0, Value_Total_Supply_GW_km3])), "{0:.2f}".format(np.nansum([0, Value_NonRecovableFlow_Return_GW_km3])), "{0:.2f}".format(np.nansum([0, Value_Total_Supply_SW_km3])), "{0:.2f}".format(np.nansum([0, Value_Non_Consumed_km3])), "{0:.2f}".format(np.nansum([0, Value_RecovableFlow_Return_GW_km3])), "{0:.2f}".format(np.nansum([0, Value_Consumed_Others])), "{0:.2f}".format(np.nansum([0, Value_Consumed_km3])), "{0:.2f}".format(np.nansum([0, Value_Demand])), "{0:.2f}".format(np.nansum([0, Value_RecovableFlow_Return_SW_km3])), "{0:.2f}".format(np.nansum([0, Value_NonRecovableFlow_Return_SW_km3]))]

            # Write the row.
            writer.writerow(row)

            # Add one LU counter
            j += 1

        # Close the csv-file.
        csv_file.close()
        i += 1
        Start_Year += 12

    return(Data_Path_CSV, Unit_front)