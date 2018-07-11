# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Generator/Sheet2
"""
# import general modules
import os
import pandas as pd
import numpy as np
import csv

def Create(Dir_Basin, Simulation, Basin, Startdate, Enddate, nc_outname, Example_dataset):
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
        Path to the .nc file containing the  data
    Example_dataset : str
         Data path to the example tiff file containing the right amount of pixels and projection

    Returns
    -------
    Data_Path_CSV : str
        Data path pointing to the CSV output files

    """
    # import WA modules
    import wa.Functions.Start.Get_Dictionaries as GD
    import wa.General.raster_conversions as RC
    from wa.Functions import Start

    # Create output folder for CSV files
    Data_Path_CSV = os.path.join(Dir_Basin, "Simulations", "Simulation_%d" %Simulation, "CSV")
    if not os.path.exists(Data_Path_CSV):
        os.mkdir(Data_Path_CSV)

    # Open LULC map
    LULC = RC.Open_nc_array(nc_outname, 'Landuse')

    # Open I, T, E
    DataCube_I = RC.Open_nc_array(nc_outname, 'Interception', Startdate, Enddate)
    DataCube_T = RC.Open_nc_array(nc_outname, 'Transpiration', Startdate, Enddate)
    DataCube_E = RC.Open_nc_array(nc_outname, 'Evaporation', Startdate, Enddate)

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
    area_in_m2 = Start.Area_converter.Degrees_to_m2(Example_dataset)

    # Create Beneficial Maps
    lulc_dict = GD.get_lulcs()

    # Get all the LULC values
    Values_LULC = np.unique(LULC)

    # Create new Benefial arrays
    T_ben_array = np.zeros(np.shape(LULC))
    E_ben_array = np.zeros(np.shape(LULC))
    I_ben_array = np.zeros(np.shape(LULC))
    agriculture_array = np.zeros(np.shape(LULC))
    environment_array= np.zeros(np.shape(LULC))
    economic_array = np.zeros(np.shape(LULC))
    energy_array = np.zeros(np.shape(LULC))
    leisure_array = np.zeros(np.shape(LULC))

    # Loop over LULC values and set benefial fractions
    for Value_LULC in Values_LULC:
        if Value_LULC in lulc_dict.keys():
            T_ben = lulc_dict[Value_LULC][3]
            E_ben = lulc_dict[Value_LULC][4]
            I_ben = lulc_dict[Value_LULC][5]
            agriculture = lulc_dict[Value_LULC][6]
            environment = lulc_dict[Value_LULC][7]
            economic = lulc_dict[Value_LULC][8]
            energy = lulc_dict[Value_LULC][9]
            leisure = lulc_dict[Value_LULC][10]

            T_ben_array[LULC == Value_LULC] = T_ben/100.
            E_ben_array[LULC == Value_LULC] = E_ben/100.
            I_ben_array[LULC == Value_LULC] = I_ben/100.
            agriculture_array[LULC == Value_LULC] = agriculture/100.
            environment_array[LULC == Value_LULC] = environment/100.
            economic_array[LULC == Value_LULC] = economic /100.
            energy_array[LULC == Value_LULC] = energy/100.
            leisure_array[LULC == Value_LULC] = leisure /100.

    # Open sheet 2 dict
    sheet2_classes_dict = GD.get_sheet2_classes()

    # Convert data from mm/month to km3/month
    I_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_I)/ 1e12
    E_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_E)/ 1e12
    T_km3 = np.einsum('ij,kij->kij', area_in_m2, DataCube_T)/ 1e12

    # Calculate beneficial I, E, and T
    Iben_km3 = np.einsum('ij,kij->kij', I_ben_array, I_km3)
    Eben_km3 = np.einsum('ij,kij->kij', E_ben_array, E_km3)
    Tben_km3 = np.einsum('ij,kij->kij', T_ben_array, T_km3)
    ETben_tot_km3 = Iben_km3 + Eben_km3 + Tben_km3

    # Determine service contribution
    agriculture_km3 = np.einsum('ij,kij->kij', agriculture_array, ETben_tot_km3)
    environment_km3 = np.einsum('ij,kij->kij', environment_array, ETben_tot_km3)
    economic_km3 = np.einsum('ij,kij->kij', economic_array, ETben_tot_km3)
    energy_km3 = np.einsum('ij,kij->kij', energy_array, ETben_tot_km3)
    leisure_km3 = np.einsum('ij,kij->kij', leisure_array, ETben_tot_km3)


    # Create empty arrays
    DataT = np.zeros([29,len(Dates)])
    DataI = np.zeros([29,len(Dates)])
    DataE = np.zeros([29,len(Dates)])
    DataBT = np.zeros([29,len(Dates)])
    DataBI = np.zeros([29,len(Dates)])
    DataBE = np.zeros([29,len(Dates)])
    DataAgriculture = np.zeros([29,len(Dates)])
    DataEnvironment = np.zeros([29,len(Dates)])
    DataEconomic = np.zeros([29,len(Dates)])
    DataEnergy = np.zeros([29,len(Dates)])
    DataLeisure = np.zeros([29,len(Dates)])
    i = 0

    # Loop over the LULC by using the Sheet 2 dictionary
    for LAND_USE in sheet2_classes_dict.keys():
        for CLASS in sheet2_classes_dict[LAND_USE].keys():
            lulcs = sheet2_classes_dict[LAND_USE][CLASS]

            # Create a mask to ignore non relevant pixels.
            mask=np.logical_or.reduce([LULC == value for value in lulcs])
            mask3d = mask * np.ones(len(Dates))[:,None,None]

            # Calculate the spatial sum of the different parameters.
            T_LU_tot = np.nansum(np.nansum((T_km3 * mask3d),1),1)
            I_LU_tot = np.nansum(np.nansum((I_km3 * mask3d),1),1)
            E_LU_tot = np.nansum(np.nansum((E_km3 * mask3d),1),1)
            BT_LU_tot = np.nansum(np.nansum((Tben_km3 * mask3d),1),1)
            BI_LU_tot = np.nansum(np.nansum((Iben_km3 * mask3d),1),1)
            BE_LU_tot = np.nansum(np.nansum((Eben_km3 * mask3d),1),1)
            Agriculture_LU_tot = np.nansum(np.nansum((agriculture_km3 * mask3d),1),1)
            Environment_LU_tot = np.nansum(np.nansum((environment_km3 * mask3d),1),1)
            Economic_LU_tot = np.nansum(np.nansum((economic_km3 * mask3d),1),1)
            Energy_LU_tot = np.nansum(np.nansum((energy_km3 * mask3d),1),1)
            Leisure_LU_tot = np.nansum(np.nansum((leisure_km3 * mask3d),1),1)

            DataT[i,:] = T_LU_tot
            DataBT[i,:] = BT_LU_tot
            DataI[i,:] = I_LU_tot
            DataBI[i,:] = BI_LU_tot
            DataE[i,:] = E_LU_tot
            DataBE[i,:] = BE_LU_tot
            DataAgriculture[i,:] = Agriculture_LU_tot
            DataEnvironment[i,:] = Environment_LU_tot
            DataEconomic[i,:] = Economic_LU_tot
            DataEnergy[i,:] = Energy_LU_tot
            DataLeisure[i,:] = Leisure_LU_tot
            i += 1

    # Calculate non benefial components
    DataNBT = DataT - DataBT
    DataNBI = DataI - DataBI
    DataNBE = DataE - DataBE
    DataNB_tot = DataNBT + DataNBI + DataNBE

    # Create CSV
    first_row = ['LAND_USE', 'CLASS', 'TRANSPIRATION', 'WATER', 'SOIL', 'INTERCEPTION', 'AGRICULTURE', 'ENVIRONMENT', 'ECONOMY', 'ENERGY', 'LEISURE', 'NON_BENEFICIAL']
    i = 0

    # Create monthly CSV
    for Date in Dates:

        # Create csv-file.
        csv_filename = os.path.join(Data_Path_CSV, 'Sheet2_Sim%d_%s_%d_%02d.csv' %(Simulation, Basin, Date.year, Date.month))
        csv_file = open(csv_filename, 'wb')
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(first_row)

        j = 0

        # Loop over landuse and class
        for LAND_USE in sheet2_classes_dict.keys():
             for CLASS in sheet2_classes_dict[LAND_USE].keys():

                # Get the value of the current class and landuse
                Transpiration = DataT[j,i]
                Evaporation = DataE[j,i]
                Interception = DataI[j,i]
                Agriculture = DataAgriculture[j,i]
                Environment = DataEnvironment[j,i]
                Economic = DataEconomic[j,i]
                Energy = DataEnergy[j,i]
                Leisure = DataLeisure[j,i]
                Non_beneficial = DataNB_tot[j,i]

                # Set special cases.
                if np.any([CLASS == 'Natural water bodies', CLASS == 'Managed water bodies']):
                    Soil_evaporation = 0
                    Water_evaporation = Evaporation
                else:
                    Soil_evaporation = Evaporation
                    Water_evaporation = 0

                # Create the row to be written
                row = [LAND_USE, CLASS, "{0:.2f}".format(np.nansum([0, Transpiration])), "{0:.2f}".format(np.nansum([0, Water_evaporation])), "{0:.2f}".format(np.nansum([0, Soil_evaporation])), "{0:.2f}".format(np.nansum([0, Interception])), "{0:.2f}".format(np.nansum([0, Agriculture])), "{0:.2f}".format(np.nansum([0, Environment])), "{0:.2f}".format(np.nansum([0, Economic])), "{0:.2f}".format(np.nansum([0, Energy])), "{0:.2f}".format(np.nansum([0, Leisure])), "{0:.2f}".format(np.nansum([0, Non_beneficial]))]

                # Write the row.
                writer.writerow(row)

                j += 1

        # Close the csv-file.
        csv_file.close()
        i += 1

    # Create yearly CSV
    i = 0
    for Year in Years:

        # Create csv-file.
        csv_filename = os.path.join(Data_Path_CSV, 'Sheet2_Sim%d_%s_%d.csv' %(Simulation, Basin, Year))
        csv_file = open(csv_filename, 'wb')
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(first_row)

        j = 0

        # Loop over landuse and class
        for LAND_USE in sheet2_classes_dict.keys():
             for CLASS in sheet2_classes_dict[LAND_USE].keys():

                # Get the yearly value of the current class and landuse
                Transpiration = np.sum(DataT[j,Start_Year:Start_Year+12])
                Evaporation = np.sum(DataE[j,Start_Year:Start_Year+12])
                Interception = np.sum(DataI[j,Start_Year:Start_Year+12])
                Agriculture = np.sum(DataAgriculture[j,Start_Year:Start_Year+12])
                Environment = np.sum(DataEnvironment[j,Start_Year:Start_Year+12])
                Economic = np.sum(DataEconomic[j,Start_Year:Start_Year+12])
                Energy = np.sum(DataEnergy[j,Start_Year:Start_Year+12])
                Leisure = np.sum(DataLeisure[j,Start_Year:Start_Year+12])
                Non_beneficial = np.sum(DataNB_tot[j,Start_Year:Start_Year+12])

                # Set special cases.
                if np.any([CLASS == 'Natural water bodies', CLASS == 'Managed water bodies']):
                    Soil_evaporation = 0
                    Water_evaporation = Evaporation
                else:
                    Soil_evaporation = Evaporation
                    Water_evaporation = 0

                # Create the row to be written
                row = [LAND_USE, CLASS, "{0:.2f}".format(np.nansum([0, Transpiration])), "{0:.2f}".format(np.nansum([0, Water_evaporation])), "{0:.2f}".format(np.nansum([0, Soil_evaporation])), "{0:.2f}".format(np.nansum([0, Interception])), "{0:.2f}".format(np.nansum([0, Agriculture])), "{0:.2f}".format(np.nansum([0, Environment])), "{0:.2f}".format(np.nansum([0, Economic])), "{0:.2f}".format(np.nansum([0, Energy])), "{0:.2f}".format(np.nansum([0, Leisure])), "{0:.2f}".format(np.nansum([0, Non_beneficial]))]

                # Write the row.
                writer.writerow(row)

                j += 1

        # Close the csv-file.
        csv_file.close()
        i += 1
        Start_Year += 12

    return(Data_Path_CSV)