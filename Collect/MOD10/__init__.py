# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MOD10

Description:
This module downloads MOD10 SnowFrac data from
https://n5eil01u.ecs.nsidc.org/MOST/MOD10A2.006. Use the MOD10.SnowFrac_8daily function to
download and create 8 daily SnowFrac images in Gtiff format.
The data is available between 2000-02-18 till present.

Examples:
from wa.Collect import MOD10
MOD10.SnowFrac_8daily(Dir='C:/Temp4/',Startdate='2003-12-01',Enddate='2003-12-20',
                                 latlim=[30,35],lonlim=[70,75])   
"""

from .SnowFrac_8daily import main as SnowFrac_8daily

__all__ = ['SnowFrac_8daily']

__version__ = '0.1'
