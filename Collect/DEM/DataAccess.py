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
import tempfile
import gdal

# WA+ modules
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC

def DownloadData(output_folder, latlim, lonlim):
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
    # converts the latlim and lonlim into names of the tiles which must be
    # downloaded
    name, rangeLon, rangeLat = Find_Document_Names(latlim, lonlim)
    nameResults = []
				
	# Memory for the map x and y shape (starts with zero)			
    size_X_tot = 0
    size_Y_tot = 0
				
    # Create a temporary folder for processing				
    output_folder_trash = tempfile.mkdtemp()

    # Download, extract, and converts all the files to tiff files
    for nameFile in name:

        try:
            # Download the data from
            # http://earlywarning.usgs.gov/hydrodata/
            output_file, file_name = Download_Data(nameFile,
                                                   output_folder_trash)

            # extract zip data
            DC.Extract_Data(output_file, output_folder_trash)

            # Converts the data with a adf extention to a tiff extension.
            # The input is the file name and in which directory the data must be stored
            file_name_tiff = file_name.split('.')[0] + '_trans_temporary.tif'
            file_name_extract = file_name.split('_')[0:3]
            file_name_extract2 = file_name_extract[0]+'_'+file_name_extract[1]
            input_adf = os.path.join(output_folder_trash, file_name_extract2,
                                    file_name_extract2, 'hdr.adf')
            output_tiff = os.path.join(output_folder_trash, file_name_tiff)

            # convert data from adf to a tiff file
            output_tiff = DC.Convert_adf_to_tiff(input_adf, output_tiff)

        except:
            # If tile not excist create a replacing zero tile (sea tiles)
            output = nameFile.split('.')[0] + "_trans_temporary.tif"
            output_tiff = os.path.join(output_folder_trash, output)
            file_name = nameFile
            data = np.zeros((6000, 6000))
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
            geo_in = [Bound2, 0.00083333333333333, 0.0, int(Bound1 + 5),
                      0.0, 0.0008333333333333333333]

            # save chunk as tiff file
            DC.Save_as_tiff(name=output_tiff, data=data, geo=geo_in,
                         projection="WGS84")

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

    size_X_end = int(size_X_tot/len(rangeLat)) 
    size_Y_end = int(size_Y_tot/len(rangeLon)) 
		
    # Define the georeference of the end matrix			
    geo_out = [Geo_x_end, Geo_data[1], 0, Geo_y_end, 0, Geo_data[5]]

    latlim_out = [geo_out[3] + geo_out[5] * size_Y_end, geo_out[3]]
    lonlim_out = [geo_out[0], geo_out[0] + geo_out[1] * size_X_end]
				
    # merge chunk together resulting in 1 tiff map
    datasetTot = Merge_DEM(latlim_out, lonlim_out, nameResults, size_Y_end,
                           size_X_end)

    # name of the end result
    output_DEM_name = "DEM_HydroShed_m.tif"
    Save_name = os.path.join(output_folder, output_DEM_name)   
				
	
    # Make geotiff file
    DC.Save_as_tiff(name=Save_name, data=datasetTot, geo=geo_out, projection="WGS84")
    
	# Delete the temporary folder
    shutil.rmtree(output_folder_trash)


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
    datasetTot = np.zeros([size_Y_tot, size_X_tot])
				
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

def Find_Document_Names(latlim, lonlim):
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
                        "_con_grid.zip"))
    return(name, rangeLon, rangeLat)


def Download_Data(nameFile, output_folder_trash):
    """
    This function downloads the DEM data from the HydroShed website

    Keyword Arguments:
    nameFile -- name, name of the file that must be downloaded
    output_folder_trash -- Dir, directory where the downloaded data must be
                           stored
    """
    # download data from the internet
    allcontinents = ["AF", "AS", "au", "CA", "EU", "NA", "SA"]
    DoContinent = "AF"
    TotalSize = 0
    for continent in allcontinents:
        
        # Reset the begin parameters for downloading												
        downloaded = 0   
        N=0  	
																	
        # if not downloaded try to download file																	
        while downloaded == 0:								
            try:
                url = ("http://earlywarning.usgs.gov/hydrodata/sa_con_3s_grid/"
                       "%s/%s") % (continent, nameFile)

                site = urllib.urlopen(url)
                meta = site.info()
                if meta.getheaders("Content-Length")[0] > TotalSize:
                    DoContinent = continent
                    TotalSize = meta.getheaders("Content-Length")[0]

																
                url = ("http://earlywarning.usgs.gov/hydrodata/sa_con_3s_grid/"
                         "%s/%s") % (DoContinent, nameFile)

                file_name = url.split('/')[-1]
                output_file = os.path.join(output_folder_trash, file_name)
                urllib.urlretrieve(url, output_file)													
                downloaded = 1												
																
            # If download was not succesfull								
            except:	
																			
                # Try another time                     																				
                N = N + 1
																				
                # Stop trying after 10 times																				
                if N == 10:
                    print 'Data from HydroSHED %s is not available' %continent
                    downloaded = 1
	    			
    return(output_file, file_name)

