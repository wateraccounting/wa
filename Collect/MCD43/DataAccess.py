# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MCD43
"""

# import general python modules
import os
import numpy as np
import pandas as pd
import gdal
import urllib
import urllib2
from bs4 import BeautifulSoup
import re
import urlparse
import glob
import requests
from joblib import Parallel, delayed

# Water Accounting modules
import wa
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC
from wa import WebAccounts

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar, cores, hdf_library, remove_hdf):
    """
    This function downloads MCD43 daily data

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

    # Check start and end date and otherwise set the date to max
    if not Startdate:
        Startdate = pd.Timestamp('2000-02-24')
    if not Enddate:
        Enddate = pd.Timestamp('Now')

    # Make an array of the days of which the NDVI is taken
    Dates = pd.date_range(Startdate, Enddate, freq = 'D')

    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    if latlim[0] < -90 or latlim[1] > 90:
        print 'Latitude above 90N or below 90S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0], -90)
        latlim[1] = np.min(latlim[1], 90)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0], -180)
        lonlim[1] = np.min(lonlim[1], 180)

    # Make directory for the MODIS Albedo data
    Dir = Dir.replace("/", os.sep)
    output_folder = os.path.join(Dir, 'Albedo', 'MCD43')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define which MODIS tiles are required
    TilesVertical, TilesHorizontal = wa.Collect.MOD15.DataAccess.Get_tiles_from_txt(output_folder, hdf_library, latlim, lonlim)

    # Pass variables to parallel function and run
    args = [output_folder, TilesVertical, TilesHorizontal, lonlim, latlim, hdf_library]
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
    if remove_hdf == 1:
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
    This function retrieves MCD43 Albedo data for a given date from the
    http://e4ftl01.cr.usgs.gov/ server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, TilesVertical, TilesHorizontal, lonlim, latlim, hdf_library] = args

    # Collect the data from the MODIS webpage and returns the data and lat and long in meters of those tiles
    try:
        Collect_data(TilesHorizontal, TilesVertical, Date, output_folder, hdf_library)
    except:
        print "Was not able to download the file"

      # Define the output name of the collect data function
    name_collect = os.path.join(output_folder, 'Merged.tif')

    # Reproject the MODIS product to epsg_to
    epsg_to ='4326'
    name_reprojected = RC.reproject_MODIS(name_collect, epsg_to)

    # Clip the data to the users extend
    data, geo = RC.clip_data(name_reprojected, latlim, lonlim)

    # Save results as Gtiff
    ReffileName = os.path.join(output_folder, 'Albedo_MCD43A3_-_daily_' + Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + Date.strftime('%d') + '.tif')
    DC.Save_as_tiff(name=ReffileName, data=data, geo=geo, projection='WGS84')

    # remove the side products
    os.remove(os.path.join(output_folder, name_collect))
    os.remove(os.path.join(output_folder, name_reprojected))

    return True

