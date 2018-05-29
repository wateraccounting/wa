# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2018
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MCD43

Description:
This module downloads MCD43 reflectance data from
https://e4ftl01.cr.usgs.gov/. Use the MCD43.Albedo_daily function to
download and create daily Reflectance images in Gtiff format.
The data is available between 2000-02-18 till present.

Examples:
from wa.Collect import MCD43
MCD43.Albedo_daily(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])
"""

from .Albedo_daily import main as Albedo_daily

__all__ = ['Albedo_daily']

__version__ = '0.1'
