import sys
from DataAccess import DownloadData


def main(Dir, Startdate, Enddate, latlim, lonlim, cores=False):
    """
    This function downloads MOD9 reflectance daily data for the specified time
    interval, and spatial extent.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
	cores -- amount of cores used
    """
    DownloadData(Dir, Startdate, Enddate, latlim, lonlim, cores)

if __name__ == '__main__':
    main(sys.argv)