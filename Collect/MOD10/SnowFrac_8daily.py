import sys
from DataAccess import DownloadData


def main(Dir, Startdate, Enddate, latlim, lonlim, cores=False, Waitbar = 1):
    """
    This function downloads MOD10 8-daily data for the specified time
    interval, and spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    cores -- amount of cores used
    Waitbar -- 1 (Default) will print a waitbar
    """
    print '\nDownload 8-daily MODIS SnowFrac data for period %s till %s' %(Startdate, Enddate)
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar, cores)

if __name__ == '__main__':
    main(sys.argv)