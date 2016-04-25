# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 09:27:36 2016

@author: tih
"""


def Path(Type=None, Change=False, New=None):

    Paths = {
            'gdalwarp': 'C:\\Anaconda2\\Lib\\site-packages\\osgeo\\gdalwarp.exe',
            'gdal_translate': 'C:\\Anaconda2\\Library\\bin\\gdal_translate.exe',
            'curl': 'C:\\Users\\ged\\Documents\\Programs\\cURL\\bin\\curl.exe',
            '7zip': 'D:\\FTP\\Programs\\7zip\\7za.exe'}

    Selected_Path = Paths[Type]

    return(Selected_Path)

'''
from wa.Level1 import CFSR
CFSR.DLWR_Daily('1986-02-01', '1986-03-01', [29, 31], [-96, -98], r'C:\Temp')
'''
