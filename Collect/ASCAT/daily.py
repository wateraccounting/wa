# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 07:54:17 2017

@author: tih
"""
import sys
from DataAccess import DownloadData


def main(Dir, Startdate='', Enddate='', latlim=[-60, 70],
         lonlim=[-180, 180], Waitbar=1):
    """
    This function downloads daily ASCAT data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -60 and 70)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    print '\nDownload daily ASCAT SWI data for the period %s till %s'\
        % (Startdate, Enddate)

    # Download data
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar)

if __name__ == '__main__':
    main(sys.argv)
