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

def DownloadData(Dir, Var, Startdate, Enddate, latlim, lonlim, Waitbar, cores, TimeCase):    
    """
    This function downloads GLDAS CLSM daily data

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
			
    # Set required data for the daily option
    if TimeCase == 'daily':
					
        types = ['mean']
								
        # Define output folder and create this one if not exists
        path = {'mean': os.path.join(Dir, 'Weather_Data', 'Model', 'GLDAS_CLSM',
                                     TimeCase, Var, 'mean')}
        for i in range(len(types)):
            if not os.path.exists(path[types[i]]):
                os.makedirs(path[types[i]])		
				
        # Startdate if not defined																
        sd_date = '1948-01-01'
								
        # Define Time frequency								
        TimeFreq = 'D'
        
        # Define URL by using personal account	
        url = 'https://hydro1.gesdisc.eosdis.nasa.gov/dods/GLDAS_CLSM025_D.2.0'
										
        # Name the definition that will be used to obtain the data									
        RetrieveData_fcn = RetrieveData_daily

    # Set required data for the monthly option
    if TimeCase == 'monthly':
					
        types = ['mean']
								
        # Define output folder and create this one if not exists
        path = {'mean': os.path.join(Dir, 'Weather_Data', 'Model', 'GLDAS_CLSM',
                                     TimeCase, Var, 'mean')}
        for i in range(len(types)):
            if not os.path.exists(path[types[i]]):
                os.makedirs(path[types[i]])		
				
        # Startdate if not defined																
        sd_date = '1948-01-01'
								
        # Define Time frequency								
        TimeFreq = 'MS'
        
        # Define URL by using personal account	
        url = 'https://hydro1.gesdisc.eosdis.nasa.gov/dods/GLDAS_CLSM025_D.2.0'
										
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
    args = [path, url, Var, VarStr, VarInfo, TimeCase, xID, yID, lonlim, latlim, username, password, types]
												
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


def RetrieveData_daily(Date, args):
    """
    This function retrieves GLDAS daily data for a given date.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
				
    # Open all the parameters
    [path, url, Var, VarStr, VarInfo, TimeCase, xID, yID, lonlim, latlim, username, password, types] = args
	      
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
        BasinDir = os.path.join(path[T], VarStr + '_GLDAS-CLSM_' +  VarInfo.units[Var] + '_daily_' + Date.strftime('%Y.%m.%d') + '.tif')
        
        # Check if the outputfile already excists						
        if not os.path.isfile(BasinDir):
            
            # Create the time dimension
            if version == '2.0':
                zID_start = int(((Date - pd.Timestamp("1948-1-1")).days))
                zID_end = int(zID_start)
                if zID_end == 24472:
                    zID_end = 24470

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
                    datashape = [yID[1] - yID[0] + 1,xID[1] - xID[0] + 1]
                    data_start = np.genfromtxt(pathtext,dtype = float,skip_header = 1,skip_footer = 6,delimiter = ',')																	
                    data_list = np.asarray(data_start[:,1:])
                    data_end = np.resize(data_list,(datashape[0], datashape[1]))																									
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
                    data = np.flipud(data_end)
 
                geo = [lonlimGLDAS,0.25,0,latlimGLDAS,0,-0.25]
                DC.Save_as_tiff(name=BasinDir, data=data, geo=geo, projection="WGS84")																
																				
            except:
                print 'GLDAS map from '+ Date.strftime('%Y-%m-%d') + ' is not created'	
																
    return True


