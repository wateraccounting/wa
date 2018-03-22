# -*- coding: utf-8 -*-
"""
Authors: Gert Mulder, Tim Hessels, and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/GLDAS


Description:
This script automatically downloads GLDAS 2.0 or 2.1 data with a 0.25 degree
resolution for different extends based on their opendap server. The time
interval available are: three-hourly ('3hour'), daily ('day'), and monthly
('month'). A list of the variables can be printed with the command:
    GLDAS.VarInfo('daily').descriptions.keys()
Futher information of the variable can be printed with the following commands:
    GLDAS.VarInfo('daily').descriptions['evap']
    GLDAS.VarInfo('daily').units['evap']
    GLDAS.VarInfo('daily').names['evap']
    GLDAS.VarInfo('daily').factors['evap']

Examples:
from wa.Collect import GLDAS
GLDAS.three_hourly(Dir='C:/Temp/', Vars=['qair','tair'], Startdate='2004-12-20', Enddate='2005-01-10',
                   latlim=[38, 41], lonlim=[-76, -73], Periods=[4, 5], gldas_version = '2.1')
GLDAS.daily(Dir='C:/Temp/', Vars=['qair'], Startdate='2004-12-20', Enddate='2005-01-01',
            latlim=[38, 41], lonlim=[-76, -73],
            SumMean=1, Min=1, Max=1, gldas_version = '2.1')
GLDAS.monthly(Dir='C:/TempGLDAS', Vars=['swnet'], Startdate='2004-12-20', Enddate='2005-03-10',latlim=[38, 41], lonlim=[-76, -73], gldas_version = '2.1')
"""

from .three_hourly import main as three_hourly
from .daily import main as daily
from .monthly import main as monthly
from .DataAccess import VariablesInfo as VarInfo
from .CLSM_DataAccess import VariablesInfo as CLSM_VarInfo
from .CLSM_daily import main as CLSM_daily
from .CLSM_monthly import main as CLSM_monthly

__all__ = ['three_hourly', 'daily', 'monthly', 'VarInfo', 'CLSM_VarInfo', 'CLSM_daily', 'CLSM_monthly']

__version__ = '0.1'
