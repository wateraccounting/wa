# -*- coding: utf-8 -*-

# General modules
import numpy as np
import calendar
import os
import pandas as pd
import requests
from joblib import Parallel, delayed

# Water Accounting modules
from wa import WebAccounts
import wa.General.data_conversions as DC

def DownloadData(Dir, Var, Startdate, Enddate, latlim, lonlim, Waitbar, cores,
                 TimeCase, CaseParameters, gldas_version = '2.1'):
    """
    This function downloads GLDAS Version 2 three-hourly, daily or monthly data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Var -- 'wind_f_inst' : (string) For all variable codes: VariablesInfo('day').descriptions.keys()
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    cores -- 1....8
    CaseParameters -- See files: three_hourly.py, daily.py, and monthly.py
    """

    # Load factors / unit / type of variables / accounts
    VarInfo = VariablesInfo(TimeCase)
    username, password = WebAccounts.Accounts(Type = 'NASA')

    # Set required data for the three hourly option
    if TimeCase == 'three_hourly':

        # Define output folder and create this one if not exists
        path = os.path.join(Dir, 'Weather_Data', 'Model', 'GLDAS',
                            TimeCase, Var)

        if not os.path.exists(path):
            os.makedirs(path)

        # Startdate if not defined
        sd_date = '2000-02-24'

        # Define Time frequency
        TimeFreq = 'D'

        # Define URL by using personal account
        #url = 'http://%s:%s@hydro1.gesdisc.eosdis.nasa.gov:80/dods/GLDAS_NOAH025SUBP_3H' %(username,password)
        url = 'https://hydro1.gesdisc.eosdis.nasa.gov/dods/GLDAS_NOAH025_3H.{0}'.format(gldas_version) #%(username,password)

        # Name the definition that will be used to obtain the data
        RetrieveData_fcn = RetrieveData_three_hourly

    # Set required data for the daily option
    elif TimeCase == 'daily':

        # seperate the daily case parameters
        SumMean, Min, Max = CaseParameters

        # Define output folder and create this one if not exists
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

        # Startdate if not defined
        sd_date = '2000-02-24'

        # Define Time frequency
        TimeFreq = 'D'

        # Define URL by using personal account
        #url = 'http://%s:%s@hydro1.gesdisc.eosdis.nasa.gov:80/dods/GLDAS_NOAH025SUBP_3H' %(username,password)
        url = 'https://hydro1.gesdisc.eosdis.nasa.gov/dods/GLDAS_NOAH025_3H.{0}'.format(gldas_version) #%(username,password)

        # Name the definition that will be used to obtain the data
        RetrieveData_fcn = RetrieveData_daily

    # Set required data for the monthly option
    elif TimeCase == 'monthly':

        # Define output folder and create this one if not exists
        path = os.path.join(Dir, 'Weather_Data', 'Model', 'GLDAS',
                            TimeCase, Var)
        if not os.path.exists(path):
            os.makedirs(path)
        CaseParameters = []

        # Startdate if not defined
        sd_date = '2000-03-01'

        # Define Time frequency
        TimeFreq = 'MS'

        # Define URL by using personal account
        #url = 'http://%s:%s@hydro1.gesdisc.eosdis.nasa.gov:80/dods/GLDAS_NOAH025_M' %(username,password)
        url = 'https://hydro1.gesdisc.eosdis.nasa.gov/dods/GLDAS_NOAH025_M.{0}'.format(gldas_version) #%(username,password)


        # Name the definition that will be used to obtain the data
        RetrieveData_fcn = RetrieveData_monthly

    # If none of the possible option are chosen
    else:
        raise KeyError("The input time interval is not supported")

    # Define IDs (latitude/longitude)
    yID = np.int16(np.array([np.ceil((latlim[0] + 60) * 4),
                             np.floor((latlim[1] + 60) * 4)]))
    xID = np.int16(np.array([np.floor((lonlim[0] + 180) * 4),
                             np.ceil((lonlim[1] + 180) * 4)]))

    # Check dates. If no dates are given, the max number of days is used.
    if not Startdate:
        Startdate = pd.Timestamp(sd_date)
    if not Enddate:
        Enddate = pd.Timestamp('Now')  # Should be much than available

    # Create all dates that will be calculated
    Dates = pd.date_range(Startdate, Enddate, freq=TimeFreq)

    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Define the variable string name
    VarStr = VarInfo.names[Var]

    # Create one parameter with all the required arguments
    args = [path, url, Var, VarStr, VarInfo,
            TimeCase, xID, yID, lonlim, latlim, CaseParameters, username, password]

    # Pass variables to parallel function and run
    if not cores:
        for Date in Dates:
            RetrieveData_fcn(Date, args)
            if Waitbar == 1:
                amount += 1
                WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
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

	# Open all the parameters
    [path, url, Var, VarStr, VarInfo, TimeCase, xID, yID, lonlim, latlim, CaseParameters, username, password] = args

	# Open variable info parameters
    VarFactor = VarInfo.factors[Var]

    # Check GLDAS version
    version = url[-3:]

	# Loop over the periods
    for period in CaseParameters:

        # Check whether the file already exist or the worldfile is
        # downloaded
        BasinDir = path + '/' + VarStr + '_GLDAS-NOAH_' + \
            VarInfo.units[Var] + '_3hour_' + Date.strftime('%Y.%m.%d') + \
            '_'+str(period) + '.tif'

        if not os.path.isfile(BasinDir):

            # Reset the begin parameters for downloading
            downloaded = 0
            N=0

            while downloaded == 0:
                try:

                    # Define time
                    if version == '2.1':
                        zID = int(((Date - pd.Timestamp("2000-1-1")).days) * 8) + (period - 1)
                    elif version == '2.0':
                        zID = int(((Date - pd.Timestamp("1948-1-1")).days) * 8) + (period - 1)

                    # total URL
                    url_GLDAS = url + '.ascii?%s[%s][%s:1:%s][%s:1:%s]' %(Var,zID,yID[0],yID[1],xID[0],xID[1])

                    # open URL
                    try:
                        dataset = requests.get(url_GLDAS, allow_redirects=False,stream = True)
                    except:
                        from requests.packages.urllib3.exceptions import InsecureRequestWarning
                        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                        dataset = requests.get(url_GLDAS, allow_redirects=False,stream = True, verify = False)

                    try:
                        get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True)
                    except:
                        from requests.packages.urllib3.exceptions import InsecureRequestWarning
                        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                        get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True, verify = False)

                    # download data (first save as text file)
                    pathtext = os.path.join(path,'temp%s.txt' %zID)
                    z = open(pathtext,'w')
                    z.write(get_dataset.content)
                    z.close()

                    # Open text file and remove header and footer
                    data_start = np.genfromtxt(pathtext,dtype = float,skip_header = 1,skip_footer = 6,delimiter=',')
                    data = data_start[:,1:]

                    # Add the VarFactor
                    if VarFactor < 0:
                        data = data + VarFactor
                    else:
                        data = data * VarFactor
                    if VarInfo.types[Var] == 'flux':
                        data = data / 8

                    # Set Nan value for values lower than -9999
                    data[data < -9999] = -9999

                    # Say that download was succesfull
                    downloaded = 1

                # If download was not succesfull
                except:
                    data=[]

                    # Try another time
                    N = N + 1

                    # Stop trying after 10 times
                    if N == 10:
                        print 'Data from ' + Date.strftime('%Y-%m-%d') + ' is not available'
                        downloaded = 1

            # define geo
            lonlimGLDAS = xID[0] * 0.25 - 180
            latlimGLDAS = (yID[1] + 1) * 0.25 - 60

            # Save to geotiff file
            geo = [lonlimGLDAS,0.25,0,latlimGLDAS,0,-0.25]
            DC.Save_as_tiff(name=BasinDir, data=np.flipud(data[:,:]), geo=geo, projection="WGS84")

            # Delete data and text file
            del data
            os.remove(pathtext)

    return True


