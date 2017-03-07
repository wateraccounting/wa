# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/ECMWF

Before running this tool, please install the ecmwfapi. You can find the manual here:
https://software.ecmwf.int/wiki/display/WEBAPI/Access+ECMWF+Public+Datasets

from wa.Collect import ECMWF
ECMWF.monthly(Dir="C:/test2", Vars = ['T'], Startdate = '2008-01-01' , Enddate = '2008-02-02', latlim = [30.1, 50.1], lonlim = [-20.1, 20.1])
ECMWF.daily(Dir="C:/test2", Vars = ['10U','10V','2D','SR','AL','HCC','TP'], Startdate = '2003-01-01' , Enddate = '2003-02-28', latlim = [30.1, 50.1], lonlim = [20, 40])

Suported parameters are: 'T','SP','Q','SSR','R','E','SUND','RO','TP', '10U', '10V, '2D', 'SR', 'AL', 'HCC' More will be follow soon.
The list of parameters can be found here: https://rda.ucar.edu/cgi-bin/transform?xml=/metadata/ParameterTables/WMO_GRIB1.98-0.128.xml&view=gribdoc
"""

from .daily import main as daily
from .monthly import main as monthly
from .DataAccess import VariablesInfo as VarInfo

__all__ = ['daily', 'monthly', 'VarInfo']

__version__ = '0.1'
