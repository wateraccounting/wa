# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref

Description:
This module creates ETref data. The data will first be collected by downloading 
CFSR, HydroSHED, and GLDAS data.
The LANDSAF data can also be used by using the LANDSAF=1 code. The downloading 
of LANDSAF data is not automated, so you have to download this data by yourself
and define the path to this data in the SoureLANDSAF parameter.

LANDSAF:
The LANDSAF data can be downloaded from CMSAF.eu. You need to have the following directories:
~LANDSAF/SIS/SISdm200501310000001190010801GL.nc.gz
~LANDSAF/SID/DNIdm200501010000002231000101MA.nc.gz

The ~LANDSAF is the path which you have to define as the SourceLANDSAF parameter

ETref.monthly(Dir='C:/TempR/', Startdate='2012-09-01', Enddate='2012-12-31',
           latlim=[33, 35], lonlim=[35, 37], pixel_size=0.01)
ETref.daily(Dir='C:/TempTestLANDSAF3/', Startdate='2005-01-02', Enddate='2005-01-04',
           latlim=[33, 35], lonlim=[35, 37], LANDSAF=1, SourceLANDSAF =r'D:\LANDSAF')
"""

from .daily import main as daily
from .monthly import main as monthly

__all__ = ['daily', 'monthly']

__version__ = '0.1'
