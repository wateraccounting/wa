# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
from ftplib import FTP
import gzip
from osgeo import osr, gdal
from joblib import Parallel, delayed


def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, cores, TimeCase):
    """
    This function downloads CHIRPS daily or monthly data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine. It can be 'False'
             to avoid using parallel computing routines.
    TimeCase -- String equal to 'daily' or 'monthly'
    """
    # Define timestep for the timedates
    if TimeCase == 'daily':
        TimeFreq = 'D'
    elif TimeCase == 'monthly':
        TimeFreq = 'MS'
    else:
        raise KeyError("The input time interval is not supported")
    
	# check time variables
    if not Startdate:
        Startdate = pd.Timestamp('1981-01-01')
    if not Enddate:
        Enddate = pd.Timestamp('Now')
								
    # Create days
    Dates = pd.date_range(Startdate, Enddate, freq=TimeFreq)

    # Check space variables
    if latlim[0] < -50 or latlim[1] > 50:
        print ('Latitude above 50N or below 50S is not possible.'
               ' Value set to maximum')
        latlim[0] = np.max(latlim[0], -50)
        latlim[1] = np.min(lonlim[1], 50)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print ('Longitude must be between 180E and 180W.'
               ' Now value is set to maximum')
        lonlim[0] = np.max(latlim[0], -180)
        lonlim[1] = np.min(lonlim[1], 180)

    # make directory if it not exists
    output_folder = os.path.join(Dir, 'Precipitation', 'CHIRPS/')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define IDs
    yID = 2000 - np.int16(np.array([np.ceil((latlim[1] + 50)*20),
                                    np.floor((latlim[0] + 50)*20)]))
    xID = np.int16(np.array([np.floor((lonlim[0] + 180)*20),
                             np.ceil((lonlim[1] + 180)*20)]))

    # Pass variables to parallel function and run
    args = [output_folder, TimeCase, xID, yID, lonlim, latlim]
    if not cores:
        for Date in Dates:
            RetrieveData(Date, args)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(RetrieveData)(Date, args)
                                         for Date in Dates)
    return results


def RetrieveData(Date, args):
    """
    This function retrieves CHIRPS data for a given date from the
    ftp://chg-ftpout.geog.ucsb.edu server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, TimeCase, xID, yID, lonlim, latlim] = args
				
    # open ftp server
    ftp = FTP("chg-ftpout.geog.ucsb.edu", "", "")
    ftp.login()
				
	# Define FTP path to directory 			
    if TimeCase == 'daily':
        pathFTP = 'pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p05/' + \
                  Date.strftime('%Y') + '/'
    elif TimeCase == 'monthly':
        pathFTP = 'pub/org/chg/products/CHIRPS-2.0/global_monthly/tifs/'
    else:
        raise KeyError("The input time interval is not supported")
								
    # find the document name in this directory								
    ftp.cwd(pathFTP)
    listing = []
				
	# read all the file names in the directory			
    ftp.retrlines("LIST", listing.append)
				
	# create all the input name (filename) and output (outfilename, filetif, DiFileEnd) names			
    if TimeCase == 'daily':
        filename = 'chirps-v2.0.' + Date.strftime('%Y') + '.' + \
                   Date.strftime('%m') + '.' + Date.strftime('%d') + '.tif.gz'
        outfilename = output_folder + 'chirps-v2.0.' + \
            Date.strftime('%Y') + '.' + Date.strftime('%m') + \
            '.' + Date.strftime('%d') + '.tif'
        filetif = output_folder + 'chirps-v2.0.' + Date.strftime('%Y') + \
            '.' + Date.strftime('%m') + '.' + Date.strftime('%d') + '.tif'
        DirFileEnd = output_folder + 'P_CHIRPS.v2.0_mm-day-1_daily_' + \
            Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + \
            Date.strftime('%d') + '.tif'
    elif TimeCase == 'monthly':
        filename = 'chirps-v2.0.' + Date.strftime('%Y') + '.' + \
            Date.strftime('%m') + '.tif.gz'
        outfilename = output_folder + 'chirps-v2.0.' + \
            Date.strftime('%Y') + '.' + Date.strftime('%m') + '.tif'
        filetif = output_folder + 'chirps-v2.0.' + Date.strftime('%Y') + \
            '.' + Date.strftime('%m') + '.tif'
        DirFileEnd = output_folder + 'P_CHIRPS.v2.0_mm-month-1_monthly_' + \
            Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + \
            Date.strftime('%d') + '.tif'
    else:
        raise KeyError("The input time interval is not supported")

    # download the global rainfall file
    try:
        local_filename = os.path.join(output_folder, filename)
        lf = open(local_filename, "wb")
        ftp.retrbinary("RETR " + filename, lf.write, 8192)
        lf.close()

        # unzip the file
        zip_filename = output_folder + filename
        with gzip.GzipFile(zip_filename, 'rb') as zf:
            file_content = zf.read()
            save_file_content = file(outfilename, 'wb')
            save_file_content.write(file_content)
        save_file_content.close()
        zf.close()
        os.remove(zip_filename)

        # open tiff file
        ds = gdal.Open(filetif)
        dataset = np.array(ds.GetRasterBand(1).ReadAsArray())

        # clip dataset to the given extent
        data = dataset[yID[0]:yID[1], xID[0]:xID[1]]
        data[data < 0] = -9999

        # save dataset as geotiff file
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.Create(DirFileEnd, data.shape[1],
                               int(yID[1]-yID[0]), 1, gdal.GDT_Float32,
                               ['COMPRESS=LZW'])
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS("WGS84")
        dst_ds.SetProjection(srs.ExportToWkt())
        dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
        dst_ds.SetGeoTransform([lonlim[0], 0.05, 0, latlim[1], 0, -0.05])
        dst_ds.GetRasterBand(1).WriteArray(data)
        dst_ds = None

        # delete old tif file
        ds = None
        os.remove(filetif)

    except:
        print "file not exists"
    return True
