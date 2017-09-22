# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD12

Description:
This module downloads MOD12 LC data from
http://e4ftl01.cr.usgs.gov/. Use the MOD12.LC_yearly function to
download and create yearly LC images in Gtiff format.
The data is available between 2001-01-01 till 2014-01-01 .

Examples:
from wa.Collect import MOD12
MOD17.LC_yearly(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])
MOD17.LC_yearly(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])		   
"""

from .LC_yearly import main as LC_yearly

__all__ = ['LC_yearly']

__version__ = '0.1'
