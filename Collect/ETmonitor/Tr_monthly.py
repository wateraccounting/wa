# -*- coding: utf-8 -*-
"""
Created on Wed Jan 03 09:38:51 2018

@author: tih
"""

import os
import sys
from DataAccess import DownloadData

def main(Dir, Startdate='', Enddate='', latlim=[-60, 70], lonlim=[-180, 180], Waitbar = 1):
    """
    This function downloads monthly ETmonitor data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -60 and 70)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    print '\nDownload monthly ETmonitor Transpiration data for the period %s till %s' %(Startdate, Enddate)
    
    Type = "tr"
	
    # Download data
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Type, Waitbar)
    
if __name__ == '__main__':
    main(sys.argv)