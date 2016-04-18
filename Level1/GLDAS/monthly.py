# -*- coding: utf-8 -*-
import sys
from DataAccess import DownloadData


def main(Var, Startdate, Enddate, latlim, lonlim, Dir, cores=False):
    """
    This function downloads GLDAS monthly data for a given variable, time
    interval, and spatial extent.

    Keyword arguments:
    Var -- Variable code: VariablesInfo('day').descriptions.keys()
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    Dir -- 'C:/file/to/path/'
    """
    # Download data
    DownloadData(Var, Startdate, Enddate, latlim, lonlim, Dir, cores,
                 TimeCase='monthly', CaseParameters=False)

if __name__ == '__main__':
    main(sys.argv)
