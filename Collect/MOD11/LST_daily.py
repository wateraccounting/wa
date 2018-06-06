import sys
from DataAccess import DownloadData


def main(Dir, Startdate, Enddate, latlim, lonlim, cores=False, Waitbar = 1, hdf_library = None, remove_hdf = 1):
    """
    This function downloads MOD11 daily data for the specified time
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

    print '\nDownload daily MODIS land surface temperature data for period %s till %s' %(Startdate, Enddate)
    TimeStep = 1
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, TimeStep, Waitbar, cores, hdf_library, remove_hdf)

if __name__ == '__main__':
    main(sys.argv)