def Collect_data(TilesHorizontal,TilesVertical,Date,output_folder, hdf_library):
    '''
    This function downloads all the needed MODIS tiles from https://e4ftl01.cr.usgs.gov/MOTA/MCD43A3.006/ as a hdf file.

    Keywords arguments:
    TilesHorizontal -- [TileMin,TileMax] max and min horizontal tile number
    TilesVertical -- [TileMin,TileMax] max and min vertical tile number
    Date -- 'yyyy-mm-dd'
    output_folder -- 'C:/file/to/path/'
    '''

    # Make a new tile for the data
    sizeX = int((TilesHorizontal[1] - TilesHorizontal[0] + 1) * 2400)
    sizeY = int((TilesVertical[1] - TilesVertical[0] + 1) * 2400)
    DataTot_Direct = np.zeros((sizeY, sizeX))
    DataTot_Diffuse= np.zeros((sizeY, sizeX))

    # Load accounts
    username, password = WebAccounts.Accounts(Type = 'NASA')

    # Create the Lat and Long of the MODIS tile in meters
    for Vertical in range(int(TilesVertical[0]), int(TilesVertical[1])+1):
        Distance = 231.65635826395834 * 2 # resolution of a MODIS pixel in meter
        countY=(TilesVertical[1] - TilesVertical[0] + 1) - (Vertical - TilesVertical[0])

        for Horizontal in range(int(TilesHorizontal[0]), int(TilesHorizontal[1]) + 1):
            countX=Horizontal - TilesHorizontal[0] + 1

            # Download the MODIS NDVI data
            url = 'https://e4ftl01.cr.usgs.gov/MOTA/MCD43A3.006/' + Date.strftime('%Y') + '.' + Date.strftime('%m') + '.' + Date.strftime('%d') + '/'

		      # Reset the begin parameters for downloading
            downloaded = 0
            N=0

	         # Check the library given by user
            if hdf_library is not None:
                os.chdir(hdf_library)
                hdf_name = glob.glob("MCD43A3.A%s%03s.h%02dv%02d.*" %(Date.strftime('%Y'), Date.strftime('%j'), Horizontal, Vertical))

                if len(hdf_name) == 1:
                    hdf_file = os.path.join(hdf_library, hdf_name[0])

                    if os.path.exists(hdf_file):
                        downloaded = 1
                        file_name = hdf_file

            if not downloaded == 1:

                # Get files on FTP server
                f = urllib2.urlopen(url)

                # Sum all the files on the server
                soup = BeautifulSoup(f, "lxml")
                for i in soup.findAll('a', attrs = {'href': re.compile('(?i)(hdf)$')}):

                    # Find the file with the wanted tile number
                    Vfile=str(i)[30:32]
                    Hfile=str(i)[27:29]
                    if int(Vfile) is int(Vertical) and int(Hfile) is int(Horizontal):

                        # Define the whole url name
                        full_url = urlparse.urljoin(url, i['href'])

                        # if not downloaded try to download file
                        while downloaded == 0:

                            try:# open http and download whole .hdf
                                nameDownload = full_url
                                file_name = os.path.join(output_folder,nameDownload.split('/')[-1])
                                if os.path.isfile(file_name):
                                    downloaded = 1
                                else:
                                    x = requests.get(nameDownload, allow_redirects = False)
                                    try:
                                        y = requests.get(x.headers['location'], auth = (username, password))
                                    except:
                                        from requests.packages.urllib3.exceptions import InsecureRequestWarning
                                        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                                        y = requests.get(x.headers['location'], auth = (username, password), verify = False)
                                    z = open(file_name, 'wb')
                                    z.write(y.content)
                                    z.close()
                                    statinfo = os.stat(file_name)
                                    # Say that download was succesfull
                                    if int(statinfo.st_size) > 10000:
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
                # Open .hdf only band with NDVI and collect all tiles to one array
                dataset = gdal.Open(file_name)
                sdsdict = dataset.GetMetadata('SUBDATASETS')
                sdslist = [sdsdict[k] for k in sdsdict.keys() if '_20_NAME' in k]
                sds = []

                for n in sdslist:
                    sds.append(gdal.Open(n))
                    full_layer = [i for i in sdslist if 'Albedo_BSA_shortwave' in i]
                    idx = sdslist.index(full_layer[0])
                    if Horizontal == TilesHorizontal[0] and Vertical == TilesVertical[0]:
                        geo_t = sds[idx].GetGeoTransform()

                        # get the projection value
                        proj = sds[idx].GetProjection()

                    data = sds[idx].ReadAsArray()
                    countYdata = (TilesVertical[1] - TilesVertical[0] + 2) - countY
                    DataTot_Direct[int((countYdata - 1) * 2400):int(countYdata * 2400), int((countX - 1) * 2400):int(countX * 2400)]=data

                # Open .hdf only band with NDVI and collect all tiles to one array
                dataset = gdal.Open(file_name)
                sdsdict = dataset.GetMetadata('SUBDATASETS')
                sdslist = [sdsdict[k] for k in sdsdict.keys() if '_30_NAME' in k]
                sds = []

                for n in sdslist:
                    sds.append(gdal.Open(n))
                    full_layer = [i for i in sdslist if 'Albedo_WSA_shortwave' in i]
                    idx = sdslist.index(full_layer[0])
                    if Horizontal == TilesHorizontal[0] and Vertical == TilesVertical[0]:
                        geo_t = sds[idx].GetGeoTransform()

                        # get the projection value
                        proj = sds[idx].GetProjection()

                    data = sds[idx].ReadAsArray()
                    countYdata = (TilesVertical[1] - TilesVertical[0] + 2) - countY
                    DataTot_Diffuse[int((countYdata - 1) * 2400):int(countYdata * 2400), int((countX - 1) * 2400):int(countX * 2400)]=data
                del data


            # if the tile not exists or cannot be opened, create a nan array with the right projection
            except:
                if Horizontal==TilesHorizontal[0] and Vertical==TilesVertical[0]:
                     x1 = (TilesHorizontal[0] - 19) * 2400 * Distance
                     x4 = (TilesVertical[0] - 9) * 2400 * -1 * Distance
                     geo = 	[x1, Distance, 0.0, x4, 0.0, -Distance]
                     geo_t=tuple(geo)

                proj='PROJCS["unnamed",GEOGCS["Unknown datum based upon the custom spheroid",DATUM["Not specified (based on custom spheroid)",SPHEROID["Custom spheroid",6371007.181,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Sinusoidal"],PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'
                data=np.ones((2400,2400)) * (-9999)
                countYdata=(TilesVertical[1] - TilesVertical[0] + 2) - countY
                DataTot_Direct[(countYdata - 1) * 2400:countYdata * 2400,(countX - 1) * 2400:countX * 2400] = data
                DataTot_Diffuse[(countYdata - 1) * 2400:countYdata * 2400,(countX - 1) * 2400:countX * 2400] = data
                del data

    DataTot = (0.3 * DataTot_Diffuse + 0.7 * DataTot_Direct) * 0.001
    DataTot[DataTot>5.] = -9999

    # Make geotiff file
    name2 = os.path.join(output_folder, 'Merged.tif')
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(name2, DataTot.shape[1], DataTot.shape[0], 1, gdal.GDT_Float32, ['COMPRESS=LZW'])
    try:
         dst_ds.SetProjection(proj)
    except:
        proj='PROJCS["unnamed",GEOGCS["Unknown datum based upon the custom spheroid",DATUM["Not specified (based on custom spheroid)",SPHEROID["Custom spheroid",6371007.181,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Sinusoidal"],PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'
        x1 = (TilesHorizontal[0] - 18) * 2400 * Distance
        x4 = (TilesVertical[0] - 9) * 2400 * -1 * Distance
        geo = [x1, Distance, 0.0, x4, 0.0, -Distance]
        geo_t = tuple(geo)
        dst_ds.SetProjection(proj)

    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform(geo_t)
    dst_ds.GetRasterBand(1).WriteArray(DataTot)
    dst_ds = None
    sds = None
    return()
