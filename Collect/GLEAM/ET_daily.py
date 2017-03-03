# -*- coding: utf-8 -*-
'''
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/GLEAM
'''


import sys
from DataAccess import DownloadData


def main(Dir, Startdate, Enddate, latlim, lonlim, cores=False):
    """
    This function downloads GLEAM daily data for the specified time
    interval, and spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
	cores -- amount of cores used
    """
    TimeCase = 'daily'
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, cores, TimeCase)

if __name__ == '__main__':
    main(sys.argv)