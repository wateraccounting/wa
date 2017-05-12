# -*- coding: utf-8 -*-
import sys
from DataAccess import DownloadData


def main(Dir, Vars, Startdate, Enddate, latlim, lonlim, cores=False,
         SumMean=1, Min=0, Max=0, Waitbar = 1):
    """
    This function downloads GLDAS daily data for a given variable, time
    interval, and spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Var -- Variable code: VariablesInfo('day').descriptions.keys()
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    SumMean -- 0 or 1. Indicates if the output values are the daily mean for
               instantaneous values or sum for fluxes
    Min -- 0 or 1. Indicates if the output values are the daily minimum
    Max -- 0 or 1. Indicates if the output values are the daily maximum
    Waitbar -- 1 (Default) Will print a waitbar
    """
    for Var in Vars:
        
        if Waitbar == 1:
            print '\nDownloading daily GLDAS %s data for the period %s till %s' %(Var, Startdate, Enddate)   
      
        # Download data
        DownloadData(Dir, Var, Startdate, Enddate, latlim, lonlim, Waitbar, cores,
					 TimeCase='daily', CaseParameters=[SumMean, Min, Max])

if __name__ == '__main__':
    main(sys.argv)

