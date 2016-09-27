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

from wa.Collect import TRMM, GLDAS, ALEXI, CHIRPS, DEM, CFSR, MOD13, MOD15, MOD16, MOD17

__all__ = ['TRMM', 'GLDAS', 'ALEXI', 'CHIRPS', 'DEM', 'CFSR', 'MOD13', 'MOD15', 'MOD16', 'MOD17']

__version__ = '0.1'
