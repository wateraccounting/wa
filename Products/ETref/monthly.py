# -*- coding: utf-8 -*-
'''
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
'''
# import general python modules
import sys
import pandas as pd
import numpy as np
import calendar
import os
import gdal

# import WA+ modules
from wa.General import raster_conversions as RC
from wa.General import data_conversions as DC
from wa.Products.ETref import daily

def main(Dir, Startdate = '', Enddate = '',
         latlim = [-60, 60], lonlim = [-180, 180], pixel_size = False, cores = False, LANDSAF =  0, SourceLANDSAF=  '', Waitbar = 1):
    """
    This function downloads TRMM3B43 V7 (monthly) data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine.
             It can be 'False' to avoid using parallel computing
             routines.
    Waitbar -- 1 (Default) will print the waitbar	             
    """
    
    print 'Create monthly Reference ET data for period %s till %s' %(Startdate, Enddate)	
		
    # An array of monthly dates which will be calculated            
    Dates = pd.date_range(Startdate,Enddate,freq = 'MS') 												

    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

	# Calculate the ETref day by day for every month														
    for Date in Dates:
					
        # Collect date data				
        Y=Date.year
        M=Date.month
        Mday=calendar.monthrange(Y,M)[1]
        Days=pd.date_range(Date,Date+pd.Timedelta(days=Mday),freq='D')
        StartTime=Date.strftime('%Y')+'-'+Date.strftime('%m')+ '-01' 
        EndTime=Date.strftime('%Y')+'-'+Date.strftime('%m')+'-'+str(Mday)
                   
        # Get ETref on daily basis
        daily(Dir=Dir, Startdate=StartTime,Enddate=EndTime,latlim=latlim, lonlim=lonlim, pixel_size = pixel_size, cores=cores, LANDSAF=LANDSAF, SourceLANDSAF=SourceLANDSAF, Waitbar = 0)

        # Load DEM 
        if not pixel_size:
            nameDEM='DEM_HydroShed_m.tif'
            DEMmap=os.path.join(Dir,'HydroSHED','DEM',nameDEM )
        else:
            DEMmap=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m_reshaped_for_ETref.tif')
        # Get some geo-data to save results
        geo_ET, proj, size_X, size_Y = RC.Open_array_info(DEMmap)
      
        dataMonth=np.zeros([size_Y,size_X])
       
        for Day in Days[:-1]: 
            output_folder_day=os.path.join(Dir,'ETref','Daily')
            DirDay=output_folder_day + '\ETref_mm-day-1_daily_' + Date.strftime('%Y.%m.%d') + '.tif'

            dataDay=gdal.Open(DirDay)
            Dval=dataDay.GetRasterBand(1).ReadAsArray().astype(np.float32)    
            Dval[Dval<0]=0
            dataMonth=dataMonth+Dval
            dataDay=None
         
        # make geotiff file 
        output_folder_month=os.path.join(Dir,'ETref','Monthly')
        if os.path.exists(output_folder_month)==False:       
            os.makedirs(output_folder_month)
        DirMonth=os.path.join(output_folder_month,'ETref_mm-month-1_monthly_'+Date.strftime('%Y.%m.%d') + '.tif')
       
        # Create the tiff file
        DC.Save_as_tiff(DirMonth,dataMonth, geo_ET, proj)

        # Create Waitbar
        if Waitbar == 1:
            amount += 1
            WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)


if __name__ == '__main__':
    main(sys.argv)
