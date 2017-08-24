# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/TWC

Description:
This module downloads the global gray water footprint data from
ftp.wateraccounting.unesco-ihe.org. Use the TWC.Gray_Water_Footprint function to
download the dataset.

Requirement:
The WA_FTP username and password must be filled in the WebAccounts.py.
Contact the Water Accounting Team to get access to our WA FTP server.

Developers:
This dataset is developed by the Twente Water Centre:
Mekonnen, Mesfin M., and Arjen Y. Hoekstra. 
"Global gray water footprint and water pollution levels related to anthropogenic nitrogen loads to fresh water." 
Environmental science & technology 49.21 (2015): 12860-12868.

Examples:
from wa.Collect import TWC
TWC.Gray_Water_Footprint(Dir='C:/Temp/', latlim=[-10, 30], lonlim=[-20, -10])
"""

from .Gray_Water_Footprint import main as Gray_Water_Footprint

__all__ = ['Gray_Water_Footprint']

__version__ = '0.1'
