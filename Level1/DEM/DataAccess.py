# -*- coding: utf-8 -*-
import numpy as np
import os
from osgeo import osr, gdal
import urllib
import zipfile
import shutil
import tempfile


def DownloadData(latlim, lonlim, Resample, output_folder):
    """
    This function downloads TRMM daily or monthly data

    Keyword arguments:
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    Resample -- 1 = The data will be resampled to 0.001 degree spatial
                    resolution
             -- 0 = The data will have the same pixel size as the data obtained
                    from the internet
    output_folder -- directory of the result
    """
    # converts the latlim and lonlim into names of the tiles which must be
    # downloaded
    name, rangeLon, rangeLat = Find_Document_Names(latlim, lonlim)
    nameResults = []
    size_X_tot = 0
    size_Y_tot = 0
    output_folder_trash = tempfile.mkdtemp()

    for nameFile in name:
        try:
            # Download the data from
            # http://earlywarning.usgs.gov/hydrodata/
            output_file, file_name = Download_Data(nameFile,
                                                   output_folder_trash)

            # extract zip data
            Extract_Data(output_file, output_folder_trash)

            # convert data from adf to a tiff file
            output_tiff = Convert_adf_to_tiff(file_name,
                                              output_folder_trash)

        except:
            # If tile not excist create a replacing NaN tile
            output = nameFile.split('.')[0] + "_trans_temporary.tif"
            output_tiff = os.path.join(output_folder_trash, output)
            file_name = nameFile
            data = np.zeros((6000, 6000))
            data = data.astype(np.float32)

            Vfile = str(file_name)[1:3]
            SignV = str(file_name)[0]
            SignVer = 1
            if SignV is "s":
                SignVer = -1
            Bound2 = int(SignVer)*int(Vfile)

            Hfile = str(file_name)[4:7]
            SignH = str(file_name)[3]
            SignHor = 1
            if SignH is "w":
                SignHor = -1
            Bound1 = int(SignHor) * int(Hfile)

            # Geospatial data for the tile
            geo_in = [Bound2, 0.00083333333333333, 0.0, int(Bound1 + 5),
                      0.0, 0.0008333333333333333333]

            # save chunk as tiff file
            Save_as_tiff(name=output_tiff, data=data, geo=geo_in,
                         projection="WGS84")

        # create temporary names for output of the clipping data
        file_chunk = "%stemporary.tif" % (output_tiff)
        outputfile_name_chunk = os.path.join(file_chunk)

        # clip data
        Bound1, Bound2, Bound3, Bound4 = clip_data(latlim, lonlim,
                                                   output_tiff,
                                                   outputfile_name_chunk,
                                                   rangeLat,
                                                   rangeLon,
                                                   file_name)

        if Resample == 1:
            # Resample the data from 0.0008333 to a 0.001 degree grid
            Data, size_Y_out, size_X_out, geo_out, proj_out = Resample_DEM(
                outputfile_name_chunk, Bound1, Bound2, Bound3, Bound4)

        else:
            f = gdal.Open(outputfile_name_chunk)
            geo_out = f.GetGeoTransform()
            Data = np.array(f.GetRasterBand(1).ReadAsArray())
            proj_out = f.GetProjection()
            size_X_out = f.RasterXSize
            size_Y_out = f.RasterYSize
            f = None

        # Total size of the product so far
        size_Y_tot = int(size_Y_tot + size_Y_out)
        size_X_tot = int(size_X_tot + size_X_out)

        # create name for chunk
        FileNameEnd = "%s_temporary.tif" % (nameFile)
        nameForEnd = os.path.join(output_folder_trash, FileNameEnd)
        nameResults.append(str(nameForEnd))

        # save chunk as tiff file
        Save_as_tiff(name=nameForEnd, data=Data, geo=geo_out,
                     projection=proj_out)

    size_X_tot = int(size_X_tot/len(rangeLat))
    size_Y_tot = int(size_Y_tot/len(rangeLon))

    # merge chunk together resulting in 1 tiff map
    datasetTot = Merge_DEM(latlim, lonlim, nameResults, size_Y_tot,
                           size_X_tot)

    # name of the end result
    output_DEM_name = "DEM_HydroShed_m.tif"
    Save_name = os.path.join(output_folder, output_DEM_name)

    # Make geotiff file
    Save_as_tiff_end(name=Save_name, data=datasetTot, lonext=lonlim[0],
                     latext=latlim[1], geo=geo_out)

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

    datasetTot = np.zeros([size_Y_tot, size_X_tot])
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


