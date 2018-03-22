# -*- coding: utf-8 -*-
import sys
from CLSM_DataAccess import DownloadData


def main(Dir, Vars, Startdate, Enddate, latlim, lonlim, cores=False, Waitbar = 1):
    """
    This function downloads CLSM GLDAS daily data for a given variable, time
    interval, and spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Vars -- ['wind_f_inst','qair_f_inst'] (array of strings) Variable code: VariablesInfo('day').descriptions.keys()
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    Waitbar -- 1 (Default) Will print a waitbar

    """
    for Var in Vars:
        
        if Waitbar == 1:
            print '\nDownloading daily GLDAS CLSM %s data for the period %s till %s' %(Var, Startdate, Enddate)   
      
        # Download data
        DownloadData(Dir, Var, Startdate, Enddate, latlim, lonlim, Waitbar, cores, TimeCase='daily')

if __name__ == '__main__':
    main(sys.argv)

