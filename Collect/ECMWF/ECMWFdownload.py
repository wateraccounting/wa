# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 09:54:37 2017

@author: tih
"""

 
def API(output_folder, DownloadType, string1, string2, string3, string4, string5, string6, string7, string8, string9, string10):

    import os
    from ecmwfapi import ECMWFDataServer
    os.chdir(output_folder)	
    server = ECMWFDataServer()

    if DownloadType == 1 or DownloadType == 2:
        server.retrieve({
            'stream'    : "%s" %string1,
            'levtype'   : "%s" %string2,
            'param'     : "%s" %string3,
            'dataset'   : "interim",
            'step'      : "%s" %string4,
            'grid'      : "%s" %string5,
            'time'      : "%s" %string6,
            'date'      : "%s" %string7,
            'type'      : "%s" %string8,     # http://apps.ecmwf.int/codes/grib/format/mars/type/
            'class'     : "%s" %string9,     # http://apps.ecmwf.int/codes/grib/format/mars/class/
            'area'      : "%s" %string10,   							
            'format'    : "netcdf",
            'target'    : "data_interim.nc"
            })

    if DownloadType == 3:
        server.retrieve({
            'levelist'   : "1000",
            'stream'    : "%s" %string1,
            'levtype'   : "%s" %string2,
            'param'     : "%s" %string3,
            'dataset'   : "interim",
            'step'      : "%s" %string4,
            'grid'      : "%s" %string5,
            'time'      : "%s" %string6,
            'date'      : "%s" %string7,
            'type'      : "%s" %string8,     # http://apps.ecmwf.int/codes/grib/format/mars/type/
            'class'     : "%s" %string9,     # http://apps.ecmwf.int/codes/grib/format/mars/class/
            'area'      : "%s" %string10,   							
            'format'    : "netcdf",
            'target'    : "data_interim.nc"
            })
	
	
    return()
	
	
	
	
	