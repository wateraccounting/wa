# -*- coding: utf-8 -*-
import sys
from DataAccess import DownloadData


def main(Dir, Vars, Startdate, Enddate, latlim, lonlim, cores=False):
    """
    This function downloads GLDAS monthly data for a given variable, time
    interval, and spatial extent.

    Keyword arguments:
	Dir -- 'C:/file/to/path/'
    Var -- Variable code: VariablesInfo('day').descriptions.keys()
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    """
    for Var in Vars:
	    # Download data
         DownloadData(Dir, Var, Startdate, Enddate, latlim, lonlim, cores,
                     TimeCase='monthly', CaseParameters=False)

if __name__ == '__main__':
    main(sys.argv)
