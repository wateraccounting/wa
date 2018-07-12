# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/DEM
"""

# General modules
import numpy as np
import os
import urllib
import shutil
import gdal
import glob

# WA+ modules
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC

def DownloadData(output_folder, latlim, lonlim, parameter, resolution):
    """
    This function downloads DEM data from HydroSHED

    Keyword arguments:
    output_folder -- directory of the result
	latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    Resample -- 1 = The data will be resampled to 0.001 degree spatial
                    resolution
             -- 0 = The data will have the same pixel size as the data obtained
                    from the internet
    """
    # Define parameter depedent variables
    if parameter == "dir_3s":
        para_name = "DIR"
        unit = "-"
        resolution = '3s'
        parameter = 'dir'

    if parameter == "dem_3s":
        para_name = "DEM"
        unit = "m"
        resolution = '3s'
        parameter = 'dem'

    if parameter == "dir_15s":
        para_name = "DIR"
        unit = "-"
        resolution = '15s'
        parameter = 'dir'

    if parameter == "dem_15s":
        para_name = "DEM"
        unit = "m"
        resolution = '15s'
        parameter = 'dem'

   # converts the latlim and lonlim into names of the tiles which must be
    # downloaded
    if resolution == '3s':

        name, rangeLon, rangeLat = Find_Document_Names(latlim, lonlim, parameter)


        # Memory for the map x and y shape (starts with zero)
        size_X_tot = 0
        size_Y_tot = 0

    if resolution == '15s':
       name = Find_Document_names_15s(latlim, lonlim, parameter, resolution)

    nameResults = []
    # Create a temporary folder for processing
    output_folder_trash = os.path.join(output_folder, "Temp")
    if not os.path.exists(output_folder_trash):
        os.makedirs(output_folder_trash)

    # Download, extract, and converts all the files to tiff files
    for nameFile in name:

        try:
            # Download the data from
            # http://earlywarning.usgs.gov/hydrodata/
            output_file, file_name = Download_Data(nameFile,
                                                   output_folder_trash, parameter, para_name,resolution)

            # extract zip data
            DC.Extract_Data(output_file, output_folder_trash)

            # Converts the data with a adf extention to a tiff extension.
            # The input is the file name and in which directory the data must be stored
            file_name_tiff = file_name.split('.')[0] + '_trans_temporary.tif'
            file_name_extract = file_name.split('_')[0:3]
            if resolution == '3s':
                file_name_extract2 = file_name_extract[0]+'_'+file_name_extract[1]

            if resolution == '15s':
                file_name_extract2 = file_name_extract[0]+'_'+file_name_extract[1]+'_15s'

            input_adf = os.path.join(output_folder_trash, file_name_extract2,
                                    file_name_extract2, 'hdr.adf')
            output_tiff = os.path.join(output_folder_trash, file_name_tiff)

            # convert data from adf to a tiff file
            output_tiff = DC.Convert_adf_to_tiff(input_adf, output_tiff)

            geo_out, proj, size_X, size_Y = RC.Open_array_info(output_tiff)
            if int(size_X) != int(6000) or int(size_Y) != int(6000):
                data = np.ones((6000, 6000)) * -9999

                # Create the latitude bound
                Vfile = str(nameFile)[1:3]
                SignV = str(nameFile)[0]
                SignVer = 1
                # If the sign before the filename is a south sign than latitude is negative
                if SignV is "s":
                    SignVer = -1
                Bound2 = int(SignVer)*int(Vfile)

              # Create the longitude bound
                Hfile = str(nameFile)[4:7]
                SignH = str(nameFile)[3]
                SignHor = 1
                # If the sign before the filename is a west sign than longitude is negative
                if SignH is "w":
                    SignHor = -1
                Bound1 = int(SignHor) * int(Hfile)

                Expected_X_min = Bound1
                Expected_Y_max = Bound2 + 5

                Xid_start = int(np.round((geo_out[0] - Expected_X_min)/geo_out[1]))
                Xid_end = int(np.round(((geo_out[0] + size_X * geo_out[1]) - Expected_X_min)/geo_out[1]))
                Yid_start = int(np.round((Expected_Y_max - geo_out[3])/(-geo_out[5])))
                Yid_end = int(np.round((Expected_Y_max - (geo_out[3] + (size_Y * geo_out[5])))/(-geo_out[5])))

                data[Yid_start:Yid_end,Xid_start:Xid_end] = RC.Open_tiff_array(output_tiff)
                if np.max(data)==255:
                    data[data==255] = -9999
                data[data<-9999] = -9999

                geo_in = [Bound1, 0.00083333333333333, 0.0, int(Bound2 + 5),
                          0.0, -0.0008333333333333333333]

                # save chunk as tiff file
                DC.Save_as_tiff(name=output_tiff, data=data, geo=geo_in,
                             projection="WGS84")

        except:

            if resolution == '3s':
                # If tile not exist create a replacing zero tile (sea tiles)
                output = nameFile.split('.')[0] + "_trans_temporary.tif"
                output_tiff = os.path.join(output_folder_trash, output)
                file_name = nameFile
                data = np.ones((6000, 6000)) * -9999
                data = data.astype(np.float32)

                # Create the latitude bound
                Vfile = str(file_name)[1:3]
                SignV = str(file_name)[0]
                SignVer = 1
                # If the sign before the filename is a south sign than latitude is negative
                if SignV is "s":
                    SignVer = -1
                Bound2 = int(SignVer)*int(Vfile)

                # Create the longitude bound
                Hfile = str(file_name)[4:7]
                SignH = str(file_name)[3]
                SignHor = 1
                # If the sign before the filename is a west sign than longitude is negative
                if SignH is "w":
                    SignHor = -1
                Bound1 = int(SignHor) * int(Hfile)

                # Geospatial data for the tile
                geo_in = [Bound1, 0.00083333333333333, 0.0, int(Bound2 + 5),
                          0.0, -0.0008333333333333333333]

                # save chunk as tiff file
                DC.Save_as_tiff(name=output_tiff, data=data, geo=geo_in,
                             projection="WGS84")

            if resolution == '15s':

                print 'no 15s data is in dataset'

        if resolution =='3s':

            # clip data
            Data, Geo_data = RC.clip_data(output_tiff, latlim, lonlim)
            size_Y_out = int(np.shape(Data)[0])
            size_X_out = int(np.shape(Data)[1])

            # Total size of the product so far
            size_Y_tot = int(size_Y_tot + size_Y_out)
            size_X_tot = int(size_X_tot + size_X_out)

            if nameFile is name[0]:
                Geo_x_end = Geo_data[0]
                Geo_y_end = Geo_data[3]
            else:
                Geo_x_end = np.min([Geo_x_end,Geo_data[0]])
                Geo_y_end = np.max([Geo_y_end,Geo_data[3]])

            # create name for chunk
            FileNameEnd = "%s_temporary.tif" % (nameFile)
            nameForEnd = os.path.join(output_folder_trash, FileNameEnd)
            nameResults.append(str(nameForEnd))

            # save chunk as tiff file
            DC.Save_as_tiff(name=nameForEnd, data=Data, geo=Geo_data,
                          projection="WGS84")

    if resolution =='3s':
        #size_X_end = int(size_X_tot) #!
        #size_Y_end = int(size_Y_tot) #!

        size_X_end = int(size_X_tot/len(rangeLat)) + 1 #!
        size_Y_end = int(size_Y_tot/len(rangeLon)) + 1 #!

        # Define the georeference of the end matrix
        geo_out = [Geo_x_end, Geo_data[1], 0, Geo_y_end, 0, Geo_data[5]]

        latlim_out = [geo_out[3] + geo_out[5] * size_Y_end, geo_out[3]]
        lonlim_out = [geo_out[0], geo_out[0] + geo_out[1] * size_X_end]


        # merge chunk together resulting in 1 tiff map
        datasetTot = Merge_DEM(latlim_out, lonlim_out, nameResults, size_Y_end,
                                    size_X_end)

        datasetTot[datasetTot<-9999] = -9999


    if resolution =='15s':
        output_file_merged = os.path.join(output_folder_trash,'merged.tif')
        datasetTot, geo_out = Merge_DEM_15s(output_folder_trash, output_file_merged,latlim, lonlim)

    # name of the end result
    output_DEM_name = "%s_HydroShed_%s_%s.tif" %(para_name,unit,resolution)

    Save_name = os.path.join(output_folder, output_DEM_name)

    # Make geotiff file
    DC.Save_as_tiff(name=Save_name, data=datasetTot, geo=geo_out, projection="WGS84")
    os.chdir(output_folder)

    # Delete the temporary folder
    shutil.rmtree(output_folder_trash)

def Merge_DEM_15s(output_folder_trash,output_file_merged,latlim, lonlim):

    os.chdir(output_folder_trash)
    tiff_files = glob.glob('*.tif')
    resolution_geo = []
    lonmin =  lonlim[0]
    lonmax =  lonlim[1]
    latmin =  latlim[0]
    latmax =  latlim[1]
    resolution_geo = 0.00416667

    size_x_tot = int(np.round((lonmax-lonmin) / resolution_geo))
    size_y_tot = int(np.round((latmax-latmin) / resolution_geo))

    data_tot = np.ones([size_y_tot,size_x_tot]) * -9999.

    for tiff_file in tiff_files:
        inFile=os.path.join(output_folder_trash,tiff_file)
        geo, proj, size_X, size_Y = RC.Open_array_info(inFile)
        resolution_geo = geo[1]

        lonmin_one = geo[0]
        lonmax_one = geo[0] + size_X *	geo[1]
        latmin_one = geo[3] + size_Y *	geo[5]
        latmax_one = geo[3]

        if lonmin_one < lonmin:
           lonmin_clip = lonmin
        else:
           lonmin_clip = lonmin_one

        if lonmax_one > lonmax:
            lonmax_clip = lonmax
        else:
            lonmax_clip = lonmax_one

        if latmin_one < latmin:
            latmin_clip = latmin
        else:
           latmin_clip = latmin_one

        if latmax_one > latmax:
            latmax_clip = latmax
        else:
           latmax_clip = latmax_one

        size_x_clip = int(np.round((lonmax_clip-lonmin_clip) / resolution_geo))
        size_y_clip = int(np.round((latmax_clip-latmin_clip) / resolution_geo))

        inFile=os.path.join(output_folder_trash,tiff_file)
        geo, proj, size_X, size_Y = RC.Open_array_info(inFile)
        Data = RC.Open_tiff_array(inFile)
        lonmin_tiff = geo[0]
        latmax_tiff = geo[3]
        lon_tiff_position = int(np.round((lonmin_clip - lonmin_tiff)/ resolution_geo))
        lat_tiff_position = int(np.round((latmax_tiff - latmax_clip)/ resolution_geo))
        lon_data_tot_position = int(np.round((lonmin_clip - lonmin)/ resolution_geo))
        lat_data_tot_position = int(np.round((latmax - latmax_clip)/ resolution_geo))

        Data[Data<-9999.] = -9999.
        data_tot[lat_data_tot_position:lat_data_tot_position+size_y_clip,lon_data_tot_position:lon_data_tot_position+size_x_clip][data_tot[lat_data_tot_position:lat_data_tot_position+size_y_clip,lon_data_tot_position:lon_data_tot_position+size_x_clip]==-9999]= Data[lat_tiff_position:lat_tiff_position+size_y_clip,lon_tiff_position:lon_tiff_position+size_x_clip][data_tot[lat_data_tot_position:lat_data_tot_position+size_y_clip,lon_data_tot_position:lon_data_tot_position+size_x_clip]==-9999]

    geo_out = [lonmin, resolution_geo, 0.0, latmax, 0.0, -1 * resolution_geo]
    geo_out = tuple(geo_out)
    data_tot[data_tot<-9999.] = -9999.

    return(data_tot, geo_out)

def Merge_DEM(latlim, lonlim, nameResults, size_Y_tot, size_X_tot):
    """
    This function will merge the tiles

    Keyword arguments:
    latlim -- [ymin, ymax], (values must be between -50 and 50)
    lonlim -- [xmin, xmax], (values must be between -180 and 180)
    nameResults -- ['string'], The directories of the tiles which must be
                   merged
    size_Y_tot -- integer, the width of the merged array
    size_X_tot -- integer, the length of the merged array
    """
    # Define total size of end dataset and create zero array
    datasetTot = np.ones([size_Y_tot, size_X_tot])*-9999.

    # Put all the files in the datasetTot (1 by 1)
    for nameTot in nameResults:
        f = gdal.Open(nameTot)
        dataset = np.array(f.GetRasterBand(1).ReadAsArray())
        dataset = np.flipud(dataset)
        geo_out = f.GetGeoTransform()
        BoundChunk1 = int(round((geo_out[0]-lonlim[0])/geo_out[1]))
        BoundChunk2 = BoundChunk1 + int(dataset.shape[1])
        BoundChunk4 = size_Y_tot + int(round((geo_out[3] -
                                       latlim[1]) / geo_out[1]))
        BoundChunk3 = BoundChunk4 - int(dataset.shape[0])
        datasetTot[BoundChunk3:BoundChunk4, BoundChunk1:BoundChunk2] = dataset
        f = None
    datasetTot = np.flipud(datasetTot)
    return(datasetTot)

def Find_Document_Names(latlim, lonlim, parameter):
    """
    This function will translate the latitude and longitude limits into
    the filenames that must be downloaded from the hydroshed webpage

    Keyword Arguments:
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    # find tiles that must be downloaded
    startLon = np.floor(lonlim[0] / 5) * 5
    startLat = np.floor(latlim[0] / 5) * 5
    endLon = np.ceil(lonlim[1] / 5.0) * 5
    endLat = np.ceil(latlim[1] / 5.0) * 5
    rangeLon = np.arange(startLon, endLon, 5)
    rangeLat = np.arange(startLat, endLat, 5)

    name = []

    # make the names of the files that must be downloaded
    for lonname in rangeLon:
        if lonname < 0:
            DirectionLon = "w"
        else:
            DirectionLon = "e"

        for latname in rangeLat:
            if latname < 0:
                DirectionLat = "s"
            else:
                DirectionLat = "n"

            name.append(str(DirectionLat + str('%02d' % int(abs(latname))) +
                        DirectionLon + str('%03d' % int(abs(lonname))) +
                        "_%s_grid.zip" %parameter))
    return(name, rangeLon, rangeLat)


