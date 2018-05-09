# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD11

Description:
This module downloads MOD11 LST data from
http://e4ftl01.cr.usgs.gov/. Use the MOD11.LST_8daily function to
download and create 8 daily LST images in Gtiff format.
The data is available between 2000-02-18 till present.

Examples:
from wa.Collect import MOD11
MOD11.LST_8daily(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-30',
           latlim=[41, 45], lonlim=[-8, -5])
"""

from .LST_8daily import main as LST_8daily
from .LST_daily import main as LST_daily

__all__ = ['LST_8daily', 'LST_daily']

__version__ = '0.1'