def RetrieveData_daily(Date, args):
    """
    This function retrieves GLDAS daily data for a given date.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """

    # Open all the parameters
    [path, url, Var, VarStr, VarInfo,
     TimeCase, xID, yID, lonlim, latlim, CaseParameters, username, password] = args
    [selected, types] = CaseParameters

    # Reset the begin parameters for downloading
    downloaded = 0
    N = 0
    data_end = []

    # Check GLDAS version
    version = url[-3:]

    # Open all variable info
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

        # Check if the outputfile already excists
        if not os.path.isfile(BasinDir):

            # Create the time dimension
            if version == '2.0':
                zID_start = int(((Date - pd.Timestamp("1948-1-1")).days) * 8)
                zID_end = zID_start + 7
            elif version == '2.1':
                zID_start = int(((Date - pd.Timestamp("2000-1-1")).days) * 8)
                zID_end = zID_start + 7

            # define total url
            url_GLDAS = url + '.ascii?%s[%s:1:%s][%s:1:%s][%s:1:%s]' %(Var,zID_start,zID_end,yID[0],yID[1],xID[0],xID[1])

            # if not downloaded try to download file
            while downloaded == 0:
                try:

                    # open URL
                    try:
                        dataset = requests.get(url_GLDAS, allow_redirects=False,stream = True)
                    except:
                        from requests.packages.urllib3.exceptions import InsecureRequestWarning
                        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                        dataset = requests.get(url_GLDAS, allow_redirects=False,stream = True, verify = False)
                    try:
                        get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True)
                    except:
                        from requests.packages.urllib3.exceptions import InsecureRequestWarning
                        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                        get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True, verify = False)

                    # download data (first save as text file)
                    pathtext = os.path.join(path[T],'temp%s.txt' %str(zID_start))
                    z = open(pathtext,'w')
                    z.write(get_dataset.content)
                    z.close()

                    # Reshape data
                    datashape = [8,yID[1] - yID[0] + 1,xID[1] - xID[0] + 1]
                    data_start = np.genfromtxt(pathtext,dtype = float,skip_header = 1,skip_footer = 6,delimiter = ',')
                    data_list = np.asarray(data_start[:,1:])
                    data_end = np.resize(data_list,(8, datashape[1], datashape[2]))
                    os.remove(pathtext)

                    # Add the VarFactor
                    if VarInfo.factors[Var] < 0:
                        data_end[data_end != -9999] = data_end[data_end != -9999] + VarInfo.factors[Var]
                    else:
                        data_end[data_end != -9999] = data_end[data_end != -9999] * VarInfo.factors[Var]
                    data_end[data_end < -9999] = -9999

                    # define geo
                    lonlimGLDAS = xID[0] * 0.25 - 180
                    latlimGLDAS = (yID[1] + 1) * 0.25 - 60

                    # Download was succesfull
                    downloaded = 1

                # If download was not succesfull
                except:

                    # Try another time
                    N = N + 1

                    # Stop trying after 10 times
                    if N == 10:
                        print 'Data from ' + Date.strftime('%Y-%m-%d') + ' is not available'
                        downloaded = 1

            try:
                # Save to geotiff file

                if T == 'mean':
                    data = np.flipud(np.mean(data_end, axis=0))
                if T == 'max':
                    data = np.flipud(np.max(data_end, axis=0))
                if T == 'min':
                    data = np.flipud(np.min(data_end, axis=0))

                geo = [lonlimGLDAS,0.25,0,latlimGLDAS,0,-0.25]
                DC.Save_as_tiff(name=BasinDir, data=data, geo=geo, projection="WGS84")

            except:
                print 'GLDAS map from '+ Date.strftime('%Y-%m-%d') + ' is not created'

    return True