def Download_Data(nameFile, output_folder_trash, parameter,para_name,resolution):
    """
    This function downloads the DEM data from the HydroShed website

    Keyword Arguments:
    nameFile -- name, name of the file that must be downloaded
    output_folder_trash -- Dir, directory where the downloaded data must be
                           stored
    """

    # download data from the internet
    allcontinents = ["af", "as", "au", "ca", "eu", "na", "sa"]
    for continent in allcontinents:
        try:
            continent2 = continent.upper()
            para_name2 = para_name.lower()
            # info about the roots http://www.hydrosheds.org/download/getroot
            if resolution == '3s':
                url="https://earlywarning.usgs.gov/hydrodata/sa_%s_%s_grid/%s/%s" %(para_name2,resolution,continent2,nameFile)
            if resolution == '15s':
                url="https://earlywarning.usgs.gov/hydrodata/sa_%s_zip_grid/%s" %(resolution,nameFile)
            file_name = url.split('/')[-1]
            output_file = os.path.join(output_folder_trash, file_name)
            urllib.urlretrieve(url, output_file)
            size_data	= int(os.stat(output_file).st_size)

            if  size_data > 10000:
                break
        except:
            continue

    if int(os.stat(output_file).st_size) == 0:
        for continent in allcontinents:
            try:
                continent2 = continent.upper()
                para_name2 = para_name.lower()
                # info about the roots http://www.hydrosheds.org/download/getroot
                if resolution == '3s':
                    url="https://earlywarning.usgs.gov/hydrodata/sa_%s_%s_grid/%s/%s" %(para_name2,resolution,continent2,nameFile)
                if resolution == '15s':
                    url="https://earlywarning.usgs.gov/hydrodata/sa_%s_zip_grid/%s" %(resolution,nameFile)
                file_name = url.split('/')[-1]
                output_file = os.path.join(output_folder_trash, file_name)
                urllib.urlretrieve(url, output_file)

                if int(os.stat(output_file).st_size) > 10000:
                    break
            except:
                continue

    return(output_file, file_name)


def Find_Document_names_15s(latlim, lonlim, parameter, resolution):

    continents = ['na','ca','sa','eu','af','as','au']
    continents_download = []

    for continent in continents:
        extent = DEM_15s_extents.Continent[continent]
        if (extent[0] < lonlim[0] and extent[1] > lonlim[0] and extent[2] < latlim[0] and extent[3] > latlim[0]) or (extent[0] < lonlim[1] and extent[1] > lonlim[1] and extent[2] < latlim[1] and extent[3] > latlim[1]) == True:
            name = '%s_%s_%s_grid.zip' %(continent, parameter, resolution)
            continents_download = np.append(continents_download,name)

    return(continents_download)

class DEM_15s_extents:
        Continent = { 'na' : [-138, -52, 24, 60],
					'ca' : [-119, -60, 5, 39],
                      'sa' : [-93, -32, -56, 15],
                      'eu' : [-14, 70, 12, 62],
                      'af' : [-19, 55, -35, 38],
                      'as' : [57, 180, -12, 61],
                      'au' : [112, 180, -56, -10]}


