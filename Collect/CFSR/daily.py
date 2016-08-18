'''
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/CFSR
'''

# General modules
import sys
import pandas as pd

# WA+ modules
from wa.Collect.CFSR.DataAccess_CFSR import CollectData


def main(Dir, Vars, Startdate='', Enddate='',
         latlim=[-90, 90], lonlim=[-180, 180], cores=False):
    """
    This function downloads daily CFSR data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Vars -- ['dlwsfc','dswsfc','ulwsfc',or/and 'uswsfc']
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine.
             It can be 'False' to avoid using parallel computing
			routines.
    """
    # Define startdate and enddate
    if not Startdate:
        Startdate = pd.Timestamp('1979-01-01')
    if not Enddate: 
        Enddate = pd.Timestamp('now')

    # Loops over the wanted variables
    for Var in Vars:
       	
        # Defines all the dates that will be calculated								
        Dates = pd.date_range(Startdate,Enddate,freq = 'D') 							

		# If dates are  older dthan April 2011 than download CFSR						
        if Dates[0]<pd.Timestamp(pd.datetime(2011, 4, 1)) and Dates[-1]<pd.Timestamp(pd.datetime(2011, 4, 1)):								
 
            # download CFSR data       
            CollectData(Dir, Var, Startdate,Enddate,latlim,lonlim, cores, 1)

		# If dates are older than April 2011 than download CFSR, for the other dates CFSRv2		 
        if Dates[0]<pd.Timestamp(pd.datetime(2011, 4, 1)) and Dates[-1]>=pd.Timestamp(pd.datetime(2011, 4, 1)):
  
            # Define CFSR startdate and enddate         
            EnddateCFSR=pd.Timestamp(pd.datetime(2011, 3, 31))
            StartdateCFSRv2=pd.Timestamp(pd.datetime(2011, 4, 1))
                
            # download CFSR data
            CollectData(Dir, Var, Startdate,EnddateCFSR,latlim,lonlim, cores, 1)
            
            # download CFSRv2 data
            CollectData(Dir, Var, StartdateCFSRv2,Enddate,latlim,lonlim, cores, 2)												

		# If dates are younger than April 2011 than download CFSRv2	      
        if Dates[0] >= pd.Timestamp(pd.datetime(2011, 4, 1)): 
  
            # download CFSRv2 data
            CollectData(Dir, Var, Startdate, Enddate, latlim, lonlim, cores, 2)												
       
if __name__ == '__main__':
    main(sys.argv)