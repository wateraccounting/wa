# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 07:54:17 2017

@author: tih
"""

import sys
from DataAccess import DownloadData

def main(Dir, Startdate='', Enddate='', latlim=[-90, 90], lonlim=[-180, 180], Waitbar = 1):
    """
    This function downloads monthly SEBS data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between 90 and 90)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    print '\nDownload monthly SEBS evapotranspiration data for the period %s till %s' %(Startdate, Enddate)
    
    # Download data
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar)
    
if __name__ == '__main__':
    main(sys.argv)
