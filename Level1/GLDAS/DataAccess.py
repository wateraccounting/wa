# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from pydap.client import open_url
import calendar
from osgeo import osr, gdal


def DownloadData(Var, Startdate, Enddate, latlim, lonlim, Dir, cores,
                 TimeCase, CaseParameters):
    """
    This function downloads GLDAS three-hourly, daily or monthly data

    Keyword arguments:
    Var -- Variable code: VariablesInfo('day').descriptions.keys()
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    Dir -- 'C:/file/to/path/'
    CaseParameters -- See files: three_hourly.py, daily.py, and monthly.py
    """
    # Load factors / unit / type of variables
    VarInfo = VariablesInfo(TimeCase)
    # Load string parameters
    if TimeCase == 'three_hourly':
        # Define goal of folder and trim Shape if needed
        path = os.path.join(Dir, 'Weather_Data', 'Model', 'GLDAS',
                            TimeCase, Var)
        if not os.path.exists(path):
            os.makedirs(path)
        sd_date = '2000-02-24'
        TimeFreq = 'D'
        url = 'http://hydro1.sci.gsfc.nasa.gov:80/dods/GLDAS_NOAH025SUBP_3H'
        RetrieveData_fcn = RetrieveData_three_hourly
    elif TimeCase == 'daily':
        # Case parameters
        SumMean, Min, Max = CaseParameters
        # Define goal of folder and trim Shape if needed
        path = {'mean': os.path.join(Dir, 'Weather_Data', 'Model', 'GLDAS',
                                     TimeCase, Var, 'mean'),
                'min': os.path.join(Dir, 'Weather_Data', 'Model', 'GLDAS',
                                    TimeCase, Var, 'min'),
                'max': os.path.join(Dir, 'Weather_Data', 'Model', 'GLDAS',
                                    TimeCase, Var, 'max')}
        selected = np.array([SumMean, Min, Max])
        types = np.array(('mean', 'min', 'max'))[selected == 1]
        CaseParameters = [selected, types]
        for i in range(len(types)):
            if not os.path.exists(path[types[i]]):
                os.makedirs(path[types[i]])
        sd_date = '2000-02-24'
        TimeFreq = 'D'
        url = 'http://hydro1.sci.gsfc.nasa.gov:80/dods/GLDAS_NOAH025SUBP_3H'
        RetrieveData_fcn = RetrieveData_daily
    elif TimeCase == 'monthly':
        # Define goal of folder and trim Shape if needed
        path = os.path.join(Dir, 'Weather_Data', 'Model', 'GLDAS',
                            TimeCase, Var)
        if not os.path.exists(path):
            os.makedirs(path)
        selected = ''
        types = ''
        sd_date = '2000-03-01'
        TimeFreq = 'MS'
        url = 'http://hydro1.sci.gsfc.nasa.gov:80/dods/GLDAS_NOAH025_M'
        RetrieveData_fcn = RetrieveData_monthly
    else:
        raise KeyError("The input time interval is not supported")

    # Define IDs
    yID = np.int16(np.array([np.ceil((latlim[0] + 60)*4),
                             np.floor((latlim[1] + 60)*4)]))
    xID = np.int16(np.array([np.floor((lonlim[0] + 180)*4),
                             np.ceil((lonlim[1] + 180)*4)]))

    # Check dates. If no dates are given, the max number of days is used.
    if not Startdate:
        Startdate = pd.Timestamp(sd_date)
    if not Enddate:
        Enddate = pd.Timestamp('Now')  # Should be much than available
    dataset = open_url(url)
    Dates = pd.date_range(Startdate, Enddate, freq=TimeFreq)
    Time = np.int32(np.floor(dataset['time'][:])) - 1
    VarStr = VarInfo.names[Var]

    # Pass variables to parallel function and run
    args = [path, url, Time, Var, VarStr, VarInfo,
            TimeCase, xID, yID, lonlim, latlim, CaseParameters]
    if not cores:
        for Date in Dates:
            RetrieveData_fcn(Date, args)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(RetrieveData_fcn)(Date, args)
                                         for Date in Dates)
    return results


