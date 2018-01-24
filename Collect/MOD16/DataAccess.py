# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD16
"""

# import general python modules
import os
import numpy as np
import pandas as pd
import gdal
import urllib
import urllib2
import re
import glob
from joblib import Parallel, delayed
from bs4 import BeautifulSoup
import requests
import datetime
import math

# Water Accounting modules
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, timestep, Waitbar, cores):
    """
    This function downloads MOD13 16-daily data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -90 and 90)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine. It can be 'False'
             to avoid using parallel computing routines.
    Waitbar -- 1 (Default) will print a waitbar             
    """

    # Check start and end date and otherwise set the date
    if not Startdate:
        Startdate = pd.Timestamp('2000-01-01')
    if not Enddate: 
        Enddate = pd.Timestamp('2014-12-31')
    
    # Make an array of the days of which the ET is taken
    if timestep == 'monthly':
        Dates = pd.date_range(Startdate,Enddate,freq = 'M') 
        TIMESTEP = 'Monthly'
    elif timestep == '8-daily':
        Dates = Make_TimeStamps(Startdate,Enddate)  
        TIMESTEP = '8_Daily'
        
    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    # Make directory for the MODIS ET data
    output_folder=os.path.join(Dir,'Evaporation','MOD16', TIMESTEP)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Download list (txt file on the internet) which includes the lat and lon information for the integrized sinusoidal projection tiles of MODIS
    nameDownloadtext='https://modis-land.gsfc.nasa.gov/pdf/sn_gring_10deg.txt'  
    file_nametext=os.path.join(output_folder,nameDownloadtext.split('/')[-1])
    try:
        try:
            urllib.urlretrieve(nameDownloadtext, file_nametext)
        except:
            data = urllib2.urlopen(nameDownloadtext).read()
            with open(file_nametext, "wb") as fp:
                fp.write(data)
    except:
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)             
        with open(file_nametext, "wb") as fp:
            data = requests.get(nameDownloadtext, verify=False)
            fp.write(data.content)

    # Open text file with tiles which is downloaded before
    tiletext=np.genfromtxt(file_nametext,skip_header=7,skip_footer=1,usecols=(0,1,2,3,4,5,6,7,8,9))
    tiletext2=tiletext[tiletext[:,2]>=-900,:]
            
    # This function converts the values in the text file into horizontal and vertical number of the tiles which must be downloaded to cover the extent defined by the user
    TilesVertical, TilesHorizontal = Tiles_to_download(tiletext2=tiletext2,lonlim1=lonlim,latlim1=latlim)
	
    # Pass variables to parallel function and run
    args = [output_folder, TilesVertical, TilesHorizontal,latlim, lonlim, timestep]
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
    files = glob.glob("*.hdf")																																				
    for f in files:
        os.remove(os.path.join(output_folder, f))      

    # Remove all .txt files	
    files = glob.glob("*.txt")																																				
    for f in files:
        os.remove(os.path.join(output_folder, f))      
													
	return results	

def RetrieveData(Date, args):
    """
    This function retrieves MOD16 ET data for a given date from the
    ftp://ftp.ntsg.umt.edu/ server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, TilesVertical, TilesHorizontal,latlim, lonlim, timestep] = args

    # Collect the data from the MODIS webpage and returns the data and lat and long in meters of those tiles
    try:
        Collect_data(TilesHorizontal,TilesVertical,Date,output_folder, timestep)
    except:
        print "Was not able to download the file"  
    
    # Define the output name of the collect data function
    name_collect = os.path.join(output_folder, 'Merged.tif')	         

    # Reproject the MODIS product to epsg_to
    epsg_to ='4326'
    name_reprojected = RC.reproject_MODIS(name_collect, epsg_to)				

    # Clip the data to the users extend			
    data, geo = RC.clip_data(name_reprojected, latlim, lonlim)
		
    if timestep == 'monthly':	
         ETfileName = os.path.join(output_folder, 'ET_MOD16A2_mm-month-1_monthly_'+Date.strftime('%Y')+'.' + Date.strftime('%m')+'.01.tif')
    elif timestep == '8-daily':
         ETfileName = os.path.join(output_folder, 'ET_MOD16A2_mm-8days-1_8-daily_'+Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + Date.strftime('%d') + '.tif')

    DC.Save_as_tiff(name=ETfileName, data=data, geo=geo, projection='WGS84')
                   				
    # remove the side products       
    os.remove(os.path.join(output_folder, name_collect))
    os.remove(os.path.join(output_folder, name_reprojected))                

    return()

    
