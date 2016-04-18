# -*- coding: utf-8 -*-
import numpy as np
import os
from osgeo import osr, gdal
import pandas as pd
from ftplib import FTP
from struct import unpack
from joblib import Parallel, delayed


def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, cores, TimeCase):
    """
    This function downloads TRMM daily or monthly data

    Keyword arguments:
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    Dir -- 'C:/file/to/path/'
    TimeCase -- String equal to 'daily' or 'monthly'
    """
    # String Parameters
    if TimeCase == 'daily':
        VarCode = 'P_TRMM3B42.V7_mm-day-1_daily_'
        FTPprefix = 'data/TRMM/Gridded/Derived_Products/3B42_V7/Daily/'
        TimeFreq = 'D'
        Const = [1, '%j', 1]
    elif TimeCase == 'monthly':
        VarCode = 'P_TRMM3B42.V7_mm-month-1_monthly_'
        FTPprefix = 'data/TRMM/Gridded/3B43_V7/'
        TimeFreq = 'MS'
        Const = [4, '%m', 3]
    else:
        raise KeyError("The input time interval is not supported")
    # Check variables
    if not Startdate:
        Startdate = pd.Timestamp('1998-01-01')
    if not Enddate:
        Enddate = pd.Timestamp('Now')
    Dates = pd.date_range(Startdate,  Enddate, freq=TimeFreq)
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
    # Make directory
    output_folder = os.path.join(Dir, 'Precipitation', 'TRMM/')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define IDs
    yID = 400 - np.int16(np.array([np.ceil((latlim[1] + 50)*4),
                                   np.floor((latlim[0] + 50)*4)]))
    xID = np.int16(np.array([np.floor((lonlim[0])*4),
                             np.ceil((lonlim[1])*4)]) + 720)

    # Pass variables to parallel function and run
    args = [output_folder, VarCode, FTPprefix, Const,
            TimeCase, xID, yID, lonlim, latlim]
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
    This function retrieves TRMM data for a given date from the
    ftp://disc2.nascom.nasa.gov server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, VarCode, FTPprefix, Const,
     TimeCase, xID, yID, lonlim, latlim] = args
    # File name .Tiff (final result)
    DirFile = output_folder + VarCode + \
        Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + \
        Date.strftime('%d') + '.tif'
    # Open ftp server
    ftp = FTP("disc2.nascom.nasa.gov", "", "")
    ftp.login()
    pathFTP = FTPprefix + Date.strftime('%Y') + '/'
    # ftp.retrlines("LIST")
    ftp.cwd(pathFTP)
    listing = []
    ftp.retrlines("LIST", listing.append)
    words = listing[Const[0]*int(
            Date.strftime(Const[1])) - Const[2]].split(None, 8)
    filename = words[-1].lstrip()

    # Download the file
    try:
        local_filename = os.path.join(output_folder, filename)
        lf = open(local_filename, "wb")
        ftp.retrbinary("RETR " + filename, lf.write, 8192)  # 8*1024
        lf.close()
        # Open .bin file
        if TimeCase == 'daily':
            opendata = output_folder + '3B42_daily.' + \
                Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + \
                Date.strftime('%d') + '.7.bin'
        elif TimeCase == 'monthly':
            opendata = output_folder + '3B43.' + Date.strftime('%y') + \
                Date.strftime('%m') + Date.strftime('%d') + \
                '.7.precipitation.accum'
        else:
                raise KeyError("The input time interval is not supported")
        f = open(opendata, "rb")
        NumbytesFile = 576000
        NumElementxRecord = -1440
        dataset = np.zeros(shape=(1440, 400))
        i = -1
        for PositionByte in range(NumbytesFile, 0, NumElementxRecord):
            i = i + 1
            Record = ''
            for c in range(PositionByte - 720, PositionByte, 1):
                f.seek(c * 4)
                DataElement = unpack('>f', f.read(4))
                Record = Record + str("%.2f" % DataElement + ' ')

            for c in range(PositionByte - 1440, PositionByte - 720, 1):
                f.seek(c * 4)
                DataElement = unpack('>f', f.read(4))
                Record = Record + str("%.2f" % DataElement + ' ')

            datasetrow = np.fromstring(Record, dtype=float, sep=' ')
            dataset[:, i] = datasetrow
        # Delete .bin file
        f.close()
        os.remove(opendata)

        # Clip extend out of world data
        dataset = np.transpose(dataset)
        if TimeCase == 'monthly':
                dataset2 = dataset[:, 0:720]
                dataset3 = dataset[:, 720:1440]
                dataset = np.hstack([dataset3, dataset2])
        data = dataset[yID[0]:yID[1], xID[0]:xID[1]]
        data[data < 0] = -9999
        # Make geotiff file
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.Create(DirFile, data.shape[1], int(yID[1]-yID[0]),
                               1, gdal.GDT_Float32, ['COMPRESS=LZW'])
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS("WGS84")
        dst_ds.SetProjection(srs.ExportToWkt())
        dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
        dst_ds.SetGeoTransform([lonlim[0], 0.25, 0, latlim[1], 0, -0.25])
        dst_ds.GetRasterBand(1).WriteArray(data)
        dst_ds = None
    except:
        print "file not exists"
    return True
