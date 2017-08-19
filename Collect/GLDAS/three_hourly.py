# -*- coding: utf-8 -*-
import sys
from DataAccess import DownloadData


def main(Dir, Vars, Startdate, Enddate, latlim, lonlim, cores=False,
         Periods=[1, 2, 3, 4, 5, 6, 7, 8], Waitbar = 1, gldas_version = '2.1'):
    """
    This function downloads GLDAS three-hourly data for a given variable, time
    interval, spatial extent, and day period.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Var --  ['wind_f_inst','qair_f_inst'] Variable code. Run: VariablesInfo('day').descriptions.keys()
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    Periods -- List of numbers from 1 to 8 (e.g. [1,4,5,8]). Stands for the
               period of hour of a day as follows:
                    Period       Hours
                      1      00:00 - 03:00
                      2      03:00 - 06:00
                      3      06:00 - 09:00
                      4      09:00 - 12:00
                      5      12:00 - 15:00
                      6      15:00 - 18:00
                      7      18:00 - 21:00
                      8      21:00 - 24:00
    Waitbar -- 1 (Default) Will print a waitbar   
    gldas_version = '2.1' (Default) or '2.0'  
    
    Version 2.1 is available from 2000-01-01 till present
    Version 2.0 is available from 1948-01-01 till 2010-12-31
    """
    for Var in Vars:

        if Waitbar == 1:
            print '\nDownloading 3-houly GLDAS %s data for the period %s till %s' %(Var, Startdate, Enddate)  
        
        # Download data
        DownloadData(Dir, Var, Startdate, Enddate, latlim, lonlim, Waitbar, cores,
					 TimeCase='three_hourly', CaseParameters=Periods, gldas_version = gldas_version)    # Download data

if __name__ == '__main__':
    main(sys.argv)
