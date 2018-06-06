import sys
from DataAccess import DownloadData


def main(Dir, Startdate, Enddate, latlim, lonlim, cores=False, Waitbar = 1, hdf_library = None, remove_hdf = 1):
    """
    This function downloads MOD16 8-daily data for the specified time
    interval, and spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    cores -- amount of cores used
    Waitbar -- 1 (Default) will print a waitbar

    Dir = "C:/testMOD"
    Startdate = "2003-11-01"
    Enddate = "2004-01-06"
    latlim =[17,30]
    lonlim=[93,100]
    """
    print '\nDownload 8-daily MODIS ET data for period %s till %s' %(Startdate, Enddate)
    timestep = '8-daily'
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, timestep, Waitbar, cores, hdf_library, remove_hdf)

if __name__ == '__main__':
    main(sys.argv)