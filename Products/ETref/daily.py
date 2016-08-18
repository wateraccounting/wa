# -*- coding: utf-8 -*-
import sys
from CollectDataETref import CollectData


def main(Dir, Startdate='', Enddate='',
         latlim=[-50, 50], lonlim=[-180, 180], cores=False, LANDSAF=0):
                """
                This function creates ETref (daily) data based on Hydroshed, GLDAS, and (CFSR/LANDSAF)

                Keyword arguments:
                Dir -- 'C:/file/to/path/'
                Startdate -- 'yyyy-mm-dd'
                Enddate -- 'yyyy-mm-dd'
                latlim -- [ymin, ymax] (values must be between -50 and 50)
                lonlim -- [xmin, xmax] (values must be between -180 and 180)
                cores -- The number of cores used to run the routine.
                         It can be 'False' to avoid using parallel computing
                         routines.
                """
                # Download data
                CollectData(Dir, Startdate, Enddate, latlim, lonlim, cores, LANDSAF)

if __name__ == '__main__':
    main(sys.argv)
