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
from osgeo import osr, gdal
import urllib
import re
import math
from ftplib import FTP
import pycurl
from joblib import Parallel, delayed

# Water Accounting modules
from wa import WebAccounts

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, cores):
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
    """

    # Check start and end date and otherwise set the date
    if not Startdate:
        Startdate = pd.Timestamp('2000-01-01')
    if not Enddate: 
        Enddate = pd.Timestamp('2014-12-31')
    
    # Make an array of the days of which the ET is taken
    Dates = pd.date_range(Startdate,Enddate,freq = 'M')    
    
    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    if latlim[0] < -90 or latlim[1] > 90:
        print 'Latitude above 90N or below 90S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0],-90)
        latlim[1] = np.min(latlim[1],90)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0],-180)
        lonlim[1] = np.min(lonlim[1],180)
        
    # Make directory for the MODIS ET data
    output_folder=os.path.join(Dir,'Evaporation','MOD16/')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # Part to select the tiles
    
    # Download list (txt file on the internet) which includes the lat and lon information for the integrized sinusoidal projection tiles of MODIS
    nameDownloadtext='http://modis-land.gsfc.nasa.gov/pdf/sn_gring_10deg.txt'  
    file_nametext=output_folder + nameDownloadtext.split('/')[-1]
    urllib.urlretrieve(nameDownloadtext,file_nametext)
          
    # Set start variables for chunks (chunks are used when the area is to large)    
    IsHorTilesNeeded=0
    IsVerTilesNeeded=0
    VerticalTiles=1
    HorizontalTiles=1
    
    # Cut in chunks if the latlim and lonlim are to large, to prevent for memory errors
    if latlim[1]-latlim[0]>5.1:
        VerticalTiles=int(math.ceil((latlim[1]-latlim[0])/float(5)))
        IsVerTilesNeeded=1
        LatChunk=np.arange(latlim[0],latlim[1],5)
        LatChunk=np.append(LatChunk,latlim[1])
    else:
        LatChunk=[latlim[0],latlim[1]]
        
    if lonlim[1]-lonlim[0]>5.1:
        HorizontalTiles=int(math.ceil((lonlim[1]-lonlim[0])/float(5)))
        IsHorTilesNeeded=1
        LonChunk=np.arange(lonlim[0],lonlim[1],5)
        LonChunk=np.append(LonChunk,lonlim[1])
    else:
        LonChunk=[lonlim[0],lonlim[1]]
    
    latname=0
	
    # Start loop of the chunks    
    for TileVertical in range(0, int(VerticalTiles)):
					
        # Give latitude limits of the chunks					
        latlim1 = [LatChunk[TileVertical], LatChunk[TileVertical+1]]
        latname = latname + 1
        lonname = 0
        for TileHorizontal in range(0,int(HorizontalTiles)):
									
            # Give longitude limits of the chunks	 									
            lonlim1 = [LonChunk[TileHorizontal], LonChunk[TileHorizontal+1]]
            lonname = lonname+1
                
            # Open text file with tiles which is downloaded before
            tiletext=np.genfromtxt(file_nametext,skip_header=7,skip_footer=1,usecols=(0,1,2,3,4,5,6,7,8,9))
            tiletext2=tiletext[tiletext[:,2]>=-900,:]
            
            # This function converts the values in the text file into horizontal and vertical number of the tiles which must be downloaded to cover the extent defined by the user
            TilesVertical, TilesHorizontal = Tiles_to_download(tiletext2=tiletext2,lonlim1=lonlim1,latlim1=latlim1)
            
            # Pass variables to parallel function and run
            args = [output_folder, TilesVertical, TilesHorizontal, IsVerTilesNeeded, IsHorTilesNeeded, lonlim1, latlim1, lonname, latname]
            if not cores:
                for Date in Dates:
                     RetrieveData(Date, args)
                results = True
            else:
                results = Parallel(n_jobs=cores)(delayed(RetrieveData)(Date, args)
                                                 for Date in Dates)
    # Remove all .hdf files
    for f in os.listdir(output_folder):
        if re.search(".hdf", f) or re.search(".txt", f):
            os.remove(os.path.join(output_folder, f))
												
    # If chunks are used, than merge to one picture      
    if IsHorTilesNeeded!=0 or IsVerTilesNeeded!=0:
        for Date in Dates:
            TotSizeY=int((latlim[1]-latlim[0])*200)
            TotSizeX=int((lonlim[1]-lonlim[0])*200)
            TotData=np.zeros((TotSizeY,TotSizeX))
            YtotDataStart=0
            YtotDataEnd=0
    
            for YnameChunk in range(int(VerticalTiles),0,-1):
                YtotDataStart=YtotDataEnd
                YtotDataEnd=int(YtotDataStart+(LatChunk[YnameChunk]-LatChunk[YnameChunk-1])*200)
                XtotDataStart=0
                XtotDataEnd=0
                for XnameChunk in range(1,int(HorizontalTiles)+1):
                    XtotDataStart=XtotDataEnd
                    XtotDataEnd=int(XtotDataStart+(LonChunk[XnameChunk]-LonChunk[XnameChunk-1])*200)
                    file_name=os.path.join(output_folder, 'ET_MOD16A2_mm-month-1_monthly_'+Date.strftime('%Y')+'.' + Date.strftime('%m')+'.01_chunk_h' + str(XnameChunk) + 'v'+ str(YnameChunk) + '.tif')
                    fileopen=gdal.Open(file_name)
                    arrayChunk=np.array(fileopen.GetRasterBand(1).ReadAsArray())
                    TotData[YtotDataStart:YtotDataEnd,XtotDataStart:XtotDataEnd]=arrayChunk
                    fileopen=None          
                    os.remove(file_name)
            
            ETfileName = os.path.join(output_folder, 'ET_MOD16A2_mm-month-1_monthly_'+Date.strftime('%Y')+'.' + Date.strftime('%m')+'.01.tif')
            TotData=np.flipud(TotData)
            Save_as_Gtiff(TotData,ETfileName,lonlim,latlim)           
        
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
    [output_folder, TilesVertical, TilesHorizontal, IsVerTilesNeeded, IsHorTilesNeeded, lonlim1, latlim1, lonname, latname] = args

    # Collect the data from the MODIS webpage and returns the data and lat and long in meters of those tiles
    DataTot, LatMet, LongMet = Collect_data(TilesHorizontal,TilesVertical,Date,output_folder)
                
    # Make the new latitude and longitude for the WGS84 projection
    Latitude=np.zeros((int(DataTot.shape[0]),1))
    Longitude=np.zeros((int(DataTot.shape[0]),int(DataTot.shape[1])))
                    
    PerimeterEarth=6371007.181
                
    # Calculate the integrized sinusoidal projection latitude and longitude for every pixel of the MODIS tile
    for lat in range(0,int(DataTot.shape[0])):
        Latitude[lat]=LatMet[lat]/PerimeterEarth*180/3.14159265359
        for lon in range(0,int(DataTot.shape[1])):
            Longitude[lat,lon]=LongMet[lon]/(PerimeterEarth*math.cos(Latitude[lat]*(3.14159265359/180)))*(180/3.14159265359)
                
    # Make new grid for new projected dataset
    LatStep=int(abs(latlim1[1]-latlim1[0])/0.005)
    LatPro=np.linspace(latlim1[0]+0.01,(latlim1[1]+0.005),LatStep)+0.00025
    LonStep=int(abs(lonlim1[1]-lonlim1[0])/0.005)
    LonPro=np.linspace(lonlim1[0]+0.005,(lonlim1[1]-0.01),LonStep)+0.00025
    A=np.zeros((LatStep,LonStep))
                
    # Find the nearest value in the integrized sinusoidal projection for the WGS84 projection
    Kolom=-1
    for i in LatPro:
        Rij=-1
        Kolom=Kolom+1
        Nearest=find_nearest(Latitude,i)
        Colomn=np.where(np.any(Latitude==Nearest, axis=1))
        for j in LonPro:   
            Rij=Rij+1
            Nearest2=find_nearest(Longitude[int(Colomn[0]),:],j)
            Row=np.where(Longitude[int(Colomn[0]),:]==Nearest2)
            A[Kolom,Rij]=DataTot[int(DataTot.shape[0])-int(Colomn[0]),int(Row[0])]
                
                
    # Save results as Gtiff
    if IsHorTilesNeeded==0 and IsVerTilesNeeded==0:
        ETfileName = os.path.join(output_folder, 'ET_MOD16A2_mm-month-1_monthly_'+Date.strftime('%Y')+'.' + Date.strftime('%m')+'.01.tif')
        Save_as_Gtiff(A,ETfileName,lonlim1,latlim1)                     
                    
    else:
        ETfileName = os.path.join(output_folder, 'ET_MOD16A2_mm-month-1_monthly_'+Date.strftime('%Y')+'.' + Date.strftime('%m')+'.01_chunk_h' + str(lonname) + 'v'+ str(latname) + '.tif')
        Save_as_Gtiff(A,ETfileName,lonlim1,latlim1) 

    return True

def find_nearest(array,value):
    '''
	This function finds the nearest value in a column. 
		
    Keywords arguments:
    array -- [] numpy 1D array
    value -- value of which the nearest number must be found within the array
	'''
    
    # This function find the nearest value of an array
    idx = (np.abs(array-value)).argmin()
    return array[idx]
    
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
    
    
def Collect_data(TilesHorizontal,TilesVertical,Date,output_folder):
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
    DataTot=np.zeros((sizeY,sizeX))
    
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
         
            # Download the MODIS ET data by using pycurl     
            login = 0									
            while login == 0:
                try:							
                   ftp=FTP("ftp.ntsg.umt.edu", "", "")
                   ftp.login()
                   login = 1	
                except:
                   login = 0	
            pathFTP='/pub/MODIS/NTSG_Products/MOD16/MOD16A2_MONTHLY.MERRA_GMAO_1kmALB/Y'+ Date.strftime('%Y')+'/M' + Date.strftime('%m')+'/'
            ftp.cwd(pathFTP)   
            data = []
            ftp.dir(data.append)

            searchname='MOD16A2.A'+Date.strftime('%Y')+'M'+Date.strftime('%m')+'.h'+ str(Horizontal).zfill(2)+'v'+ str(Vertical).zfill(2)
            total=[]
            for i in data:
                if re.search(searchname,i):
                    total=i
            
            N=0
												
            try:# open http and download whole .hdf       
                try:
                    nameTotal=total.split( )[8]
                    file_name=output_folder + nameTotal
                    FTP_name='ftp://ftp.ntsg.umt.edu'+pathFTP+nameTotal
                    if  os.path.isfile(file_name):
                        print "file ", file_name, " already exists"
                    else:
                        downloaded = 0
                        while (downloaded == 0 or N<50):
                            directory=pathFTP
                            ftp.cwd(directory)
                            lf = open(file_name, "wb")
                            ftp.retrbinary("RETR " + nameTotal, lf.write)
                            lf.close()												
                            statinfo = os.stat(file_name)	
                            N = N + 1																												
                            # Say that download was succesfull		
                            if int(statinfo.st_size) > 1000:																								
                                downloaded = 1
                            else:																													
                                print '%d attemps are needed to download %s' %(N, file_name)     			                  
 																									
                            print "downloading ", FTP_name    
  
                except:	
	               # Try another time                     																				
                    N = N + 1
																				
			   # Stop trying after 10 times																				
                if N == 50:
                    downloaded = 1
                    print 'Was not able to download %s' % file_name		
																	
                # Open .hdf only band with ET and collect all tiles to one array
                dataset=gdal.Open(file_name)
                sdsdict=dataset.GetMetadata('SUBDATASETS')
                sdslist =[sdsdict[k] for k in sdsdict.keys() if '_1_NAME' in k]
                sds=[]
               
                for n in sdslist:
                    sds.append(gdal.Open(n))
                    full_layer = [i for i in sdslist if 'ET_1km' in i]
                    idx = sdslist.index(full_layer[0]) 
                    data = sds[idx].ReadAsArray() 
                    countYdata=(TilesVertical[1]-TilesVertical[0]+2)-countY
                    DataTot[(countYdata-1)*1200:countYdata*1200,(countX-1)*1200:countX*1200]=data*0.1
                    DataTot[DataTot>3000]=0
                    sds=None
                del data
                    
            except:
                data=np.ones((1200,1200))*(-99990)
                countYdata=(TilesVertical[1]-TilesVertical[0]+2)-countY
                DataTot[(countYdata-1)*1200:countYdata*1200,(countX-1)*1200:countX*1200]=data*0.1
                DataTot[DataTot>3000]=-9999
    return(DataTot,LatMet,LongMet)
    
def Save_as_Gtiff(A,ETfileName,lonlim,latlim):
    '''
	This function saves an array as a tiff file

    Keywords arguments:
    A -- Numpy array (includes values for the tiff file)
    NDVIfileName -- 'C:/file/to/path/' (the output tiff file)	
    lonlim -- [ymin, ymax] (longitude limits of the whole image)
    latlim -- [ymin, ymax] (latitude limits of the whole image) 	
    ''' 
      
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(ETfileName, A.shape[1], A.shape[0], 1, gdal.GDT_Float32, ['COMPRESS=LZW'])                    
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")
    dst_ds.SetProjection(srs.ExportToWkt())
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform([lonlim[0],0.005,0,latlim[1],0,-0.005])
    dst_ds.GetRasterBand(1).WriteArray(np.flipud(A))
    dst_ds = None