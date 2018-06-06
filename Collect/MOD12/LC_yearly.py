import sys
from DataAccess import DownloadData


def main(Dir, Startdate, Enddate, latlim, lonlim, LC_Types = [1], cores=False, Waitbar = 1, hdf_library = None, remove_hdf = 1):
    """
    This function downloads MOD12 yearly LC data for the specified time
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

    for LC_Type in LC_Types:
        print '\nDownload yearly MODIS LC%d data for period %s till %s' %(LC_Type, Startdate, Enddate)
        DownloadData(Dir, Startdate, Enddate, latlim, lonlim, LC_Type, Waitbar, cores, hdf_library, remove_hdf)

if __name__ == '__main__':
    main(sys.argv)