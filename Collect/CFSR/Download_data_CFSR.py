"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/CFSR
"""
# General modules
import os
import pycurl

def Download_data(Date, Version, output_folder, Var):        
    """
    This function downloads CFSR data from the FTP server
				For - CFSR:    ftp://nomads.ncdc.noaa.gov/CFSR/HP_time_series/
				    - CFSRv2:  http://nomads.ncdc.noaa.gov/modeldata/cfsv2_analysis_timeseries/

    Keyword arguments:
    Date -- pandas timestamp day
    Version -- 1 or 2 (1 = CFSR, 2 = CFSRv2)			
    output_folder -- The directory for storing the downloaded files
    Var -- The variable that must be downloaded from the server ('dlwsfc','uswsfc','dswsfc','ulwsfc')
    """
    # Define the filename that must be downloaded     
    if Version == 1:
        filename = Var + '.gdas.' + str(Date.strftime('%Y')) + str(Date.strftime('%m')) + '.grb2'
    if Version == 2:
        filename = Var + '.gdas.' + str(Date.strftime('%Y')) + str(Date.strftime('%m')) + '.grib2'

    try:
         # download the file when it not exist					
        local_filename = os.path.join(output_folder, filename)
        if not os.path.exists(local_filename):
									
            # Create the command and run the command in cmd
            if Version == 1:
                FTP_name = 'ftp://nomads.ncdc.noaa.gov/CFSR/HP_time_series/' + Date.strftime('%Y') + Date.strftime('%m')+ '/' + filename
							
            if Version == 2:
                FTP_name = 'https://nomads.ncdc.noaa.gov/modeldata/cfsv2_analysis_timeseries/' + Date.strftime('%Y') + '/' + Date.strftime('%Y') + Date.strftime('%m')+ '/' + filename

            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, FTP_name)
            fp = open(local_filename, "wb")
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            curl.setopt(pycurl.SSL_VERIFYHOST, 0)
            curl.setopt(pycurl.WRITEDATA, fp)
            curl.perform()
            curl.close()
            fp.close()										
								
    except:
        print 'Was not able to download the CFSR file from the FTP server'
    
    return(local_filename)   