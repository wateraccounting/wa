# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 07:54:17 2017

@author: tih
"""
import os
import sys
from DataAccess import DownloadData

def main(Dir, Startdate='', Enddate='', latlim=[-59.17, 80], lonlim=[-180, 180], version = "V4", Waitbar = 1):
    """
    This function downloads monthly SSEBop data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -59.17 and 80)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    print '\nDownload monthly SSEBop evapotranspiration data for the period %s till %s' %(Startdate, Enddate)

    # Download data
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar, version)

if __name__ == '__main__':
    main(sys.argv)
