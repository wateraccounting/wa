"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Level1/TRMM


Description:
This module downloads TRMM3B42 V7 (daily) and TRMM3B43 V7 (monthly) data from
ftp://disc2.nascom.nasa.gov. Use the TRMM_daily or TRMM_monthly definitions to
download and create daily or monthly TRMM images in Gtiff format.
The TRMM data is available since 1998-01-01 till 2015-04-30

Examples:
from wa.Level1 import TRMM
TRMM.daily(Dir='C:/Temp/', Startdate='1999-02-01', Enddate='1999-02-28',
           latlim=[-10, 30], lonlim=[-20, 120], cores=2)
TRMM.monthly(Dir='C:/Temp/', Startdate='1999-02-01', Enddate='1999-02-28',
             latlim=[-10, 30], lonlim=[-20, 120], cores=2)
"""

from .daily import main as daily
from .monthly import main as monthly

__all__ = ['daily', 'monthly']

__version__ = '0.1'