def Resample_DEM(outputfile_name_chunk, Bound1, Bound2, Bound3, Bound4):
    """
    This function resample the DEM file from 0.0008333 degrees to 0.001

    Keyword arguments:
    outputfile_name_chunk -- [ymin, ymax], (values must be between -50 and 50)
    Bound1 -- [xmax], (maximum of lonlim[0] or boundary dem tile)
    Bound2 -- [ymax], (maximum of latlim[0] or boundary dem tile)
    Bound3 -- [xmin], (minimum of lonlim[1] or boundary dem tile)
    Bound4 -- [ymin], (minimum of latlim[1] or boundary dem tile)
    """
    # Resample data from a 0.0008333 degrees to a 0.001 degrees
    f = gdal.Open(outputfile_name_chunk)
    geo_in = f.GetGeoTransform()
    dataset = np.array(f.GetRasterBand(1).ReadAsArray())
    geo_out = (geo_in[0], 0.001, geo_in[2], geo_in[3], geo_in[4], -0.001)
    geo_out = tuple(geo_out)
    proj_in = f.GetProjection()
    size_X_in = f.RasterXSize
    size_Y_in = f.RasterYSize
    f = None
    mem = gdal.GetDriverByName('MEM')

    src = mem.Create('', size_X_in, size_Y_in, 1, gdal.GDT_UInt16)
    src.GetRasterBand(1).WriteArray(dataset)
    src.GetRasterBand(1).SetNoDataValue(-32768)
    src.SetGeoTransform(geo_in)
    src.SetProjection(proj_in)

    size_Y_out = int(round((Bound4-Bound2)/0.001))
    size_X_out = int(round((Bound3-Bound1)/0.001))
    proj_out = proj_in

    dest = mem.Create('', size_X_out, size_Y_out, 1, gdal.GDT_UInt16)
    dest.SetGeoTransform(geo_out)
    dest.SetProjection(proj_out)
    dest.GetRasterBand(1).SetNoDataValue(-32768)
    gdal.ReprojectImage(src, dest, proj_in, proj_out, gdal.GRA_Average)

    Data = dest.ReadAsArray(0).astype(float)
    return(Data, size_Y_out, size_X_out, geo_out, proj_out)


def Save_as_tiff(name='', data='', geo='', projection=''):
    """
    This function save the array as a geotiff

    Keyword arguments:
    name -- string, directory name
    data -- [array], dataset of the geotiff
    geo -- [minimum lon, pixelsize, rotation, maximum lat, rotation,
            pixelsize], (geospatial dataset)
    projection -- interger, the EPSG code
    """
    # save as a geotiff file with a resolution of 0.001 degree
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(name, int(data.shape[1]), int(data.shape[0]), 1,
                           gdal.GDT_Float32, ['COMPRESS=LZW'])
    srse = osr.SpatialReference()
    srse.SetWellKnownGeogCS(projection)
    dst_ds.SetProjection(srse.ExportToWkt())
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform(geo)
    dst_ds.GetRasterBand(1).WriteArray(data)
    dst_ds = None


def Save_as_tiff_end(name='', data='', lonext='', latext='', geo=''):
    """
    This function save the array as a geotiff for the merged end array
    The projection is in WGS84

    Keyword arguments:
    name -- string, directory name
    data -- [array], dataset of the geotiff
    lonext -- minimum longitude
    latext -- maximum latitude
    geo -- [lonlim[0], pixelsize, rotation, latlim[0], rotation, pixelsize]
           , (geospatial dataset)
    """
    # save as a geotiff file with a resolution of 0.001 degree
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(name, int(data.shape[1]), int(data.shape[0]), 1,
                           gdal.GDT_Float32, ['COMPRESS=LZW'])
    srse = osr.SpatialReference()
    srse.SetWellKnownGeogCS("WGS84")
    dst_ds.SetProjection(srse.ExportToWkt())
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform([lonext, geo[1], 0, latext, 0, geo[5]])
    dst_ds.GetRasterBand(1).WriteArray(data)
    dst_ds = None


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
        try:
            url = ("http://earlywarning.usgs.gov/hydrodata/sa_con_3s_grid/"
                   "%s/%s") % (continent, nameFile)

            site = urllib.urlopen(url)
            meta = site.info()
            if meta.getheaders("Content-Length")[0] > TotalSize:
                DoContinent = continent
                TotalSize = meta.getheaders("Content-Length")[0]
        except:
            continue

    url = ("http://earlywarning.usgs.gov/hydrodata/sa_con_3s_grid/"
           "%s/%s") % (DoContinent, nameFile)

    file_name = url.split('/')[-1]
    output_file = os.path.join(output_folder_trash, file_name)
    urllib.urlretrieve(url, output_file)
    return(output_file, file_name)


