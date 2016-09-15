# -*- coding: utf-8 -*-
"""
Authors: Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Sheets

Description:
This can be used to create the WA+ standard sheets (www.wateraccounting.org).

Examples:
from wa.Sheets import *
create_sheet1(basin='Incomati', period='2005-2010',
              data=r'C:\Sheets\csv\Sample_sheet1.csv',
              output=r'C:\Sheets\sheet_1.jpg')
from wa.Sheets import *
create_sheet2(basin='Nile Basin', period='2010',
              data=r'C:\Sheets\csv\Sample_sheet2.csv',
              output=r'C:\Sheets\sheet_2.jpg')
"""


from .sheet1 import create_sheet1
from .sheet2 import create_sheet2

__all__ = ['create_sheet1', 'create_sheet2']

__version__ = '0.1'