def Tiles_to_download(tiletext2,lonlim1,latlim1):
    '''
    Defines the MODIS tiles that must be downloaded in order to cover the latitude and longitude limits
	
    Keywords arguments:
    tiletext2 -- 'C:/file/to/path/' to path of the txt file with all the MODIS tiles extents
    lonlim1 -- [ymin, ymax] (longitude limits of the chunk or whole image)
    latlim1 -- [ymin, ymax] (latitude limits of the chunk or whole image) 	
    '''  
	
    # calculate min and max longitude and latitude
    # lat down    lat up      lon left     lon right
    tiletextExtremes=np.empty([len(tiletext2),6])
    tiletextExtremes[:,0]=tiletext2[:,0]
    tiletextExtremes[:,1]=tiletext2[:,1]
    tiletextExtremes[:,2]=np.minimum(tiletext2[:,3],tiletext2[:,9])
    tiletextExtremes[:,3]=np.maximum(tiletext2[:,5],tiletext2[:,7])
    tiletextExtremes[:,4]=np.minimum(tiletext2[:,2],tiletext2[:,4])
    tiletextExtremes[:,5]=np.maximum(tiletext2[:,6],tiletext2[:,8])
    
    # Define the upper left tile
    latlimtiles1UL=tiletextExtremes[np.logical_and(tiletextExtremes[:,2]<=latlim1[1],tiletextExtremes[:,3]>=latlim1[1])]#tiletext2[:,3]>=latlim[0],tiletext2[:,4]>=latlim[0],tiletext2[:,5]>=latlim[0],tiletext2[:,6]>=latlim[0],tiletext2[:,7]>=latlim[0]))]
    latlimtilesUL=latlimtiles1UL[np.logical_and(latlimtiles1UL[:,4]<=lonlim1[0],latlimtiles1UL[:,5]>=lonlim1[0])]
    
    # Define the lower right tile
    latlimtiles1LR=tiletextExtremes[np.logical_and(tiletextExtremes[:,2]<=latlim1[0],tiletextExtremes[:,3]>=latlim1[0])]#tiletext2[:,3]>=latlim[0],tiletext2[:,4]>=latlim[0],tiletext2[:,5]>=latlim[0],tiletext2[:,6]>=latlim[0],tiletext2[:,7]>=latlim[0]))]
    latlimtilesLR=latlimtiles1LR[np.logical_and(latlimtiles1LR[:,4]<=lonlim1[1],latlimtiles1LR[:,5]>=lonlim1[1])]
    
    # Define the total tile
    TotalTiles=np.vstack([latlimtilesUL,latlimtilesLR])
    
    # Find the minimum horizontal and vertical tile value and the maximum horizontal and vertical tile value
    TilesVertical=[TotalTiles[:,0].min(), TotalTiles[:,0].max()]
    TilesHorizontal=[TotalTiles[:,1].min(), TotalTiles[:,1].max()]
    return(TilesVertical,TilesHorizontal)
    
    
