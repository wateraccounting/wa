# -*- coding: utf-8 -*-
import sys
from DataAccess import DownloadData


def main(Dir, latlim=[-60, 84], lonlim=[-180, 180]):

    """
    This function downloads gray water footprint data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    latlim -- [ymin, ymax] (values must be between -60 and 84)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    # Download data
    DownloadData(Dir, latlim, lonlim)

if __name__ == '__main__':
    main(sys.argv)
