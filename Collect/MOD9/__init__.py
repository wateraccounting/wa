# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD13

Description:
This module downloads MOD13 NDVI data from
http://e4ftl01.cr.usgs.gov/. Use the MOD13.NDVI_16daily function to
download and create 16 daily NDVI images in Gtiff format.
The data is available between 2000-02-18 till present.

Examples:
from wa.Collect import MOD9
MOD9.REF_daily(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])
"""

from .REF_daily import main as REF_daily

__all__ = ['REF_daily']

__version__ = '0.1'
