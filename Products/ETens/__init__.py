# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETens

Description:
This module downloads ETensV1.0 data from
ftp.wateraccounting.unesco-ihe.org. Use the monthy function to
download and create monthly ET images in Gtiff format.
The data is available between 2003-01-01 till 2014-12-31.

Examples:
from wa.Products import ETens
ETens.monthly(Dir='C:/Temp/', Startdate='2003-12-01', Enddate='2003-12-20',
           latlim=[41, 45], lonlim=[-8, -5])   
"""

from .monthly import main as monthly

__all__ = ['monthly']

__version__ = '0.1'
