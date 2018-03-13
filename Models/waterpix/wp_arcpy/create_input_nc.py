# -*- coding: utf-8 -*-
"""
Authors: Gonzalo E. Espinoza-Dávalos
         IHE Delft 2017
Contact: g.espinoza@un-ihe.org
Repository: https://github.com/gespinoza/waterpix
Module: waterpix
"""

from __future__ import division
import os
import tempfile
import arcpy
import pandas as pd
import netCDF4


def create_input_nc(start_date, years,
                    cellsize, basin_shp,
                    p_path, et_path, eto_path, lai_path,
                    swi_path, swio_path, swix_path,
                    qratio_path, rainydays_path,
                    thetasat_ras, rootdepth_ras,
                    input_nc, epsg=4326, bbox=None):
    """
    Creates the input netcdf file required to run waterpix
    """
    # Script parameters
    print "Variable\tRaster"
    arcpy.CheckOutExtension('spatial')
    if bbox:
        latlim = [bbox[1], bbox[3]]
        lonlim = [bbox[0], bbox[2]]
    else:
        shp_extent = arcpy.Describe(basin_shp).extent
        latlim = [shp_extent.YMin, shp_extent.YMax]
        lonlim = [shp_extent.XMin, shp_extent.XMax]
    arcpy.env.extent = arcpy.Extent(lonlim[0], latlim[0], lonlim[1], latlim[1])
    arcpy.env.cellSize = cellsize

    time_range = pd.date_range(start_date, periods=12*years, freq='MS')
    time_ls = [d.strftime('%Y%m') for d in time_range]
    time_dt = [pd.to_datetime(i, format='%Y%m')
               for i in time_ls]

    time_n = len(time_ls)

    years_ls = set()
    years_ls = [i.year for i in time_dt
                if i.year not in years_ls and not years_ls.add(i.year)]

    time_indeces = {}

    for j, item in enumerate(years_ls):
        temp_ls = [int(i.strftime('%Y%m')) for i in
                   pd.date_range(str(item) + '0101',
                                 str(item) + '1231', freq='MS')]
        time_indeces[item] = [time_ls.index(str(i)) for i in temp_ls]

    for key in time_indeces.keys():
        if time_indeces[key] != range(time_indeces[key][0],
                                      time_indeces[key][-1] + 1):
            raise Exception('The year {0} in the netcdf file is incomplete'
                            ' or the dates are non-consecutive')

    all_paths = {'p': p_path, 'et': et_path, 'eto': eto_path, 'lai': lai_path,
                 'swi': swi_path, 'swio': swio_path, 'swix': swix_path,
                 'qratio': qratio_path, 'rainydays': rainydays_path}

    # Latitude and longitude
    lat_ls = pd.np.arange(latlim[0] + 0.5*cellsize, latlim[1] + 0.5*cellsize,
                          cellsize)
    lat_ls = lat_ls[::-1]  # ArcGIS numpy
    lon_ls = pd.np.arange(lonlim[0] + 0.5*cellsize, lonlim[1] + 0.5*cellsize,
                          cellsize)
    lat_n = len(lat_ls)
    lon_n = len(lon_ls)
    spa_ref = arcpy.SpatialReference(epsg)
    projection = spa_ref.exportToString()
    ll_corner = arcpy.Point(lonlim[0], latlim[0])

    # Snap raster
    temp_ras = arcpy.NumPyArrayToRaster(pd.np.zeros((lat_n, lon_n)),
                                        ll_corner,
                                        cellsize, cellsize)
    scratch_ras = arcpy.CreateScratchName('ras_', '.tif', '',
                                          arcpy.env.scratchFolder)
    temp_ras.save(scratch_ras)
    arcpy.management.DefineProjection(scratch_ras, spa_ref)
    arcpy.env.snapRaster = scratch_ras

    # Basin mask
    basin_ras = arcpy.CreateScratchName('bas_', '.tif', '',
                                        arcpy.env.scratchFolder)
    buff_shp = arcpy.CreateScratchName('bas_', '.shp', '',
                                       arcpy.env.scratchFolder)
    arcpy.analysis.Buffer(basin_shp, buff_shp, 2*cellsize,
                          'FULL', 'ROUND', 'NONE', '#', 'PLANAR')
    arcpy.conversion.FeatureToRaster(buff_shp, "FID",
                                     basin_ras, cellsize)

    # Create NetCDF file
    nc_file = netCDF4.Dataset(input_nc, 'w', format="NETCDF4")
    nc_file.set_fill_on()

    # Create dimensions
    lat_dim = nc_file.createDimension('latitude', lat_n)
    lon_dim = nc_file.createDimension('longitude', lon_n)
    month_dim = nc_file.createDimension('time_yyyymm', time_n)
    year_dim = nc_file.createDimension('time_yyyy', len(years_ls))

    # Create NetCDF variables
    crs_var = nc_file.createVariable('crs', 'i', (), fill_value=-9999)
    crs_var.standard_name = 'crs'
    crs_var.grid_mapping_name = 'latitude_longitude'
    crs_var.crs_wkt = projection

    lat_var = nc_file.createVariable('latitude', 'f8', ('latitude'),
                                     fill_value=-9999)
    lat_var.units = 'degrees_north'
    lat_var.standard_name = 'latitude'

    lon_var = nc_file.createVariable('longitude', 'f8', ('longitude'),
                                     fill_value=-9999)
    lon_var.units = 'degrees_east'
    lon_var.standard_name = 'longitude'

    month_var = nc_file.createVariable('time_yyyymm', 'l', ('time_yyyymm'),
                                       fill_value=-9999)
    month_var.standard_name = 'time'
    month_var.format = 'YYYYMM'

    year_var = nc_file.createVariable('time_yyyy', 'l', ('time_yyyy'),
                                      fill_value=-9999)
    year_var.standard_name = 'time'
    year_var.format = 'YYYY'

    # Variables
    p_var = nc_file.createVariable('Precipitation_M', 'f8',
                                   ('time_yyyymm', 'latitude', 'longitude'),
                                   fill_value=-9999)
    p_var.long_name = 'Precipitation'
    p_var.units = 'mm/month'

    py_var = nc_file.createVariable('Precipitation_Y', 'f8',
                                    ('time_yyyy', 'latitude', 'longitude'),
                                    fill_value=-9999)
    py_var.long_name = 'Precipitation'
    py_var.units = 'mm/year'

    et_var = nc_file.createVariable('Evapotranspiration_M', 'f8',
                                    ('time_yyyymm', 'latitude', 'longitude'),
                                    fill_value=-9999)
    et_var.long_name = 'Evapotranspiration'
    et_var.units = 'mm/month'

    ety_var = nc_file.createVariable('Evapotranspiration_Y', 'f8',
                                     ('time_yyyy', 'latitude', 'longitude'),
                                     fill_value=-9999)
    ety_var.long_name = 'Evapotranspiration'
    ety_var.units = 'mm/year'

    eto_var = nc_file.createVariable('ReferenceET_M', 'f8',
                                     ('time_yyyymm', 'latitude', 'longitude'),
                                     fill_value=-9999)
    eto_var.long_name = 'Reference Evapotranspiration'
    eto_var.units = 'mm/month'

    lai_var = nc_file.createVariable('LeafAreaIndex_M', 'f8',
                                     ('time_yyyymm', 'latitude', 'longitude'),
                                     fill_value=-9999)
    lai_var.long_name = 'Leaf Area Index'
    lai_var.units = 'm2/m2'

    swi_var = nc_file.createVariable('SWI_M', 'f8',
                                     ('time_yyyymm', 'latitude', 'longitude'),
                                     fill_value=-9999)
    swi_var.long_name = 'Soil Water Index - Monthly mean'
    swi_var.units = '%'

    swio_var = nc_file.createVariable('SWIo_M', 'f8',
                                      ('time_yyyymm', 'latitude', 'longitude'),
                                      fill_value=-9999)
    swio_var.long_name = 'Soil water index - First day of the month'
    swio_var.units = '%'

    swix_var = nc_file.createVariable('SWIx_M', 'f8',
                                      ('time_yyyymm', 'latitude', 'longitude'),
                                      fill_value=-9999)
    swix_var.long_name = 'Soil water index - Last day of the month'
    swix_var.units = '%'

    qratio_var = nc_file.createVariable('RunoffRatio_Y', 'f8',
                                        ('time_yyyy',
                                         'latitude', 'longitude'),
                                        fill_value=-9999)
    qratio_var.long_name = 'Runoff ratio'
    qratio_var.units = '-'

    rainydays_var = nc_file.createVariable('RainyDays_M', 'f8',
                                           ('time_yyyymm',
                                            'latitude', 'longitude'),
                                           fill_value=-9999)
    rainydays_var.long_name = 'Number of rainy days per month'
    rainydays_var.units = 'No. rainy days/month'

    thetasat_var = nc_file.createVariable('SaturatedWaterContent', 'f8',
                                          ('latitude', 'longitude'),
                                          fill_value=-9999)
    thetasat_var.long_name = 'Saturated water content (top soil)'
    thetasat_var.units = 'cm3/cm3'

    rootdepth_var = nc_file.createVariable('RootDepth', 'f8',
                                           ('latitude', 'longitude'),
                                           fill_value=-9999)
    rootdepth_var.long_name = 'Root depth'
    rootdepth_var.units = 'mm'

    basinmask_var = nc_file.createVariable('BasinBuffer', 'l',
                                           ('latitude', 'longitude'),
                                           fill_value=0)
    basinmask_var.long_name = 'Basin buffer'

    # Load data
    lat_var[:] = lat_ls
    lon_var[:] = lon_ls
    month_var[:] = time_ls
    year_var[:] = years_ls

    # Static variables
    temp_dir = tempfile.mkdtemp()

    # Theta sat
    print "{0}\t{1}".format('thetasat', thetasat_ras)
    thetasat_temp = os.path.join(temp_dir, 'thetasat.tif')
    arcpy.management.Resample(thetasat_ras, thetasat_temp,
                              cellsize)
    inp_ras = arcpy.Raster(thetasat_temp)

    array = arcpy.RasterToNumPyArray(inp_ras, ll_corner, lon_n, lat_n, -9999)
    thetasat_var[:, :] = array[:, :]

    # Root depth
    print "{0}\t{1}".format('rootdepth', rootdepth_ras)
    rootdepth_temp = os.path.join(temp_dir, 'rootdepth.tif')
    arcpy.management.Resample(rootdepth_ras, rootdepth_temp,
                              cellsize)
    inp_ras = arcpy.Raster(rootdepth_temp)

    array = arcpy.RasterToNumPyArray(inp_ras, ll_corner, lon_n, lat_n, -9999)
    rootdepth_var[:, :] = array[:, :]

    # Basin mask
    inp_ras = arcpy.sa.Con(arcpy.sa.IsNull(arcpy.Raster(basin_ras)), 0, 1)

    array = arcpy.RasterToNumPyArray(inp_ras, ll_corner, lon_n, lat_n, -9999)
    basinmask_var[:, :] = array[:, :]

    # Dynamic variables
    for var in ['p', 'et', 'eto', 'lai',
                'swi', 'swio', 'swix', 'rainydays']:
        # Make temp directory
        temp_dir2 = tempfile.mkdtemp()
        for yyyymm in time_ls:
            yyyy = yyyymm[:4]
            mm = yyyymm[-2:]
            ras = all_paths[var].format(yyyy=yyyy, mm=mm)
            print "{0}\t{1}".format(var, ras)
            arcpy.management.Resample(ras, os.path.join(temp_dir2,
                                                        os.path.basename(ras)),
                                      cellsize, 'NEAREST')
            inp_ras = arcpy.Raster(os.path.join(temp_dir2,
                                                os.path.basename(ras)))
            array = arcpy.RasterToNumPyArray(inp_ras, ll_corner,
                                             lon_n, lat_n, pd.np.nan)
            t_index = time_ls.index(yyyymm)
            exec('{0}_var[t_index, :, :] = array[:, :]'.format(var))
    # Runoff ratio
    temp_dir2 = tempfile.mkdtemp()
    for yyyy in years_ls:
        ras = all_paths['qratio'].format(yyyy=yyyy)
        print "{0}\t{1}".format('qratio', ras)
        arcpy.management.Resample(ras, os.path.join(temp_dir2,
                                                    os.path.basename(ras)),
                                  cellsize, 'NEAREST')
        inp_ras = arcpy.Raster(os.path.join(temp_dir2,
                                            os.path.basename(ras)))
        array = arcpy.RasterToNumPyArray(inp_ras, ll_corner,
                                         lon_n, lat_n, pd.np.nan)
        y_index = years_ls.index(yyyy)
        qratio_var[y_index, :, :] = array[:, :]
    # Calculate yearly rasters
    for yyyy in years_ls:
        yyyyi = years_ls.index(yyyy)
        ti1 = time_indeces[yyyy][0]
        ti2 = time_indeces[yyyy][-1] + 1

        py_var[yyyyi, :, :] = pd.np.sum(p_var[ti1:ti2, :, :], axis=0)
        ety_var[yyyyi, :, :] = pd.np.sum(et_var[ti1:ti2, :, :], axis=0)

    # Close file
    arcpy.env.extent = None
    arcpy.env.snapRaster = None
    arcpy.env.cellSize = 'MAXOF'
    nc_file.close()

    # Return
    return input_nc