def Extract_Data(output_file, output_folder_trash):
    """
    This function extract the zip files

    Keyword Arguments:
    output_file -- name, name of the file that must be unzipped
    output_folder_trash -- Dir, directory where the unzipped data must be
                           stored
    """
    # extract the data
    z = zipfile.ZipFile(output_file, 'r')
    z.extractall(output_folder_trash)
    z.close()


def Convert_adf_to_tiff(file_name, output_folder_trash):
    """
    This function converts the adf files into tiff files

    Keyword Arguments:
    file_name -- name, name of the adf file
    output_folder_trash -- Dir, directory where the tiff data must be
                           stored
    """
    # Converts the data with a adf extention to a tiff extension.
    # The input is the file name and in which directory the data must be stored
    file_name_tiff = file_name.split('.')[0] + '_trans_temporary.tif'
    file_name_extract = file_name.split('_')[0:3]
    file_name_extract2 = file_name_extract[0]+'_'+file_name_extract[1]
    input_adf = os.path.join(output_folder_trash, file_name_extract2,
                             file_name_extract2, 'hdr.adf')
    output_tiff = os.path.join(output_folder_trash, file_name_tiff)

    # convert data from ESRI GRID to GeoTIFF
    command = ("gdal_translate -co COMPRESS=DEFLATE -co PREDICTOR=1 -co "
               "ZLEVEL=1 -of GTiff %s %s") % (input_adf, output_tiff)
    os.system(command)
    return(output_tiff)


def clip_data(latlim, lonlim, output_tiff, outputfile_name_chunk, rangeLat,
              rangeLon, file_name):
    """
    Clip the data to the defined extend of the user (latlim, lonlim) or to the
    extend of the DEM tile

    Keyword Arguments:
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    output_tiff -- input data, output of the convert_adf_to_tiff
    outputfile_name_chunk -- output data, output of the clipped dataset
    rangeLat -- Latitude extend of the tile
    rangeLon -- Longitude extend of the tile
    file_name -- name of the input file
    """
    # clip data to the extend defined by the user
    os.system('gdalbuildvrt DEM.vrt %s' % output_tiff)

    # set the clipping extend the same as the extend defined by the user
    Bound1 = lonlim[0]
    Bound2 = latlim[0]
    Bound3 = lonlim[1]
    Bound4 = latlim[1]

    # Adjust the extend if the extend defined by the user is larger than the
    # downloaded tile
    if len(rangeLat) > 1:
        Vfile = str(file_name)[1:3]
        SignV = str(file_name)[0]
        SignVer = 1
        if SignV is "s":
            SignVer = -1
        Bound2 = int(SignVer) * int(Vfile)
        Bound4 = Bound2 + int(5)
        if latlim[0] > Bound2 and latlim[0] < Bound4:
            Bound2 = latlim[0]
        if latlim[1] > Bound2 and latlim[1] < Bound4:
            Bound4 = latlim[1]

    if len(rangeLon) > 1:
        Hfile = str(file_name)[4:7]
        SignH = str(file_name)[3]
        SignHor = 1
        if SignH is "w":
            SignHor = -1
        Bound1 = int(SignHor) * int(Hfile)
        Bound3 = Bound1 + int(5)
        if lonlim[0] > Bound1 and lonlim[0] < Bound3:
            Bound1 = lonlim[0]
        if lonlim[1] > Bound1 and lonlim[1] < Bound3:
            Bound3 = lonlim[1]

    # create the boundary box which is used for the clipping
    Bounding = '%s %s %s %s' % (Bound1, Bound2, Bound3, Bound4)

    # clips the data
    command = 'gdalwarp -te %s DEM.vrt %s' % (Bounding, outputfile_name_chunk)
    os.system(command)
    return(Bound1, Bound2, Bound3, Bound4)
