# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/DEM
"""

#General modules
import os
import sys

# Water Accounting modules
from wa.Collect.DEM.DataAccess import DownloadData

def main(Dir, latlim, lonlim, resolution = '3s'):
    """
    Downloads HydroSHED flow direction data from http://www.hydrosheds.org/download/

    this data includes a Digital Elevation Model Flow Direction 
    The spatial resolution is 90m (3s) or 450m (15s)

    The following keyword arguments are needed:
    Dir -- 'C:/file/to/path/'    
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    resolution -- '3s' (default) or '15s'
    """

    # Create directory if not exists for the output
    output_folder = os.path.join(Dir, 'HydroSHED', 'DIR')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the output map and create this if not exists  # Define the output map and create this if not exists
    nameEnd = os.path.join(Dir, 'HydroSHED', 'DIR', 'DIR_HydroShed_-_%s.tif' %resolution) 
    parameter = "dir_%s" %resolution

    if not os.path.exists(nameEnd):

        # Download and process the data
        DownloadData(output_folder, latlim, lonlim, parameter, resolution)

    else:
        print "DIR HydroSHED already exists in output folder"

if __name__ == '__main__':
    main(sys.argv)
