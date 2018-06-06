# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MYD13

Description:
This module downloads MYD13 NDVI data from
http://e4ftl01.cr.usgs.gov/. Use the MYD13.NDVI_16daily function to
download and create 16 daily NDVI images in Gtiff format.
The data is available between 2000-02-18 till present.

Examples:
from wa.Collect import MYD13
MYD13.NDVI_16daily(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])
"""

from .NDVI_16daily import main as NDVI_16daily

__all__ = ['NDVI_16daily']

__version__ = '0.1'
