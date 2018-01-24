# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD16

Description:
This module downloads MOD16 ET data from
http://e4ftl01.cr.usgs.gov/. Use the MOD16.ET_monthly function to
download and create monthly ET images in Gtiff format.
The data is available between 2000-01-01 till 2014-12-31.

Examples:
from wa.Collect import MOD16
MOD16.ET_monthly(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])
"""

from .ET_monthly import main as ET_monthly
from .ET_8daily import main as ET_8daily

__all__ = ['ET_monthly', 'ET_8daily']

__version__ = '0.1'
