# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/CFSR

Description:
This module downloads CFSR (daily or monthly) radiation data from
ftp://nomads.ncdc.noaa.gov. Use the CFSR.daily, CFSRv2.daily, CFSR.monthly, or CFSRv2.monthly functions to
download and create daily or monthly CSFR/CSFRv2 radiation images in Gtiff format.
The CFSR data is available since 1979-01-01 till 2011-03-31
The CFSRv2 data is available since 2011-04-01 till now

Examples:
from wa.Collect import CFSR
CFSR.daily(Dir='C:/Temp/', Vars = ['dlwsfc'], Startdate='2011-03-01', Enddate='2011-04-15',
           latlim=[-10, 30], lonlim=[-20, 120])
!CFSR.monthly(Dir='C:/Temp/', ['uswsfc','dswsfc'], Startdate='1999-02-01', Enddate='1999-02-28',
!             latlim=[-10, 30], lonlim=[-20, 120]) (Still in progress at the moment!!!)
"""

from .daily import main as daily
#from .monthly import main as monthly

__all__ = ['daily']

__version__ = '0.1'