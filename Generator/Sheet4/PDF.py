# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Generator/Sheet4
"""
import os
import glob

def Create(Dir_Basin, Basin, Simulation, Dir_Basin_CSV, Unit_front):
    """
    This functions create the monthly and yearly sheet 4 in pdf format, based on the csv files.

    Parameters
    ----------
    Dir_Basin : str
        Path to all the output data of the Basin
    Basin : str
        Name of the basin
    Simulation : int
        Defines the simulation
    Dir_Basin_CSV : str
        Data path pointing to the CSV output files
    Unit_front : str
        Defines the scaling of the CSV file
    """
    # import wa module
    from wa.Sheets import create_sheet4

    # Create output folder for CSV files
    Dir_Basin_PDF = os.path.join(Dir_Basin, "Simulations", "Simulation_%d" %Simulation, "PDF")
    if not os.path.exists(Dir_Basin_PDF):
        os.mkdir(Dir_Basin_PDF)

    # find all the CSV's
    os.chdir(Dir_Basin_CSV)
    files = glob.glob('Sheet4_Sim%d*.csv' %Simulation)

    # loop over CSV's files
    for File in files:

        # split the name
        FileName_Splitted = File.split('_')

        # If the splitted parts are 4 then it is a yearly sheet
        if len(FileName_Splitted)==4:
            # Define the output names
            units = '%skm3/year' %(Unit_front)
            Year = str(FileName_Splitted[-1].split('.')[0])
            outFile1 = 'Sheet4a_Sim%s_%s_%s.pdf' %(Simulation, Basin, Year)
            outFile2 = 'Sheet4b_Sim%s_%s_%s.pdf' %(Simulation, Basin, Year)

            # create the sheet
            create_sheet4(basin=Basin, period = Year, units = [units,units], data = [os.path.join(Dir_Basin_CSV,File),os.path.join(Dir_Basin_CSV,File)] , output = [os.path.join(Dir_Basin_PDF, outFile1),os.path.join(Dir_Basin_PDF, outFile2)], template=False, tolerance=1000)

        # If the splitted parts are 5 then it is a monthly sheet
        elif len(FileName_Splitted)==5:
            # Define the output names
            MonthInLetters = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
            units = '%skm3/month' %(Unit_front)
            Year = str(FileName_Splitted[3])
            Month = str(FileName_Splitted[-1].split('.')[0])
            NameTime = '%s_%02s' %(Year, Month)
            NameTimeSpace = '%s %s' %(Year, MonthInLetters[int(Month)])
            outFile1 = 'Sheet4a_Sim%s_%s_%s.pdf' %(Simulation, Basin, NameTime)
            outFile2 = 'Sheet4b_Sim%s_%s_%s.pdf' %(Simulation, Basin, NameTime)

            # create the sheet
            create_sheet4(basin=Basin, period = NameTimeSpace, units = [units,units] , data = [os.path.join(Dir_Basin_CSV,File),os.path.join(Dir_Basin_CSV,File)]  , output = [os.path.join(Dir_Basin_PDF, outFile1),os.path.join(Dir_Basin_PDF, outFile2)],template=False, tolerance=0.2)

    return()

