# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD17

Description:
This module downloads MOD17 GPP data from
http://e4ftl01.cr.usgs.gov/. Use the MOD17.GPP_8daily function to
download and create 8 daily GPP images in Gtiff format.
The data is available between 2000-02-18 till present.

Examples:
from wa.Collect import MOD17
MOD17.GPP_8daily(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])
MOD17.NPP_yearly(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])		   
"""

from .GPP_8daily import main as GPP_8daily
from .NPP_yearly import main as NPP_yearly

__all__ = ['GPP_8daily', 'NPP_yearly']

__version__ = '0.1'
