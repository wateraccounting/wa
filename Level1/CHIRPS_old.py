# -*- coding: utf-8 -*-
"""
author: Tim Hessels
contact: t.hessels@unesco-ihe.org
UNESCO-IHE 2015
"""
import os
import numpy as np
import pandas as pd
from ftplib import FTP
import gzip
from osgeo import osr, gdal

#this file downloads CHIRPS 2.0 data from ftp://chg-ftpout.geog.ucsb.edu
#import this module by using: import CHIRPS
#use the CHIRPS_daily or CHIRPS_monthly definitions to download and create daily or monthly CHIRPS images in Gtiff format
#the CHIRPS data is available since 1981-01-01 till present
#the following input is needed:
#Startdate: 'yyyy-mm-dd'
#Enddate: 'yyyy-mm-dd'
#latlim:[ymin, ymax] (values must be between -50 and 50)
#lonlim:[xmin, xmax] (values must be between -180 and 180)
#Dir: 'C:/file/to/path/'
#an example how to recieve the data:
#make a new python script and import the CHIRPS module and give variables as shown in the example below: 
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#import CHIRPS
#CHIRPS.CHIRPS_daily(Startdate='1999-02-01',Enddate='1999-05-22',latlim = [-10,30],lonlim = [-20,120], Dir = 'C:/Users/tih/Documents/Water Accounting/Precipitation/Output_map/')
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# You will recieve .tiff images of daily CHIRPS 2.0 data between the latitude of 10S and 30N and a longitude of 20W and 120E for all days between 1 February 1999 and 22 May 1999 and stored in the chosen directory

def CHIRPS_daily(Startdate = '',Enddate = '',latlim = '',lonlim = '', Dir = ''):
    # check variables
    if not Startdate:
        Startdate = pd.Timestamp('1981-01-01')
    if not Enddate: 
        Enddate = pd.Timestamp('Now')
    Dates = pd.date_range(Startdate,Enddate,freq = 'D')
    
    if latlim[0] < -50 or latlim[1] > 50:
        print 'Latitude above 50N or below 50S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0],-50)
        latlim[1] = np.min(lonlim[1],50)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(latlim[0],-180)
        lonlim[1] = np.min(lonlim[1],180)
    
    # make directory
    output_folder=os.path.join(Dir,'Precipitation','CHIRPS/')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # Define IDs
    yID = 2000 - np.int16(np.array([np.ceil((latlim[1]+50)*20),np.floor((latlim[0]+50)*20)]))
    xID = np.int16(np.array([np.floor((lonlim[0]+180)*20),np.ceil((lonlim[1]+180)*20)]))       
        
    for Date in Dates:
        
       # open ftp server         
       ftp=FTP("chg-ftpout.geog.ucsb.edu", "", "")
       ftp.login()
       pathFTP='pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p05/'+ Date.strftime('%Y') + '/'
       ftp.retrlines("LIST")
       ftp.cwd(pathFTP)
       listing=[]
       ftp.retrlines("LIST", listing.append)
       filename='chirps-v2.0.'+Date.strftime('%Y')+'.'+Date.strftime('%m')+'.'+Date.strftime('%d')+'.tif.gz'          
       
       # download the file
       try:
           local_filename = os.path.join(output_folder, filename)
           lf = open(local_filename, "wb")
           ftp.retrbinary("RETR " + filename, lf.write, 8*1024)
           lf.close()
           
           # unzip the file
           filename = output_folder + filename
           outfilename=output_folder+ 'chirps-v2.0.'+Date.strftime('%Y')+'.'+Date.strftime('%m')+'.'+Date.strftime('%d')+'.tif'
           with gzip.GzipFile(filename,'rb') as zf:
               file_content=zf.read()
               save_file_content=file(outfilename,'wb')
               save_file_content.write(file_content)
           save_file_content.close()
           zf.close()
           os.remove(filename)
           
          # open tiff file
           filetif= output_folder+ 'chirps-v2.0.'+Date.strftime('%Y')+'.'+Date.strftime('%m')+'.'+Date.strftime('%d')+'.tif'
           ds=gdal.Open(filetif)
           dataset = np.array(ds.GetRasterBand(1).ReadAsArray())
           
           # clip dataset to the given extent
           data = dataset[yID[0]:yID[1],xID[0]:xID[1]]  
           data[data < 0] = -9999
           
           # save dataset as geotiff file
           DirFileEnd=output_folder + 'P_CHIRPS.v2.0_mm-day-1_daily_' + Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + Date.strftime('%d') + '.tif'
                       
           driver = gdal.GetDriverByName("GTiff")
           dst_ds = driver.Create(DirFileEnd, data.shape[1], int(yID[1]-yID[0]), 1, gdal.GDT_Float32, ['COMPRESS=LZW'])                    
           srs = osr.SpatialReference()
           srs.SetWellKnownGeogCS("WGS84")
           dst_ds.SetProjection(srs.ExportToWkt())
           dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
           dst_ds.SetGeoTransform([lonlim[0],0.05,0,latlim[1],0,-0.05])
           dst_ds.GetRasterBand(1).WriteArray(data)
           dst_ds = None 
           
           # delete old tif file
           ds=None
           os.remove(filetif)
           
       except:
           print "file not exists"
           continue

