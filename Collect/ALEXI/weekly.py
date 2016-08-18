# -*- coding: utf-8 -*-
import sys
from DataAccess import DownloadData


def main(Dir, Startdate='', Enddate='', latlim=[-60, 70], lonlim=[-180, 180]):
                """
                This function downloads weekly ALEXI data

                Keyword arguments:
                Dir -- 'C:/file/to/path/'
                Startdate -- 'yyyy-mm-dd'
                Enddate -- 'yyyy-mm-dd'
                latlim -- [ymin, ymax] (values must be between -60 and 70)
                lonlim -- [xmin, xmax] (values must be between -180 and 180)
                """
                # Download data
                DownloadData(Dir, Startdate, Enddate, latlim, lonlim)

if __name__ == '__main__':
    main(sys.argv)
