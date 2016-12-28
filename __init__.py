# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: wa


Description:
This module contains a compilation of scripts and functions used to download
hydrologic, atmospheric, and remote sensing data from different sources.
This data is used within a water accounting framework.
(http://www.wateraccounting.org/)
"""


from wa import WA_Paths, WebAccounts, General, Collect, Products, Sheets

__all__ = ['WA_Paths', 'WebAccounts', 'General', 'Collect', 'Products', 'Sheets']

__version__ = '0.1'
