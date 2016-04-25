# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Level1/CHIRPS


Description:
This module downloads daily and monthly CHIRPS 2.0 data from
ftp://chg-ftpout.geog.ucsb.edu server.


download and create daily or monthly TRMM images in Gtiff format.
The CHIRP data is available since 1981-01-01 till the present. Use the
CHIRPS.daily or CHIRPS.monthly functions to download and create daily or
monthly CHIRPS images in Gtiff format

Examples:
from wa.Level1 import CHIRPS
CHIRPS.daily(Dir='C:/Temp/', Startdate='1999-02-01', Enddate='1999-02-22',
             latlim=[-10, 30], lonlim=[-20, 120], cores=2)
CHIRPS.monthly(Dir='C:/Temp/', Startdate='1999-02-01', Enddate='1999-02-28',
               latlim=[-10, 30], lonlim=[-20, 120], cores=2)
"""

from .daily import main as daily
from .monthly import main as monthly

__all__ = ['daily', 'monthly']

__version__ = '0.1'
