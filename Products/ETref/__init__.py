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
or
~LANDSAF/SIS/SISdm20140903000000123MVMFG01ME.nc.gz
and
~LANDSAF/SID/DNIdm200501010000002231000101MA.nc.gz
or
~LANDSAF/SID/SIDdm20140903000000123MVMFG01ME.nc.gz

The ~LANDSAF is the path which you have to define as the SourceLANDSAF parameter

ETref.monthly(Dir='C:/TempR/', Startdate='2012-09-01', Enddate='2012-09-02',
           latlim=[33, 35], lonlim=[35, 37], pixel_size=0.01)
ETref.daily(Dir='C:/TempTestLANDSAF3/', Startdate='2014-09-01', Enddate='2014-09-03',
           latlim=[27, 28], lonlim=[29, 30], pixel_size = 0.01, LANDSAF=1, SourceLANDSAF =r'C:\Users\tih\Documents\Water_Accounting\Landsaf')
"""

from .daily import main as daily
from .monthly import main as monthly

__all__ = ['daily', 'monthly']

__version__ = '0.1'
