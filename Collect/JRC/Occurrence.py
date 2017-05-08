"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/JRC
"""

import sys
from DataAccess import DownloadData


def main(Dir, latlim, lonlim):
    """
    This function downloads JRC water occurrence data for the specified spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    """
    DownloadData(Dir, latlim, lonlim)

if __name__ == '__main__':
    main(sys.argv)