def RetrieveData_three_hourly(Date, args):
    """
    This function retrieves GLDAS three-hourly data for a given date.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [path, url, Time, Var, VarStr, VarInfo,
     TimeCase, xID, yID, lonlim, latlim, CaseParameters] = args
    dataset = open_url(url)
    # Paramaeters
    IDs = np.array(np.where(Date.toordinal() == Time))
    VarStr = VarInfo.names[Var]
    for Period in CaseParameters:
        PeriodDay = Period - 1
        # Check whether the file already exist or the worldfile is
        # downloaded
        BasinDir = path + '/' + VarStr + '_GLDAS-NOAH_' + \
            VarInfo.units[Var] + '_3hour_' + Date.strftime('%Y.%m.%d') + \
            '_'+str(Period) + '.tif'

        if not os.path.isfile(BasinDir):
            data = dataset[Var]
            data = data[Var][IDs[0, 0]:IDs[0, -1] + 1, yID[0]:yID[1],
                             xID[0]:xID[1]]

            if VarInfo.factors[Var] < 0:
                data = data + VarInfo.factors[Var]
            else:
                data = data * VarInfo.factors[Var]
            data[data < -9999] = -9999

            # Save to geotiff file
            driver = gdal.GetDriverByName("GTiff")

            dst_ds = driver.Create(BasinDir, data.shape[2], data.shape[1],
                                   1, gdal.GDT_Float32, ['COMPRESS=LZW'])
            srs = osr.SpatialReference()
            srs.SetWellKnownGeogCS("WGS84")
            dst_ds.SetProjection(srs.ExportToWkt())
            dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
            dst_ds.SetGeoTransform([lonlim[0], 0.25, 0,
                                    latlim[1], 0, -0.25])

            dst_ds.GetRasterBand(1).WriteArray(
                np.flipud(data[PeriodDay, :, :]))
            dst_ds = None
    return True


def RetrieveData_daily(Date, args):
    """
    This function retrieves GLDAS daily data for a given date.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [path, url, Time, Var, VarStr, VarInfo,
     TimeCase, xID, yID, lonlim, latlim, CaseParameters] = args
    [selected, types] = CaseParameters
    dataset = open_url(url)
    # Parameters
    IDs = np.array(np.where(Date.toordinal() == Time))
    for T in types:
        if T == 'mean':
            VarStr = VarInfo.names[Var]
        else:
            VarStr = VarInfo.names[Var] + '-' + T

        # Check whether the file already exist or
        # the worldfile is downloaded
        BasinDir = path[T] + '/' + VarStr + '_GLDAS-NOAH_' + \
            VarInfo.units[Var] + '_daily_' + Date.strftime('%Y.%m.%d') + \
            '.tif'

        if not os.path.isfile(BasinDir):
                data = dataset[Var]
                data = data[Var][IDs[0, 0]:IDs[0, -1]+1,
                                 yID[0]:yID[1], xID[0]:xID[1]]

                if VarInfo.factors[Var] < 0:
                    data = data + VarInfo.factors[Var]
                else:
                    data = data * VarInfo.factors[Var]
                data[data < -9999] = -9999

                # Save to geotiff file
                driver = gdal.GetDriverByName("GTiff")

                dst_ds = driver.Create(BasinDir, data.shape[2],
                                       data.shape[1], 1, gdal.GDT_Float32,
                                       ['COMPRESS=LZW'])
                srs = osr.SpatialReference()
                srs.SetWellKnownGeogCS("WGS84")
                dst_ds.SetProjection(srs.ExportToWkt())
                dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
                dst_ds.SetGeoTransform([lonlim[0], 0.25, 0,
                                        latlim[1], 0, -0.25])

                if T == 'mean':
                    dst_ds.GetRasterBand(1).WriteArray(
                        np.flipud(np.mean(data, axis=0)))
                if T == 'max':
                    dst_ds.GetRasterBand(1).WriteArray(
                        np.flipud(np.max(data, axis=0)))
                if T == 'min':
                    dst_ds.GetRasterBand(1).WriteArray(
                        np.flipud(np.min(data, axis=0)))

                dst_ds = None
    return True


