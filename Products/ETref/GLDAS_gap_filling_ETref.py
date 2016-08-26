# -*- coding: utf-8 -*-
'''
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
'''

# import general python modules
import gdal
import numpy as np
import scipy.interpolate

# import WA+ modules
from StandardDef_ETref import GetGeoInfo, CreateGeoTiff

def gap_filling(dataset,NoDataValue):
    """
    This function fills the no data gaps in a numpy array
				
    Keyword arguments:
    dataset -- 'C:/'  path to the source data (dataset that must be filled)
    NoDataValue -- Value that must be filled
    """
	
    # Open the numpy array
    t = gdal.Open(dataset)
    data = t.ReadAsArray()

    # fill the no data values
    if NoDataValue is np.nan:
        mask = ~(np.isnan(data))
    else:
        mask = ~(data==NoDataValue)
    xx, yy = np.meshgrid(np.arange(data.shape[1]), np.arange(data.shape[0]))
    xym = np.vstack( (np.ravel(xx[mask]), np.ravel(yy[mask])) ).T
    data0 = np.ravel( data[:,:][mask] )
    interp0 = scipy.interpolate.NearestNDInterpolator( xym, data0 )
    data_end = interp0(np.ravel(xx), np.ravel(yy)).reshape( xx.shape )
    dataset_GF = dataset[:-4] + '_GF'
				
    # collect the geoinformation			
    NDV_data, xsize_data, ysize_data, GeoT_data, Projection_data, DataType_data = GetGeoInfo(dataset)
				
    # Save the filled array as geotiff				
    CreateGeoTiff(dataset_GF,data_end, NDV_data, xsize_data, ysize_data, GeoT_data, Projection_data, DataType_data)
    EndProduct=dataset[:-4] + '_GF.tif'   
				
    return (EndProduct)
