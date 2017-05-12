# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETens
"""
# General Modules
import sys
import pandas as pd
import numpy as np

# WA+ modules
from DataAccess import DownloadData

def main(Dir, Startdate, Enddate, latlim, lonlim, Waitbar = 1):
    """
    This function downloads ETensemble data for the specified time
    interval, and spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    Waitbar -- 1 (Default) Will print a waitbar
    """
 
	# Check the start and enddate
    if not Startdate:
        Startdate = pd.Timestamp('2003-01-01')
    if not Enddate: 
        Enddate = pd.Timestamp('2014-12-31')

    # Check and adjust if needed the latitude and longitude
    if latlim[0] < -90 or latlim[1] > 90:
        print 'Latitude above 90N or below 90S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0],-90)
        latlim[1] = np.min(latlim[1],90)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0],-180)
        lonlim[1] = np.min(lonlim[1],180)

    print '/nCreate monthly ETensemble maps for period %s till %s' %(Startdate, Enddate)
    # Download and create the ET data
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar)

if __name__ == '__main__':
    main(sys.argv)
				