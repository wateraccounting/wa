# -*- coding: utf-8 -*-
import sys
from DataAccess import DownloadData


def main(Var, Startdate, Enddate, latlim, lonlim, Dir, cores=False,
         SumMean=1, Min=0, Max=0):
    """
    This function downloads GLDAS daily data for a given variable, time
    interval, and spatial extent.

    Keyword arguments:
    Var -- Variable code: VariablesInfo('day').descriptions.keys()
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    Dir -- 'C:/file/to/path/'
    SumMean -- 0 or 1. Indicates if the output values are the daily mean for
               instantaneous values or sum for fluxes
    Min -- 0 or 1. Indicates if the output values are the daily minimum
    Max -- 0 or 1. Indicates if the output values are the daily maximum
    """
    # Download data
    DownloadData(Var, Startdate, Enddate, latlim, lonlim, Dir, cores,
                 TimeCase='daily', CaseParameters=[SumMean, Min, Max])

if __name__ == '__main__':
    main(sys.argv)