def RetrieveData_monthly(Date, args):
    """
    This function retrieves GLDAS CLSM monthly data for a given date.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
				
    # Open all the parameters
    [path, url, Var, VarStr, VarInfo, TimeCase, xID, yID, lonlim, latlim, username, password, types] = args
	      
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
        BasinDir = os.path.join(path[T], VarStr + '_GLDAS-CLSM_' +  VarInfo.units[Var] + '_monthly_' + Date.strftime('%Y.%m.%d') + '.tif')
        
        # Check if the outputfile already excists						
        if not os.path.isfile(BasinDir):
            
            # Create the time dimension
            if version == '2.0':
                zID_start = int(((Date - pd.Timestamp("1948-1-1")).days))
                Y = int(Date.year)
                M = int(Date.month)
                Mday = calendar.monthrange(Y,M)[1]
                zID_end = zID_start + Mday
                if zID_end == 24472:
                    zID_end = 24470
                    Mday = Mday - 2


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
                    datashape = [Mday,yID[1] - yID[0] + 1,xID[1] - xID[0] + 1]
                    data_start = np.genfromtxt(pathtext,dtype = float,skip_header = 1,skip_footer = 6,delimiter = ',')																	
                    data_list = np.asarray(data_start[:,1:])
                    data_end = np.resize(data_list,(Mday, datashape[1], datashape[2]))																									
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
                    data_end[data_end<-100] = np.nan
                    data = np.flipud(np.nanmean(data_end, axis=0))
                if VarInfo.types[Var] == 'flux':
                    data = data * Mday
                    
                geo = [lonlimGLDAS,0.25,0,latlimGLDAS,0,-0.25]
                DC.Save_as_tiff(name=BasinDir, data=data, geo=geo, projection="WGS84")																
																				
            except:
                print 'GLDAS map from '+ Date.strftime('%Y-%m-%d') + ' is not created'	
																
    return True

class VariablesInfo:
    """
    This class contains the information about the GLDAS variables
    """
    names = {'canopint_tavg': 'TotCanopyWaterStorage',
             'evap_tavg': 'ET',
             'lwdown_f_tavg': 'LWdown',
             'lwnet_tavg': 'LWnet',
             'psurf_f_tavg': 'P',
             'qair_f_tavg': 'Hum',
             'qg_tavg': 'G',
             'qh_tavg': 'H',
             'qle_tavg': 'LE',
             'qs_tavg': 'Rsur',
             'qsb_tavg': 'Rsubsur',
             'qsm_tavg': 'SnowMelt',
             'rainf_f_tavg': 'P',
             'swe_tavg': 'SnowWaterEquivalent',
             'swdown_f_tavg': 'SWdown',
             'swnet_tavg': 'SWnet',
             'snowf_tavg': 'Snow',
             'soilmoist_s_tav': 'SoilMoisturSurface',
             'soilmoist_rz_ta': 'SoilMoistureRootZone',
             'soilmoist_p_tav': 'SoilMoistureProfile',
             'tair_f_tavg': 'Tair',
             'wind_f_tavg': 'W',
             'tveg_tavg' : 'Transpiration'}
    descriptions = {'avgsurft_tavg': 'surface average surface temperature [k]',
                    'canopint_tavg': 'surface plant canopy surface water [kg/m^2]',
                    'evap_tavg': 'surface total evapotranspiration [kg/m^2/s]',
                    'lwdown_f_tavg': 'surface surface incident longwave radiation'
                               ' [w/m^2]',
                    'lwnet_tavg': 'surface net longwave radiation [w/m^2]',
                    'psurf_f_tavg': 'surface surface pressure [kPa]',
                    'qair_f_tavg': 'surface near surface specific humidity [kg/kg]',
                    'qg_tavg': 'surface ground heat flux [w/m^2]',
                    'qh_tavg': 'surface sensible heat flux [w/m^2]',
                    'qle_tavg': 'surface latent heat flux [w/m^2]',
                    'qs_tavg': 'storm surface runoff [kg/m^2/s]',
                    'qsb_tavg': 'baseflow-groundwater runoff [kg/m^2/s]',
                    'qsm_tavg': 'surface snowmelt [kg/m^2/s]',
                    'rainf_f_tavg': 'surface rainfall rate [kg/m^2/s]',
                    'swe_tavg': 'surface snow water equivalent [kg/m^2]',
                    'swdown_f_tavg': 'surface surface incident shortwave radiation'
                               ' [w/m^2]',
                    'swnet_tavg': 'surface net shortwave radiation [w/m^2]',
                    'snowf_tavg': 'surface snowfall rate [kg/m^2/s]',
                    'soilmoist_s_tav': 'surface soil moisture [kg/m^2]',
                    'soilmoist_rz_ta': 'root zone soil moisture [kg/m^2]',
                    'soilmoist_p_tav': 'profile soil moisture [kg/m^2]',
                    'tair_f_tavg': 'surface near surface air temperature [k]',
                    'wind_f_tavg': 'surface near surface wind speed [m/s]',
                    'tveg_tavg' : 'transpiration [w/m^2]'}
    factors = {'avgsurft_tavg': -273.15,
               'canopint_tavg': 1,
               'evap_tavg': 86400,
               'lwdown_f_tavg': 1,
               'lwnet_tavg': 1,
               'psurf_f_tavg': 0.001,
               'qair_f_tavg': 1,
               'qg_tavg': 1,
               'qh_tavg': 1,
               'qle_tavg': 1,
               'qs_tavg': 86400,
               'qsb_tavg': 86400,
               'qsm_tavg': 86400,
               'rainf_f_tavg': 86400,
               'swe_tavg': 1,
               'swdown_f_tavg': 1,
               'swnet_tavg': 1,
               'snowf_tavg': 1,
               'soilmoist_s_tav': 1,
               'soilmoist_rz_ta': 1,
               'soilmoist_p_tav': 1,
               'tair_f_tavg': -273.15,
               'wind_f_tavg': 0.75,
               'tveg_tavg' : 1}
    types = {'avgsurft_tavg': 'state',
             'canopint_tavg': 'state',
             'evap_tavg': 'flux',
             'lwdown_f_tavg': 'state',
             'lwnet_tavg': 'state',
             'psurf_f_tavg': 'state',
             'qair_f_tavg': 'state',
             'qg_tavg': 'state',
             'qh_tavg': 'state',
             'qle_tavg': 'state',
             'qs_tavg': 'flux',
             'qsb_tavg': 'flux',
             'qsm_tavg': 'flux',
             'rainf_f_tavg': 'flux',
             'swe_tavg': 'state',
             'swdown_f_tavg': 'state',
             'swnet_tavg': 'state',
             'snowf_tavg': 'state',
             'soilmoist_s_tav': 'state',
             'soilmoist_rz_ta': 'state',
             'soilmoist_p_tav': 'state',
             'tair_f_tavg': 'state',
             'wind_f_tavg': 'state',
             'tveg_tavg' : 'state'}

    def __init__(self, step):
        if step == 'daily':
            self.units = {'avgsurft_tavg': 'C',
                          'canopint_tavg': 'mm',
                          'evap_tavg': 'mm-day-1',
                          'lwdown_f_tavg': 'W-m-2',
                          'lwnet_tavg': 'W-m-2',
                          'psurf_f_tavg': 'kpa',
                          'qair_f_tavg': 'kg-kg',
                          'qg_tavg': 'W-m-2',
                          'qh_tavg': 'W-m-2',
                          'qle_tavg': 'W-m-2',
                          'qs_tavg': 'mm-day-1',
                          'qsb_tavg': 'mm-day-1',
                          'qsm_tavg': 'mm-day-1',
                          'rainf_f_tavg': 'mm-day-1',
                          'swe_tavg': 'mm',
                          'swdown_f_tavg': 'W-m-2',
                          'swnet_tavg': 'W-m-2',
                          'snowf_tavg': 'mm',
                          'soilmoist_s_tav': 'kg-m-2',
                          'soilmoist_rz_ta': 'kg-m-2',
                          'soilmoist_p_tav': 'kg-m-2',
                          'tair_f_tavg': 'C',
                          'wind_f_tavg': 'm-s-1',
                          'tveg_tavg' : 'W-m-2'}
        elif step == 'monthly':
            self.units = {'avgsurft_tavg': 'C',
                          'canopint_tavg': 'mm',
                          'evap_tavg': 'mm-month-1',
                          'lwdown_f_tavg': 'W-m-2',
                          'lwnet_tavg': 'W-m-2',
                          'psurf_f_tavg': 'kpa',
                          'qair_f_tavg': 'kg-kg',
                          'qg_tavg': 'W-m-2',
                          'qh_tavg': 'W-m-2',
                          'qle_tavg': 'W-m-2',
                          'qs_tavg': 'mm-month-1',
                          'qsb_tavg': 'mm-month-1',
                          'qsm_tavg': 'mm-month-1',
                          'rainf_f_tavg': 'mm-month-1',
                          'swe_tavg': 'mm',
                          'swdown_f_tavg': 'W-m-2',
                          'swnet_tavg': 'W-m-2',
                          'snowf_tavg': 'mm',
                          'soilmoist_s_tav': 'kg-m-2',
                          'soilmoist_rz_ta': 'kg-m-2',
                          'soilmoist_p_tav': 'kg-m-2',
                          'tair_f_tavg': 'C',
                          'wind_f_tavg': 'm-s-1',
                          'tveg_tavg' : 'W-m-2'} 
        else:
            raise KeyError("The input time step is not supported")
