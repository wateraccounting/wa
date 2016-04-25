# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Level1


Description:
This module contains scripts used to download Level 1 data.

Examples:
from wa import Level1
help(Level1)
dir(Level1)
"""

from wa.Level1 import TRMM, GLDAS, ALEXI

__all__ = ['TRMM', 'GLDAS', 'ALEXI']

__version__ = '0.1'
