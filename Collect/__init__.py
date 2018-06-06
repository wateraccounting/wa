# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect


Description:
This module contains scripts used to download Level 1 data (data directly from web).

Examples:
from wa import Collect
help(Collect)
dir(Collect)
"""

from wa.Collect import TRMM, GLDAS, ALEXI, CHIRPS, DEM, CFSR, MOD9, MOD10, MOD11, MOD12, MOD13, MOD15, MOD16, MOD17, MCD43, MYD13, GLEAM, HiHydroSoil, ECMWF, RFE, JRC, TWC, ETmonitor, SEBS, SSEBop, CMRSET, MSWEP, ASCAT

__all__ = ['TRMM', 'GLDAS', 'ALEXI', 'CHIRPS', 'DEM', 'CFSR', 'MOD9', 'MOD10', 'MOD11', 'MOD12', 'MOD13', 'MOD15', 'MOD16', 'MOD17', 'MCD43', 'MYD13', 'GLEAM', 'HiHydroSoil', 'ECMWF', 'RFE', 'JRC', 'TWC', 'ETmonitor', 'SEBS', 'SSEBop', 'CMRSET', 'MSWEP', 'ASCAT']

__version__ = '0.1'
