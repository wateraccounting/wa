# -*- coding: utf-8 -*-
import os
from wa.Collect.DEM.DataAccess import DownloadData
import sys


def main(Dir, latlim, lonlim, Resample=0):
    """
    Downloads HydroSHED data from http://earlywarning.usgs.gov/hydrodata/

    this data includes a Digital Elevation Model (DEM)
    The spatial resolution is 90m

    Use the HydroSHED definitions to download and create the DEM images
    in Gtiff format with a resolution of 0.001 degrees in the WGS84 projection

    The following keyword arguments are needed:
    Dir -- 'C:/file/to/path/'    
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    Resample -- 1 = The data will be resampled to 0.001 degree spatial
                    resolution
             -- 0 = The data will have the same pixel size as the data obtained
                    from the internet
    """

    # Create directory if not exists for the output
    output_folder = os.path.join(Dir, 'HydroSHED', 'DEM')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the output map and create this if not exists
    nameEnd = os.path.join(Dir, 'HydroSHED', 'DEM', 'DEM_HydroShed_m.tif')
    if not os.path.exists(nameEnd):

        # Download and process the data
        DownloadData(output_folder, latlim, lonlim, Resample)

    else:
        print "DEM HydroSHED already exists in output folder"

if __name__ == '__main__':
    main(sys.argv)
