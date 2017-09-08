# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 07:54:17 2017

@author: tih
"""
import os
import sys
from DataAccess import DownloadData

def main(Dir, Startdate='', Enddate='', latlim=[-60, 70], lonlim=[-180, 180], Waitbar = 1):
    """
    This function downloads monthly ALEXI data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -60 and 70)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    print '\nDownload monthly ALEXI evapotranspiration data for the period %s till %s' %(Startdate, Enddate)
    
    # Download data
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar)
    
    # Define directory
    Dir_ALEXI_Weekly = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Weekly')
    Dir_ALEXI_Monthly = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Monthly')
    
    # Create output directory
    if not os.path.exists(Dir_ALEXI_Monthly):
        os.mkdir(Dir_ALEXI_Monthly)
    
    # Create monthly maps based on weekly maps
    import wa.Functions.Start.Weekly_to_monthly_flux as Week2month
    Week2month.Nearest_Interpolate(Dir_ALEXI_Weekly, Startdate, Enddate, Dir_ALEXI_Monthly)

if __name__ == '__main__':
    main(sys.argv)
