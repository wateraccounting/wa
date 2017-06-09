# -*- coding: utf-8 -*-
import sys
import pandas as pd
import calendar
import os

from DataAccess import DownloadData
import wa.General.data_conversions as DC
import wa.General.raster_conversions as RC

def main(Dir, Startdate='', Enddate='',
         latlim=[-50, 50], lonlim=[-180, 180], cores=False, Waitbar = 1):

    """
    This function downloads RFE V2.0 (monthly) data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine.
             It can be 'False' to avoid using parallel computing
             routines.
    Waitbar -- 1 (Default) will print a waitbar             
    """
     # Download data
    print '\nDownload monthly RFE precipitation data for period %s till %s' %(Startdate, Enddate)   
    
    # Check variables
    if not Startdate:
        Startdate = pd.Timestamp('2001-01-01')
    if not Enddate:
        Enddate = pd.Timestamp('Now')
    Dates = pd.date_range(Startdate,  Enddate, freq='MS')

	 # Make directory
    output_folder = os.path.join(Dir, 'Precipitation', 'RFE', 'Monthly/')     
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)  

    for Date in Dates:
        month = Date.month
        year = Date.year
        end_day = calendar.monthrange(year, month)[1]
        Startdate_one_month = '%s-%02s-01' %(year, month)
        Enddate_one_month = '%s-%02s-%02s' %(year, month, end_day)        

        DownloadData(Dir, Startdate_one_month, Enddate_one_month, latlim, lonlim, 0, cores)     
        
        Dates_daily = pd.date_range(Startdate_one_month,  Enddate_one_month, freq='D')

	     # Make directory
        input_folder_daily = os.path.join(Dir, 'Precipitation', 'RFE', 'Daily/')         
        i = 0
        
        for Date_daily in Dates_daily:
            file_name = 'P_RFE.v2.0_mm-day-1_daily_%s.%02s.%02s.tif' %(Date_daily.strftime('%Y'), Date_daily.strftime('%m'), Date_daily.strftime('%d'))      
            file_name_daily_path = os.path.join(input_folder_daily, file_name)
            if os.path.exists(file_name_daily_path):
                if Date_daily == Dates_daily[i]:
                    Raster_monthly = RC.Open_tiff_array(file_name_daily_path)
                else:
                    Raster_monthly += RC.Open_tiff_array(file_name_daily_path) 
            else:
                if Date_daily == Dates_daily[i]:
                    i += 1

        geo_out, proj, size_X, size_Y = RC.Open_array_info(file_name_daily_path)         
        file_name = 'P_RFE.v2.0_mm-month-1_monthly_%s.%02s.01.tif' %(Date.strftime('%Y'), Date.strftime('%m'))
        file_name_output = os.path.join(output_folder, file_name)       
        DC.Save_as_tiff(file_name_output, Raster_monthly, geo_out, projection="WGS84")
        
        if Waitbar == 1:
            amount += 1
            WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
        
if __name__ == '__main__':
    main(sys.argv)
