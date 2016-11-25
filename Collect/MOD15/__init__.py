# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD15

Description:
This module downloads MOD15 FPAR data from
http://e4ftl01.cr.usgs.gov/. Use the MOD15.FPAR_8daily function to
download and create 8 daily FPAR images in Gtiff format.
The data is available between 2000-02-18 till present.

Examples:
from wa.Collect import MOD15
MOD15.FPAR_8daily(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])
MOD15.LAI_8daily(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])		   
"""

from .FPAR_8daily import main as FPAR_8daily
from .LAI_8daily import main as LAI_8daily

__all__ = ['FPAR_8daily', 'LAI_8daily']

__version__ = '0.1'
