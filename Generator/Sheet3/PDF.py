# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Generator/Sheet3
"""
import os

def Create(Dir_Basin, Basin, Simulation, Dir_Basin_CSV_a, Dir_Basin_CSV_b):
    """
    This functions create the monthly and yearly sheet 3 in pdf format, based on the csv files.

    Parameters
    ----------
    Dir_Basin : str
        Path to all the output data of the Basin
    Basin : str
        Name of the basin
    Simulation : int
        Defines the simulation
    Dir_Basin_CSV_a : str
        Data path pointing to the CSV output files for sheet a
    Dir_Basin_CSV_b : str
        Data path pointing to the CSV output files for sheet b
    """
    # import wa module
    from wa.Sheets import create_sheet3

    # Create output folder for PDF files
    Dir_Basin_PDF = os.path.join(Dir_Basin, "Simulations", "Simulation_%d" %Simulation, "PDF")
    if not os.path.exists(Dir_Basin_PDF):
        os.mkdir(Dir_Basin_PDF)

    # Create output filename for PDFs
    FileName_Splitted = Dir_Basin_CSV_a.split('_')
    Year = str(FileName_Splitted[-1].split('.')[0])
    outFile_a = os.path.join(Dir_Basin_PDF,'Sheet3a_Sim%s_%s_%s.pdf' %(Simulation, Basin, Year))
    outFile_b = os.path.join(Dir_Basin_PDF,'Sheet3b_Sim%s_%s_%s.pdf' %(Simulation, Basin, Year))

    # Create PDFs
    sheet3a_fh, sheet3b_fh = create_sheet3(Basin, str(Year), ['km3/year', 'kg/ha/year', 'kg/m3'], [Dir_Basin_CSV_a, Dir_Basin_CSV_b], [outFile_a, outFile_b])

    return()

