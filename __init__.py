# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         IHE Delft 2017
Contact: t.hessels@un-ihe.org
         g.espinoza@un-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: wa


Description:
This module contains a compilation of scripts and functions used to download
hydrologic, atmospheric, and remote sensing data from different sources.
This data is used within a water accounting framework.
(http://www.wateraccounting.org/)
"""


from wa import Collect_Tools, WebAccounts, General, Functions, Collect, Products, Sheets, Generator

__all__ = ['Collect_Tools', 'WebAccounts', 'General', 'Collect', 'Functions', 'Products', 'Sheets', 'Generator']

__version__ = '0.1'