def Collect_data(TilesHorizontal,TilesVertical,Date,output_folder,timestep):
    '''
    This function downloads all the needed MODIS tiles from ftp.ntsg.umt.edu/pub/MODIS/NTSG_Products/MOD16/MOD16A2_MONTHLY.MERRA_GMAO_1kmALB/ as a hdf file.

    Keywords arguments:
    TilesHorizontal -- [TileMin,TileMax] max and min horizontal tile number	
    TilesVertical -- [TileMin,TileMax] max and min vertical tile number	
    Date -- 'yyyy-mm-dd' 				
    output_folder -- 'C:/file/to/path/'	
    '''
    
    # Make a new tile for the data
    sizeX=int(TilesHorizontal[1]-TilesHorizontal[0]+1)*1200
    sizeY=int(TilesVertical[1]-TilesVertical[0]+1)*1200
    DataTot=np.ones((sizeY,sizeX))* -9999
    
    # Make a new tile for the lat and long info
    LatMet=np.zeros((sizeY))
    LongMet=np.zeros((sizeX))
    
    # Create the Lat and Long of the MODIS tile in meters
    for Vertical in range(int(TilesVertical[0]),int(TilesVertical[1])+1):
        Distance=926.625 # resolution of a MODIS pixel in meter
        countY=int((TilesVertical[1]-TilesVertical[0]+1)-(Vertical-TilesVertical[0]))
        LatMet[int((countY-1)*1200):int((countY)*1200)]=np.linspace(((8-Vertical)*1200+0.5)*Distance,((8-Vertical)*1200+1199.5)*Distance,1200)
                          
        for Horizontal in range(int(TilesHorizontal[0]),int(TilesHorizontal[1])+1):
            countX=int(Horizontal-TilesHorizontal[0]+1)
            LongMet[int((countX-1)*1200):int((countX)*1200)]=np.linspace(((Horizontal-18)*1200+0.5)*Distance,((Horizontal-18)*1200+1199.5)*Distance,1200)
         
            # Download the MODIS FPAR data
            if timestep == 'monthly':            
                url = 'http://files.ntsg.umt.edu/data/NTSG_Products/MOD16/MOD16A2_MONTHLY.MERRA_GMAO_1kmALB/Y%s/M%02s/' %(Date.strftime('%Y'), Date.strftime('%m')) 

            if timestep == '8-daily':            
                url = 'http://files.ntsg.umt.edu/data/NTSG_Products/MOD16/MOD16A2.105_MERRAGMAO/Y%s/D%03s/' %(Date.strftime('%Y'), Date.strftime('%j')) 

            # Get files on FTP server
            f = urllib2.urlopen(url)										
																			
            # Sum all the files on the server												
            soup = BeautifulSoup(f, "lxml")
										
            try:
													
                for i in soup.findAll('a', attrs = {'href': re.compile('(?i)(hdf)$')}):
													
                    # Find the file with the wanted tile number
                    nameHDF=str(i)
                    HDF_name = nameHDF.split('>')[-2][:-3]
                    Hfile=HDF_name[18:20]
                    Vfile=HDF_name[21:23]
                    if int(Vfile) is int(Vertical) and int(Hfile) is int(Horizontal):
    
                        HTTP_name = url + HDF_name
                        output_name = os.path.join(output_folder, HDF_name)
                        if not os.path.isfile(output_name):
                            downloaded = 0																				
                            while downloaded == 0:																				
																				
                                urllib.urlretrieve(HTTP_name,output_name)
    
                                statinfo = os.stat(output_name)																									
                                # Say that download was succesfull		
                                if int(statinfo.st_size) > 1000:																								
                                   downloaded = 1

             
                        # Open .hdf only band with ET and collect all tiles to one array
                        dataset=gdal.Open(output_name)
                        sdsdict=dataset.GetMetadata('SUBDATASETS')
                        sdslist =[sdsdict[k] for k in sdsdict.keys() if '_1_NAME' in k]
                        sds=[]
               												
                        sds=gdal.Open(sdslist[0])
                        data = np.float_(sds.ReadAsArray()) 
                        countYdata=(TilesVertical[1]-TilesVertical[0]+2)-countY
                        DataTot[(int(countYdata)-1)*1200:int(countYdata)*1200,(int(countX)-1)*1200:int(countX)*1200]=data*0.1
                        DataTot[DataTot>3000]=-9999
                        sds=None
                        del data
           
            except:   
                proj='PROJCS["unnamed",GEOGCS["Unknown datum based upon the custom spheroid",DATUM["Not specified (based on custom spheroid)",SPHEROID["Custom spheroid",6371007.181,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Sinusoidal"],PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'																													 
                data=np.ones((1200, 1200)) * (-9999)
                countYdata=(TilesVertical[1] - TilesVertical[0] + 2) - countY
                DataTot[(countYdata - 1) * 1200:countYdata * 1200,(countX - 1) * 1200:countX * 1200] = data * 0.1

	# Make geotiff file      
    name2 = os.path.join(output_folder, 'Merged.tif')
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(name2, DataTot.shape[1], DataTot.shape[0], 1, gdal.GDT_Float32, ['COMPRESS=LZW'])     
    try:
        dst_ds.SetProjection(proj)
    except:
        proj='PROJCS["unnamed",GEOGCS["Unknown datum based upon the custom spheroid",DATUM["Not specified (based on custom spheroid)",SPHEROID["Custom spheroid",6371007.181,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Sinusoidal"],PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'																													 
        x1 = (TilesHorizontal[0] - 18) * 1200 * Distance
        x4 = (TilesVertical[0] - 9) * 1200 * -1 * Distance
        geo = [x1, Distance, 0.0, x4, 0.0, -Distance]															
        geo_t = tuple(geo)        
        dst_ds.SetProjection(proj)		
        									
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform(geo_t)
    dst_ds.GetRasterBand(1).WriteArray(DataTot)
    dst_ds = None
    sds = None
				
    return(DataTot,LatMet,LongMet)