def CHIRPS_monthly(Startdate = '',Enddate = '',latlim = '',lonlim = '', Dir = ''):
    # check variables
    if not Startdate:
        Startdate = pd.Timestamp('1981-01-01')
    if not Enddate: 
        Enddate = pd.Timestamp('Now')
    Dates = pd.date_range(Startdate,Enddate,freq = 'MS')
    
    if latlim[0] < -50 or latlim[1] > 50:
        print 'Latitude above 50N or below 50S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0],-50)
        latlim[1] = np.min(lonlim[1],50)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(latlim[0],-180)
        lonlim[1] = np.min(lonlim[1],180)
        
        
    # make directory
    output_folder=os.path.join(Dir,'Precipitation','CHIRPS/')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
        
    # Define IDs
    yID = 2000 - np.int16(np.array([np.ceil((latlim[1]+50)*20),np.floor((latlim[0]+50)*20)]))
    xID = np.int16(np.array([np.floor((lonlim[0]+180)*20),np.ceil((lonlim[1]+180)*20)]))       
        
    for Date in Dates:
        
       # open ftp server         
       ftp=FTP("chg-ftpout.geog.ucsb.edu", "", "")
       ftp.login()
       pathFTP='pub/org/chg/products/CHIRPS-2.0/global_monthly/tifs/'
       ftp.retrlines("LIST")
       ftp.cwd(pathFTP)
       listing=[]
       ftp.retrlines("LIST", listing.append)
       filename='chirps-v2.0.'+Date.strftime('%Y')+'.'+Date.strftime('%m')+'.tif.gz'          
       
       # download the file
       try:
           local_filename = os.path.join(output_folder, filename)
           lf = open(local_filename, "wb")
           ftp.retrbinary("RETR " + filename, lf.write, 8*1024)
           lf.close()
           
           # unzip the file
           filename = output_folder + filename
           outfilename=output_folder+ 'chirps-v2.0.'+Date.strftime('%Y')+'.'+Date.strftime('%m')+'.tif'  
           with gzip.GzipFile(filename,'rb') as zf:
               file_content=zf.read()
               save_file_content=file(outfilename,'wb')
               save_file_content.write(file_content)
           save_file_content.close()
           zf.close()
           os.remove(filename)
           
          # open tiff file
           filetif= output_folder+ 'chirps-v2.0.'+Date.strftime('%Y')+'.'+Date.strftime('%m')+'.tif'  
           ds=gdal.Open(filetif)
           dataset = np.array(ds.GetRasterBand(1).ReadAsArray())
           
           # clip dataset to the given extent
           data = dataset[yID[0]:yID[1],xID[0]:xID[1]]  
           data[data < 0] = -9999
           
           # save dataset as geotiff file
           DirFileEnd=output_folder + 'P_CHIRPS.v2.0_mm-month-1_monthly_' + Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + Date.strftime('%d') + '.tif'
                       
           driver = gdal.GetDriverByName("GTiff")
           dst_ds = driver.Create(DirFileEnd, data.shape[1], int(yID[1]-yID[0]), 1, gdal.GDT_Float32, ['COMPRESS=LZW'])                    
           srs = osr.SpatialReference()
           srs.SetWellKnownGeogCS("WGS84")
           dst_ds.SetProjection(srs.ExportToWkt())
           dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
           dst_ds.SetGeoTransform([lonlim[0],0.05,0,latlim[1],0,-0.05])
           dst_ds.GetRasterBand(1).WriteArray(data)
           dst_ds = None 
           
           # delete old tif file
           ds=None
           os.remove(filetif)
           
       except:
           print "file not exists"
           continue
