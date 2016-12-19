# -*- coding: utf-8 -*-

# General modules
import numpy as np
import calendar
import os
import gdal
import pandas as pd
import requests
from joblib import Parallel, delayed

# Water Accounting modules
from wa import WebAccounts
import wa.General.data_conversions as DC

def DownloadData(Dir, Var, Startdate, Enddate, latlim, lonlim, cores,
                 TimeCase, CaseParameters):    
    """
    This function downloads GLDAS three-hourly, daily or monthly data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Var -- ['wind','qair'] :For all variable codes: VariablesInfo('day').descriptions.keys()
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
        url = 'http://%s:%s@hydro1.gesdisc.eosdis.nasa.gov:80/dods/GLDAS_NOAH025SUBP_3H' %(username,password)
								
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
        url = 'http://%s:%s@hydro1.gesdisc.eosdis.nasa.gov:80/dods/GLDAS_NOAH025SUBP_3H' %(username,password)
								
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
        url = 'http://%s:%s@hydro1.gesdisc.eosdis.nasa.gov:80/dods/GLDAS_NOAH025_M' %(username,password)
								
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
				
    # Define the variable string name    				
    VarStr = VarInfo.names[Var]

    # Create one parameter with all the required arguments
    args = [path, url, Var, VarStr, VarInfo,
            TimeCase, xID, yID, lonlim, latlim, CaseParameters, username, password]
												
    # Pass variables to parallel function and run												
    if not cores:
        for Date in Dates:
            RetrieveData_fcn(Date, args)
        results = True
    else:
        results = Parallel(n_jobs = cores)(delayed(RetrieveData_fcn)(Date, args) for Date in Dates)
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
                    zID = int((Date.toordinal() - 730174) * 8 + int(period) - 1) - 1
			
                    # total URL
                    url_GLDAS = url + '.ascii?%s[%s][%s:1:%s][%s:1:%s]' %(Var,zID,yID[0],yID[1],xID[0],xID[1])
			
                    # open URL
                    dataset = requests.get(url_GLDAS, allow_redirects=False)
                    try:
                        get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True)	
                    except:
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
            latlimGLDAS = yID[1] * 0.25 - 60

            # Save to geotiff file     
            geo = [lonlimGLDAS,0.25,0,latlimGLDAS,0,-0.25]
            DC.Save_as_tiff(name=BasinDir, data=np.flipud(data[:,:]), geo=geo, projection="WGS84")
               											
            print 'File for ' + Date.strftime('%Y-%m-%d') + ' created.'
            
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
            zID_start = int((Date.toordinal() - 730174) * 8) - 1
            zID_end = zID_start + 7												

            # define total url
            url_GLDAS = url + '.ascii?%s[%s:1:%s][%s:1:%s][%s:1:%s]' %(Var,zID_start,zID_end,yID[0],yID[1],xID[0],xID[1])
                 
            # if not downloaded try to download file																	
            while downloaded == 0:
                try:																	
                    																	
                    # open URL
                    dataset = requests.get(url_GLDAS, allow_redirects=False)
                    try:
                        get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True)	
                    except:
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
                        data_end = data_end + VarInfo.factors[Var]
                    else:
                        data_end = data_end * VarInfo.factors[Var]
                    data_end[data_end < -9999] = -9999

                    # define geo		
                    lonlimGLDAS = xID[0] * 0.25 - 180
                    latlimGLDAS = yID[1] * 0.25 - 60
																				
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

    # Check if the outputfile already excists						
    if not os.path.isfile(BasinDir):
            
        # Reset the begin parameters for downloading												
        downloaded = 0   
        N=0  										
												
        # Create the time dimension
        zID = (Y - 2000) * 12 + M - 3											

        # define total url
        url_GLDAS = url + '.ascii?%s[%s][%s:1:%s][%s:1:%s]' %(Var,zID,yID[0],yID[1],xID[0],xID[1])
                 
        # if not downloaded try to download file																	
        while downloaded == 0:
            try:																	
                    																	
                # open URL
                dataset = requests.get(url_GLDAS, allow_redirects=False)
                try:
                    get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True)	
                except:
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
            latlimGLDAS = yID[1] * 0.25 - 60

            # Save to geotiff file    
            geo = [lonlimGLDAS,0.25,0,latlimGLDAS,0,-0.25]
            DC.Save_as_tiff(name=BasinDir, data=np.flipud(data[:,:]), geo=geo, projection="WGS84")	
                												
            print 'File for ' + Date.strftime('%Y-%m-%d') + ' created.'
            
            # Delete data and text file												
            del data
            os.remove(pathtext)
    
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
    factors = {'avgsurft': -273.15,
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
               'tsoil1': -273.15,
               'tsoil2': -273.15,
               'tsoil3': -273.15,
               'tsoil4': -273.15,
               'tair': -273.15,
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
             'swdown': 'state',
             'swnet': 'state',
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