def RetrieveData_monthly(Date, args):
    """
    This function retrieves GLDAS monthly data for a given date.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [path, url, Var, VarStr, VarInfo,
            TimeCase, xID, yID, lonlim, latlim, CaseParameters, username, password] = args

	# Open variable info parameters
    VarFactor = VarInfo.factors[Var]

    # Check whether the file already exist or the worldfile is downloaded
    BasinDir = path + '/' + VarStr + '_GLDAS-NOAH_' + \
        VarInfo.units[Var] + '_monthly_' + Date.strftime('%Y.%m.%d') + \
        '.tif'

    # Define month and year of current month
    Y = Date.year
    M = Date.month
    Mday = calendar.monthrange(Y, M)[1]

    # Check GLDAS version
    version = url[-3:]

    # Check if the outputfile already excists
    if not os.path.isfile(BasinDir):

        # Reset the begin parameters for downloading
        downloaded = 0
        N=0

        # Create the time dimension
        if version == '2.1':
            zID = (Y - 2000) * 12 + (M - 1)
        elif version == '2.0':
            zID = (Y - 1948) * 12 + (M - 1)

        # define total url
        url_GLDAS = url + '.ascii?%s[%s][%s:1:%s][%s:1:%s]' %(Var,zID,yID[0],yID[1],xID[0],xID[1])

        # if not downloaded try to download file
        while downloaded == 0:
            try:

                # open URL
                try:
                    dataset = requests.get(url_GLDAS, allow_redirects=False,stream = True)
                except:
                    from requests.packages.urllib3.exceptions import InsecureRequestWarning
                    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                    dataset = requests.get(url_GLDAS, allow_redirects=False,stream = True, verify = False)
                try:
                    get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True)
                except:
                    from requests.packages.urllib3.exceptions import InsecureRequestWarning
                    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                    get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True, verify = False)

                # download data (first save as text file)
                pathtext = os.path.join(path,'temp%s.txt' %str(zID))
                z = open(pathtext,'w')
                z.write(get_dataset.content)
                z.close()

                # Open text file and remove header and footer
                data_start = np.genfromtxt(pathtext,dtype = float,skip_header = 1,skip_footer = 6,delimiter=',')
                data = data_start[:,1:]

                # Add the VarFactor
                if VarFactor < 0:
                    data = data + VarFactor
                else:
                    data = data * VarFactor
                if VarInfo.types[Var] == 'flux':
                    data = data * Mday

                # Set Nan value for values lower than -9999
                data[data < -9999] = -9999

                # Say that download was succesfull
                downloaded = 1

            # If download was not succesfull
            except:
                data=[]

                # Try another time
                N = N + 1

                # Stop trying after 10 times
                if N == 10:
                    print 'Data from ' + Date.strftime('%Y-%m-%d') + ' is not available'
                    downloaded = 1

            # define geo
            lonlimGLDAS = xID[0] * 0.25 - 180
            latlimGLDAS = (yID[1] + 1) * 0.25 - 60

            # Save to geotiff file
            geo = [lonlimGLDAS,0.25,0,latlimGLDAS,0,-0.25]
            DC.Save_as_tiff(name=BasinDir, data=np.flipud(data[:,:]), geo=geo, projection="WGS84")


            # Delete data and text file
            del data
            os.remove(pathtext)

	    return True

class VariablesInfo:
    """
    This class contains the information about the GLDAS variables
    """
    names = {'avgsurft_inst': 'T',
             'canopint_inst': 'TotCanopyWaterStorage',
             'evap_tavg': 'ET',
             'lwdown_f_tavg': 'LWdown',
             'lwnet_tavg': 'LWnet',
             'psurf_f_inst': 'P',
             'qair_f_inst': 'Hum',
             'qg_tavg': 'G',
             'qh_tavg': 'H',
             'qle_tavg': 'LE',
             'qs_acc': 'Rsur',
             'qsb_acc': 'Rsubsur',
             'qsm_acc': 'SnowMelt',
             'rainf_f_tavg': 'P',
             'swe_inst': 'SnowWaterEquivalent',
             'swdown_f_tavg': 'SWdown',
             'swnet_tavg': 'SWnet',
             'snowf_tavg': 'Snow',
             'sm0_10cm_ins': 'S1',
             'sm10_40cm_ins': 'S2',
             'sm40_100cm_ins': 'S3',
             'sm100_200cm_ins': 'S4',
             'st0_10cm_ins': 'Ts1',
             'st10_40cm_ins': 'Ts2',
             'st40_100cm_ins': 'Ts3',
             'st100_200cm_ins': 'Ts4',
             'tair_f_inst': 'Tair',
             'wind_f_inst': 'W',
             'tveg_tavg' : 'Transpiration'}
    descriptions = {'avgsurft_inst': 'surface average skin surface temperature [k]',
                    'canopint_inst': 'surface plant canopy surface water [kg/m^2]',
                    'evap_tavg': 'surface total evapotranspiration [kg/m^2/s]',
                    'lwdown_f_tavg': 'surface surface incident longwave radiation'
                               ' [w/m^2]',
                    'lwnet_tavg': 'surface net longwave radiation [w/m^2]',
                    'psurf_f_inst': 'surface surface pressure [kPa]',
                    'qair_f_inst': 'surface near surface specific humidity [kg/kg]',
                    'qg_tavg': 'surface ground heat flux [w/m^2]',
                    'qh_tavg': 'surface sensible heat flux [w/m^2]',
                    'qle_tavg': 'surface latent heat flux [w/m^2]',
                    'qs_acc': 'storm surface runoff [kg/m^2/s]',
                    'qsb_acc': 'baseflow-groundwater runoff [kg/m^2/s]',
                    'qsm_acc': 'surface snowmelt [kg/m^2/s]',
                    'rainf_f_tavg': 'surface rainfall rate [kg/m^2/s]',
                    'swe_inst': 'surface snow water equivalent [kg/m^2]',
                    'swdown_f_tavg': 'surface surface incident shortwave radiation'
                               ' [w/m^2]',
                    'swnet_tavg': 'surface net shortwave radiation [w/m^2]',
                    'snowf_tavg': 'surface snowfall rate [kg/m^2/s]',
                    'sm0_10cm_ins': '0-10 cm underground soil moisture content'
                               ' [kg/m^2]',
                    'sm10_40cm_ins': '10-40 cm underground soil moisture content'
                               ' [kg/m^2]',
                    'sm40_100cm_ins': '40-100 cm underground soil moisture content'
                               ' [kg/m^2]',
                    'sm100_200cm_ins': '100-200 cm underground soil moisture content'
                               ' [kg/m^2]',
                    'st0_10cm_ins': '0-10 cm underground soil temperature [k]',
                    'st10_40cm_ins': '10-40 cm underground soil temperature [k]',
                    'st40_100cm_ins': '40-100 cm underground soil temperature [k]',
                    'st100_200cm_ins': '100-200 cm underground soil temperature [k]',
                    'tair_f_inst': 'surface near surface air temperature [k]',
                    'wind_f_inst': 'surface near surface wind speed [m/s]',
                    'tveg_tavg' : 'transpiration [w/m^2]'}
    factors = {'avgsurft_inst': -273.15,
               'canopint_inst': 1,
               'evap_tavg': 86400,
               'lwdown_f_tavg': 1,
               'lwnet_tavg': 1,
               'psurf_f_inst': 0.001,
               'qair_f_inst': 1,
               'qg_tavg': 1,
               'qh_tavg': 1,
               'qle_tavg': 1,
               'qs_acc': 86400,
               'qsb_acc': 86400,
               'qsm_acc': 86400,
               'rainf_f_tavg': 86400,
               'swe_inst': 1,
               'swdown_f_tavg': 1,
               'swnet_tavg': 1,
               'snowf_tavg': 1,
               'sm0_10cm_ins': 1,
               'sm10_40cm_ins': 1,
               'sm40_100cm_ins': 1,
               'sm100_200cm_ins': 1,
               'st0_10cm_ins': -273.15,
               'st10_40cm_ins': -273.15,
               'st40_100cm_ins': -273.15,
               'st100_200cm_ins': -273.15,
               'tair_f_inst': -273.15,
               'wind_f_inst': 0.75,
               'tveg_tavg' : 1}
    types = {'avgsurft_inst': 'state',
             'canopint_inst': 'state',
             'evap_tavg': 'flux',
             'lwdown_f_tavg': 'state',
             'lwnet_tavg': 'state',
             'psurf_f_inst': 'state',
             'qair_f_inst': 'state',
             'qg_tavg': 'state',
             'qh_tavg': 'state',
             'qle_tavg': 'state',
             'qs_acc': 'flux',
             'qsb_acc': 'flux',
             'qsm_acc': 'flux',
             'rainf_f_tavg': 'flux',
             'swe_inst': 'state',
             'swdown_f_tavg': 'state',
             'swnet_tavg': 'state',
             'snowf_tavg': 'state',
             'sm0_10cm_ins': 'state',
             'sm10_40cm_ins': 'state',
             'sm40_100cm_ins': 'state',
             'sm100_200cm_ins': 'state',
             'st0_10cm_ins': 'state',
             'st10_40cm_ins': 'state',
             'st40_100cm_ins': 'state',
             'st100_200cm_ins': 'state',
             'tair_f_inst': 'state',
             'wind_f_inst': 'state',
             'tveg_tavg' : 'state'}

    def __init__(self, step):
        if step == 'three_hourly':
            self.units = {'avgsurft_inst': 'C',
                          'canopint_inst': 'mm',
                          'evap_tavg': 'mm-day-1',
                          'lwdown_f_tavg': 'W-m-2',
                          'lwnet_tavg': 'W-m-2',
                          'psurf_f_inst': 'kpa',
                          'qair_f_inst': 'kg-kg',
                          'qg_tavg': 'W-m-2',
                          'qh_tavg': 'W-m-2',
                          'qle_tavg': 'W-m-2',
                          'qs_acc': 'mm-3hour-1',
                          'qsb_acc': 'mm-3hour-1',
                          'qsm_acc': 'mm-3hour-1',
                          'rainf_f_tavg': 'mm-3hour-1',
                          'swe_inst': 'mm',
                          'swdown_f_tavg': 'W-m-2',
                          'swnet_tavg': 'W-m-2',
                          'snowf_tavg': 'mm',
                          'sm0_10cm_ins': 'kg-m-2',
                          'sm10_40cm_ins': 'kg-m-2',
                          'sm40_100cm_ins': 'kg-m-2',
                          'sm100_200cm_ins': 'kg-m-2',
                          'st0_10cm_ins': 'C',
                          'st10_40cm_ins': 'C',
                          'st40_100cm_ins': 'C',
                          'st100_200cm_ins': 'C',
                          'tair_f_inst': 'C',
                          'wind_f_inst': 'm-s-1',
                          'tveg_tavg' : 'W-m-2'}
        elif step == 'daily':
            self.units = {'avgsurft_inst': 'C',
                          'canopint_inst': 'mm',
                          'evap_tavg': 'mm-day-1',
                          'lwdown_f_tavg': 'W-m-2',
                          'lwnet_tavg': 'W-m-2',
                          'psurf_f_inst': 'kpa',
                          'qair_f_inst': 'kg-kg',
                          'qg_tavg': 'W-m-2',
                          'qh_tavg': 'W-m-2',
                          'qle_tavg': 'W-m-2',
                          'qs_acc': 'mm-day-1',
                          'qsb_acc': 'mm-day-1',
                          'qsm_acc': 'mm-day-1',
                          'rainf_f_tavg': 'mm-day-1',
                          'swe_inst': 'mm',
                          'swdown_f_tavg': 'W-m-2',
                          'swnet_tavg': 'W-m-2',
                          'snowf_tavg': 'mm',
                          'sm0_10cm_ins': 'kg-m-2',
                          'sm10_40cm_ins': 'kg-m-2',
                          'sm40_100cm_ins': 'kg-m-2',
                          'sm100_200cm_ins': 'kg-m-2',
                          'st0_10cm_ins': 'C',
                          'st10_40cm_ins': 'C',
                          'st40_100cm_ins': 'C',
                          'st100_200cm_ins': 'C',
                          'tair_f_inst': 'C',
                          'wind_f_inst': 'm-s-1',
                          'tveg_tavg' : 'W-m-2'}
        elif step == 'monthly':
            self.units = {'avgsurft_inst': 'C',
                          'canopint_inst': 'mm',
                          'evap_tavg': 'mm-month-1',
                          'lwdown_f_tavg': 'W-m-2',
                          'lwnet_tavg': 'W-m-2',
                          'psurf_f_inst': 'kpa',
                          'qair_f_inst': 'kg-kg',
                          'qg_tavg': 'W-m-2',
                          'qh_tavg': 'W-m-2',
                          'qle_tavg': 'W-m-2',
                          'qs_acc': 'mm-month-1',
                          'qsb_acc': 'mm-month-1',
                          'qsm_acc': 'mm-month-1',
                          'rainf_f_tavg': 'mm-month-1',
                          'swe_inst': 'mm',
                          'swdown_f_tavg': 'W-m-2',
                          'swnet_tavg': 'W-m-2',
                          'snowf_tavg': 'mm',
                          'sm0_10cm_ins': 'kg-m-2',
                          'sm10_40cm_ins': 'kg-m-2',
                          'sm40_100cm_ins': 'kg-m-2',
                          'sm100_200cm_ins': 'kg-m-2',
                          'st0_10cm_ins': 'C',
                          'st10_40cm_ins': 'C',
                          'st40_100cm_ins': 'C',
                          'st100_200cm_ins': 'C',
                          'tair_f_inst': 'C',
                          'wind_f_inst': 'm-s-1',
                          'tveg_tavg' : 'W-m-2'}
        else:
            raise KeyError("The input time step is not supported")
