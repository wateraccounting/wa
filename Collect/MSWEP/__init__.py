# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/MSWEP


Description:
This script automatically downloads MSWEP 2.1 data with a 0.1 degree
resolution for different extends based on their opendap server. The time
interval available are: daily ('day') or monthly ('month'). 

Examples:
from wa.Collect import MSWEP
MSWEP.daily(Dir='C:/Temp', Startdate='2004-12-20', Enddate='2005-01-01',
            latlim=[38, 41], lonlim=[-76, -73])
MSWEP.monthly(Dir='C:/Temp', Startdate='2004-12-20', Enddate='2005-03-10',latlim=[38, 41], lonlim=[-76, -73])
"""

from .daily import main as daily
from .monthly import main as monthly

__all__ = ['daily', 'monthly']

__version__ = '0.1'
