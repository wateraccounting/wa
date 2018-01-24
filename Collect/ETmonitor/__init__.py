# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/ETmonitor

Restrictions:
The data and this python file may not be distributed to others without
permission of the WA+ team due data restriction of the ETmonitor developers.

Description:
This module downloads ETmonitor data from
ftp.wateraccounting.unesco-ihe.org. Use the ETmonitor.monthly function to
download and create monthly ETmonitor images in Gtiff format.
The data is available between 2008-01-01 till 2012-12-31.

Examples:
from wa.Collect import ETmonitor
ETmonitor.ET_monthly(Dir='C:/Temp/', Startdate='2008-12-01', Enddate='2011-01-20',
           latlim=[-10, 30], lonlim=[-20, -10])
"""

from .ET_monthly import main as ET_monthly
from .ETpot_monthly import main as ETpot_monthly
from .Ei_monthly import main as Ei_monthly
from .Es_monthly import main as Es_monthly
from .Ew_monthly import main as Ew_monthly
from .Tr_monthly import main as Tr_monthly

__all__ = ['ET_monthly', 'ETpot_monthly','Ei_monthly', 'Es_monthly','Ew_monthly', 'Tr_monthly']

__version__ = '0.1'
