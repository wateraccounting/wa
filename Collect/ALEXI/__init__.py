# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/ALEXI

Restrictions:
The data and this python file may not be distributed to others without
permission of the WA+ team due data restriction of the ALEXI developers.

Description:
This module downloads ALEXI data from
ftp.wateraccounting.unesco-ihe.org. Use the ALEXI.daily function to
download and create weekly ALEXI images in Gtiff format.
The data is available between 2003-01-01 till 2015-12-31.

The output file with the name 2003.01.01 contains the total evaporation in mm
for the period of 1 January - 7 January.

Examples:
from wa.Collect import ALEXI
ALEXI.weekly(Dir='C:/Temp/', Startdate='2003-12-01', Enddate='2004-01-20',
           latlim=[-10, 30], lonlim=[-20, -10])
"""

from .daily import main as daily
from .weekly import main as weekly
from .monthly import main as monthly

__all__ = ['daily', 'weekly', 'monthly']

__version__ = '0.1'
