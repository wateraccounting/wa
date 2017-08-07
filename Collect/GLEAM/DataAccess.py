# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/GLEAM
"""

# import general python modules
import os
import numpy as np
import pandas as pd
import glob
from joblib import Parallel, delayed
import paramiko
import calendar
from netCDF4 import Dataset

# Water Accounting modules
import wa.General.data_conversions as DC
from wa import WebAccounts

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar, cores, TimeCase):
    """
    This function downloads GLEAM ET data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine. It can be 'False'
             to avoid using parallel computing routines.
    Waitbar -- 1 (Default) will print a waitbar             
    """
    # Check start and end date and otherwise set the date
    if not Startdate:
        Startdate = pd.Timestamp('2003-01-01')
    if not Enddate: 
        Enddate = pd.Timestamp('2015-12-31')

    # Make an array of the days of which the ET is taken
    YearsDownloadstart = str(Startdate[0:4])
    YearsDownloadend = str(Enddate[0:4])
    Years = range(int(YearsDownloadstart),int(YearsDownloadend)+1)  

    # String Parameters
    if TimeCase == 'daily':
        VarCode = 'ET_GLEAM.V3.1b_mm-day-1_daily'
        FTPprefix = 'data/v3.1b/'
        TimeFreq = 'D'
        Folder_name = 'Daily'        
        
    elif TimeCase == 'monthly':
        VarCode = 'ET_GLEAM.V3.1b_mm-month-1_monthly'
        FTPprefix = 'data/v3.1b/'
        TimeFreq = 'M'
        Folder_name = 'Monthly'
        
        # Get end of month for Enddate
        monthDownloadend = str(Enddate[5:7])
        End_month = calendar.monthrange(int(YearsDownloadend),int(monthDownloadend))[1]
        Enddate = '%d-%02d-%d' %(int(YearsDownloadend),int(monthDownloadend),int(End_month)) 
    else:
        raise KeyError("The input time interval is not supported")
             
    Dates = pd.date_range(Startdate, Enddate, freq = TimeFreq)
   
    # Make directory for the MODIS ET data
    output_folder=os.path.join(Dir,'Evaporation', 'GLEAM', Folder_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
	# Check variables
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

    # Collect the data from the GLEAM webpage and returns the data and lat and long in meters of those tiles
    try:
        Collect_data(FTPprefix, Years, output_folder, Waitbar)
    except:
        print "Was not able to download the file"  

    # Create Waitbar
    print '\nProcess the GLEAM data'
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Pass variables to parallel function and run
    args = [output_folder, latlim, lonlim, VarCode, TimeCase]
    if not cores:
        for Date in Dates:
            RetrieveData(Date, args)
            if Waitbar == 1:
                amount += 1
                WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(RetrieveData)(Date, args)
                                         for Date in Dates)
                               
    # Remove all .hdf files	
    os.chdir(output_folder)
    files = glob.glob("*.nc")																																				
    for f in files:
        os.remove(os.path.join(output_folder, f))        
									
	return(results)		

def RetrieveData(Date, args):
    """
    This function retrieves GLEAM ET data for a given date from the
    www.gleam.eu server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, latlim, lonlim, VarCode, TimeCase] = args

    # Adjust latlim to GLEAM dataset
    latlim1=[latlim[1]*-1, latlim[0]*-1]
    
    # select the spatial dataset
    Ystart=int(np.floor((latlim1[0]+90)/0.25))
    Yend=int(np.ceil((latlim1[1]+90)/0.25))
    Xstart=int(np.floor((lonlim[0]+180)/0.25))
    Xend=int(np.ceil((lonlim[1]+180)/0.25))    
       
    Year=Date.year
    Month=Date.month   
    
    filename='E_' + str(Year) + '_GLEAM_v3.1b.nc'
    local_filename = os.path.join(output_folder, filename)

    f = Dataset(local_filename,mode='r')
    
    if TimeCase == 'monthly':

        # defines the start and end of the month
        Datesend1=str(Date)
        Datesend2=Datesend1.replace(Datesend1[8:10],"01")
        Datesend3=Datesend2[0:10]
        Datesend4=Datesend1[0:10]
        Datestart = pd.date_range(Datesend3,Datesend4,freq = 'MS')
        
        # determine the DOY-1 and DOYend (those are use to define the temporal boundaries of the yearly data)
        DOY=int(Datestart[0].strftime('%j'))
        DOYend=int(Date.strftime('%j'))
        DOYDownload=DOY-1
        Day = 1
 
        Data = f.variables['E'][DOYDownload:DOYend,Xstart:Xend,Ystart:Yend]
        data=np.array(Data)
        f.close()

        # Sum ET data in time and change the no data value into -999
        dataSum=sum(data,1)
        dataSum[dataSum<-100]=-999.000
        dataCor=np.swapaxes(dataSum,0,1)
       
    if TimeCase == 'daily':  
        Day = Date.day    

        # Define the DOY, DOY-1 is taken from the yearly dataset
        DOY=int(Date.strftime('%j'))
        DOYDownload=DOY-1

        Data = f.variables['E'][DOYDownload,Xstart:Xend,Ystart:Yend]
        data=np.array(Data)
        f.close()
    
        data[data<-100]=-999.000
        dataCor=np.swapaxes(data,0,1)
        
    # The Georeference of the map
    geo_in=[lonlim[0], 0.25, 0.0, latlim[1], 0.0, -0.25]   

    # Name of the map
    dataset_name=VarCode + '_' + str(Year) + '.' + str(Month).zfill(2)  + '.' + str(Day).zfill(2) + '.tif'
    output_file=os.path.join(output_folder, dataset_name)
        
    # save data as tiff file
    DC.Save_as_tiff(name=output_file, data=dataCor, geo=geo_in, projection="WGS84")

    return True

    
def Collect_data(FTPprefix,Years,output_folder, Waitbar):
    '''
    This function downloads all the needed GLEAM files from hydras.ugent.be as a nc file.

    Keywords arguments:
    FTPprefix -- FTP path to the GLEAM data
    Date -- 'yyyy-mm-dd' 				
    output_folder -- 'C:/file/to/path/'	
    '''
    # account of the SFTP server (only password is missing)
    server='hydras.ugent.be'
    portnumber=2225

    username, password = WebAccounts.Accounts(Type='GLEAM')
  
    # Create Waitbar
    print '\nDownload GLEAM data'
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount2 = len(Years)
        amount2 = 0
        WaitbarConsole.printWaitBar(amount2, total_amount2, prefix = 'Progress:', suffix = 'Complete', length = 50)

    
    for year in Years:
        directory = os.path.join(FTPprefix, '%d' %year)  
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, port=portnumber, username=username, password=password)
        ftp=ssh.open_sftp()
        ftp.chdir(directory)
    
        filename='E_' + str(year) + '_GLEAM_v3.1b.nc'
        local_filename = os.path.join(output_folder, filename)
        
        if not os.path.exists(local_filename):
            ftp.get(filename, local_filename)
            
        if Waitbar == 1:       
            amount2 += 1
            WaitbarConsole.printWaitBar(amount2, total_amount2, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    
    ftp.close()
    ssh.close()
				
    return()