def RetrieveData_monthly(Date, args):
    """
    This function retrieves GLDAS monthly data for a given date.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [path, url, Time, Var, VarStr, VarInfo,
     TimeCase, xID, yID, lonlim, latlim, CaseParameters] = args
    ID = np.int32(np.where(Date.toordinal() == Time))[0]
    dataset = open_url(url)
    Y = Date.year
    M = Date.month
    Mday = calendar.monthrange(Y, M)[1]
    # Check whether the file already exist or the worldfile is downloaded
    BasinDir = path + '/' + VarStr + '_GLDAS-NOAH_' + \
        VarInfo.units[Var] + '_monthly_' + Date.strftime('%Y.%m.%d') + \
        '.tif'
    if not os.path.isfile(BasinDir):
        data = dataset[Var]
        data = data[Var][ID[0], yID[0]:yID[1], xID[0]:xID[1]]
        if VarInfo.factors[Var] < 0:
            data = data + VarInfo.factors[Var]
        else:
            data = data * VarInfo.factors[Var]
        if VarInfo.types[Var] == 'flux':
            data = data * Mday
        data[data < -9999] = -9999

        # Save to geotiff file
        driver = gdal.GetDriverByName("GTiff")

        dst_ds = driver.Create(BasinDir, data.shape[2], data.shape[1], 1,
                               gdal.GDT_Float32, ['COMPRESS=LZW'])
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS("WGS84")
        dst_ds.SetProjection(srs.ExportToWkt())
        dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
        dst_ds.SetGeoTransform([lonlim[0], 0.25, 0, latlim[1], 0, -0.25])

        dst_ds.GetRasterBand(1).WriteArray(
            np.flipud(np.mean(data, axis=0)))

        dst_ds = None
    return True


class VariablesInfo:
    """
    This class contains the information about the GLDAS variables
    """
    names = {'avgsurft': 'T',
             'canopint': 'TotCanopyWaterStorage',
             'evap': 'ET',
             'lwdown': 'LWdown',
             'lwnet': 'LWnet',
             'psurf': 'P',
             'qair': 'Hum',
             'qg': 'G',
             'qh': 'H',
             'qle': 'LE',
             'qs': 'Rsur',
             'qsb': 'Rsubsur',
             'qsm': 'SnowMelt',
             'rainf': 'P',
             'swe': 'SnowWaterEquivalent',
             'swdown': 'SWdown',
             'swnet': 'SWnet',
             'snowf': 'Snow',
             'soilm1': 'S1',
             'soilm2': 'S2',
             'soilm3': 'S3',
             'soilm4': 'S4',
             'tsoil1': 'Ts1',
             'tsoil2': 'Ts2',
             'tsoil3': 'Ts3',
             'tsoil4': 'Ts4',
             'tair': 'Tair',
             'wind': 'W'}
    descriptions = {'avgsurft': 'surface average surface temperature [k]',
                    'canopint': 'surface plant canopy surface water [kg/m^2]',
                    'evap': 'surface total evapotranspiration [kg/m^2/s]',
                    'lwdown': ('surface surface incident longwave radiation'
                               ' [w/m^2]'),
                    'lwnet': 'surface net longwave radiation [w/m^2]',
                    'psurf': 'surface surface pressure [kPa]',
                    'qair': 'surface near surface specific humidity [kg/kg]',
                    'qg': 'surface ground heat flux [w/m^2]',
                    'qh': 'surface sensible heat flux [w/m^2]',
                    'qle': 'surface latent heat flux [w/m^2]',
                    'qs': 'surface surface runoff [kg/m^2/s]',
                    'qsb': 'surface subsurface runoff [kg/m^2/s]',
                    'qsm': 'surface snowmelt [kg/m^2/s]',
                    'rainf': 'surface rainfall rate [kg/m^2/s]',
                    'swe': 'surface snow water equivalent [kg/m^2]',
                    'swdown': ('surface surface incident shortwave radiation'
                               ' [w/m^2]'),
                    'swnet': 'surface net shortwave radiation [w/m^2]',
                    'snowf': 'surface snowfall rate [kg/m^2/s]',
                    'soilm1': ('0-10 cm underground soil moisture content'
                               ' [kg/m^2]'),
                    'soilm2': ('10-40 cm underground soil moisture content'
                               ' [kg/m^2]'),
                    'soilm3': ('40-100 cm underground soil moisture content'
                               ' [kg/m^2]'),
                    'soilm4': ('100-200 cm underground soil moisture content'
                               ' [kg/m^2]'),
                    'tsoil1': '0-10 cm underground soil temperature [k]',
                    'tsoil2': '10-40 cm underground soil temperature [k]',
                    'tsoil3': '40-100 cm underground soil temperature [k]',
                    'tsoil4': '100-200 cm underground soil temperature [k]',
                    'tair': 'surface near surface air temperature [k]',
                    'wind': 'surface near surface wind speed [m/s]'}
    factors = {'avgsurft': -273.16,
               'canopint': 1,
               'evap': 86400,
               'lwdown': 1,
               'lwnet': 1,
               'psurf': 0.001,
               'qair': 1,
               'qg': 1,
               'qh': 1,
               'qle': 1,
               'qs': 86400,
               'qsb': 86400,
               'qsm': 86400,
               'rainf': 86400,
               'swe': 1,
               'swdown': 1,
               'swnet': 1,
               'snowf': 1,
               'soilm1': 1,
               'soilm2': 1,
               'soilm3': 1,
               'soilm4': 1,
               'tsoil1': -273.16,
               'tsoil2': -273.16,
               'tsoil3': -273.16,
               'tsoil4': -273.16,
               'tair': -273.16,
               'wind': 0.75}
    types = {'avgsurft': 'state',
             'canopint': 'state',
             'evap': 'flux',
             'lwdown': 'state',
             'lwnet': 'state',
             'psurf': 'state',
             'qair': 'state',
             'qg': 'state',
             'qh': 'state',
             'qle': 'state',
             'qs': 'flux',
             'qsb': 'flux',
             'qsm': 'flux',
             'rainf': 'flux',
             'swe': 'state',
             'swdown': 'flux',
             'swnet': 'flux',
             'snowf': 'state',
             'soilm1': 'state',
             'soilm2': 'state',
             'soilm3': 'state',
             'soilm4': 'state',
             'tsoil1': 'state',
             'tsoil2': 'state',
             'tsoil3': 'state',
             'tsoil4': 'state',
             'tair': 'state',
             'wind': 'state'}

    def __init__(self, step):
        if step == 'three_hourly':
            self.units = {'avgsurft': 'C',
                          'canopint': 'mm',
                          'evap': 'mm-day-1',
                          'lwdown': 'W-m-2',
                          'lwnet': 'W-m-2',
                          'psurf': 'kpa',
                          'qair': 'kg-kg',
                          'qg': 'W-m-2',
                          'qh': 'W-m-2',
                          'qle': 'W-m-2',
                          'qs': 'mm-3hour-1',
                          'qsb': 'mm-3hour-1',
                          'qsm': 'mm-3hour-1',
                          'rainf': 'mm-3hour-1',
                          'swe': 'mm',
                          'swdown': 'W-m-2',
                          'swnet': 'W-m-2',
                          'snowf': 'mm',
                          'soilm1': 'mm',
                          'soilm2': 'mm',
                          'soilm3': 'mm',
                          'soilm4': 'mm',
                          'tsoil1': 'C',
                          'tsoil2': 'C',
                          'tsoil3': 'C',
                          'tsoil4': 'C',
                          'tair': 'C',
                          'wind': 'm-s-1'}
        elif step == 'daily':
            self.units = {'avgsurft': 'C',
                          'canopint': 'mm',
                          'evap': 'mm-day-1',
                          'lwdown': 'W-m-2',
                          'lwnet': 'W-m-2',
                          'psurf': 'kpa',
                          'qair': 'kg-kg',
                          'qg': 'W-m-2',
                          'qh': 'W-m-2',
                          'qle': 'W-m-2',
                          'qs': 'mm-day-1',
                          'qsb': 'mm-day-1',
                          'qsm': 'mm-day-1',
                          'rainf': 'mm-day-1',
                          'swe': 'mm',
                          'swdown': 'W-m-2',
                          'swnet': 'W-m-2',
                          'snowf': 'mm',
                          'soilm1': 'mm',
                          'soilm2': 'mm',
                          'soilm3': 'mm',
                          'soilm4': 'mm',
                          'tsoil1': 'C',
                          'tsoil2': 'C',
                          'tsoil3': 'C',
                          'tsoil4': 'C',
                          'tair': 'C',
                          'wind': 'm-s-1'}
        elif step == 'monthly':
            self.units = {'avgsurft': 'C',
                          'canopint': 'mm',
                          'evap': 'mm-month-1',
                          'lwdown': 'W-m-2',
                          'lwnet': 'W-m-2',
                          'psurf': 'kpa',
                          'qair': 'kg-kg',
                          'qg': 'W-m-2',
                          'qh': 'W-m-2',
                          'qle': 'W-m-2',
                          'qs': 'mm-month-1',
                          'qsb': 'mm-month-1',
                          'qsm': 'mm-month-1',
                          'rainf': 'mm-month-1',
                          'swe': 'mm',
                          'swdown': 'W-m-2',
                          'swnet': 'W-m-2',
                          'snowf': 'mm',
                          'soilm1': 'mm',
                          'soilm2': 'mm',
                          'soilm3': 'mm',
                          'soilm4': 'mm',
                          'tsoil1': 'C',
                          'tsoil2': 'C',
                          'tsoil3': 'C',
                          'tsoil4': 'C',
                          'tair': 'C',
                          'wind': 'm-s-1'}
        else:
            raise KeyError("The input time step is not supported")
