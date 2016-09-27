# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD15

Description:
This module downloads MOD15 FPAR data from
http://e4ftl01.cr.usgs.gov/. Use the MOD15.FPAR_16daily function to
download and create 16 daily FPAR images in Gtiff format.
The data is available between 2000-02-18 till present.

Examples:
from wa.Collect import MOD15
MOD15.FPAR_16daily(Dir='C:/Temp3/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])
"""

from .FPAR_16daily import main as FPAR_16daily

__all__ = ['FPAR_16daily']

__version__ = '0.1'
