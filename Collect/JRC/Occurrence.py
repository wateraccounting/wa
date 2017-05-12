"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/JRC
"""

import sys
from DataAccess import DownloadData


def main(Dir, latlim, lonlim, Waitbar = 1):
    """
    This function downloads JRC water occurrence data for the specified spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    Waitbar -- 1 (Default) will print a waitbar
    """
    print '\nDownload JRC occurrence map'
    DownloadData(Dir, latlim, lonlim, Waitbar)

if __name__ == '__main__':
    main(sys.argv)