def Make_TimeStamps(Startdate,Enddate):
    '''
    This function determines all time steps of which the FPAR must be downloaded   
    The time stamps are 8 daily.
	
    Keywords arguments:
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    '''
    
    # Define the DOY and year of the start day
    DOY = datetime.datetime.strptime(Startdate,'%Y-%m-%d').timetuple().tm_yday
    Year = datetime.datetime.strptime(Startdate,'%Y-%m-%d').timetuple().tm_year

    # Define the year of the end day
    YearEnd = datetime.datetime.strptime(Enddate,'%Y-%m-%d').timetuple().tm_year

    # Change the DOY of the start day into a DOY of MODIS day (8-daily) and create new startdate
    DOYstart = int(math.floor(DOY / 8.0) * 8) + 1
    DOYstart = str('%s-%s' %(DOYstart, Year))
    Day = datetime.datetime.strptime(DOYstart, '%j-%Y')
    Month = '%02d' % Day.month
    Day = '%02d' % Day.day
    Startdate = (str(Year) + '-' + str(Month) + '-' + str(Day))
				
    # Create the start and end data for the whole year				
    YearStartDate = pd.date_range(Startdate, Enddate, freq = 'AS')
    YearEndDate = pd.date_range(Startdate, Enddate, freq = 'A')
				
    # Define the amount of years that are involved				
    AmountOfYear = YearEnd - Year

    # If the startday is not in the same year as the enddate
    if AmountOfYear > 0:
        for i in range(0, AmountOfYear+1):
            if i is 0:
                Startdate1 = Startdate
                Enddate1 = YearEndDate[0]
                Dates = pd.date_range(Startdate1, Enddate1, freq = '8D')
            if i is AmountOfYear:
                Startdate1 = YearStartDate[-1]
                Enddate1 = Enddate
                Dates1 = pd.date_range(Startdate1, Enddate1, freq = '8D')
                Dates = Dates.union(Dates1)
            if (i is not AmountOfYear and i is not 0):
                Startdate1 = YearStartDate[i-AmountOfYear-1]              
                Enddate1 = YearEndDate[i] 
                Dates1 = pd.date_range(Startdate1, Enddate1, freq = '8D')
                Dates = Dates.union(Dates1)
																								
    # If the startday is in the same year as the enddate               
    if AmountOfYear is 0:
        Dates = pd.date_range(Startdate, Enddate, freq = '8D')
    
    return(Dates)
            