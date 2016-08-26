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
from StandardDef_ETref import GetGeoInfo, CreateGeoTiff
from wa.Products.ETref import daily

def main(Dir, Startdate = '', Enddate = '',
         latlim = [-60, 60], lonlim = [-180, 180], pixel_size = False, cores = False, LANDSAF =  0, SourceLANDSAF=  ''):
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
    """
				
    # An array of monthly dates which will be calculated            
    Dates = pd.date_range(Startdate,Enddate,freq = 'MS') 												

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
        daily(Dir=Dir, Startdate=StartTime,Enddate=EndTime,latlim=latlim, lonlim=lonlim, pixel_size = pixel_size, cores=cores, LANDSAF=LANDSAF, SourceLANDSAF=SourceLANDSAF)

        # Load DEM 
        if not pixel_size:
            nameDEM='DEM_HydroShed_m.tif'
            DEMmap=os.path.join(Dir,'HydroSHED','DEM',nameDEM )
        else:
            DEMmap=os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m_reshaped_for_ETref.tif')
        # Get some geo-data to save results
        NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(DEMmap)
      
        dataMonth=np.zeros([ysize,xsize])
       
        for Day in Days[:-1]: 
            output_folder_day=os.path.join(Dir,'ETref','Daily')
            DirDay=output_folder_day + '\ETref_mm-day_' + Date.strftime('%Y.%m.%d') + '.tif'

            dataDay=gdal.Open(DirDay)
            Dval=dataDay.GetRasterBand(1).ReadAsArray().astype(np.float32)    
            Dval[Dval<0]=0
            dataMonth=dataMonth+Dval
            dataDay=None
         
        # make geotiff file 
        output_folder=os.path.join(Dir,'ETref','Monthly')
        if os.path.exists(output_folder)==False:       
            os.makedirs(output_folder)
        DirMonth=output_folder + '\ETref_mm-month_'+Date.strftime('%Y.%m.%d')
       
        # Create the tiff file
        CreateGeoTiff(DirMonth,dataMonth, NDV, xsize, ysize, GeoT, Projection)

if __name__ == '__main__':
    main(sys.argv)
