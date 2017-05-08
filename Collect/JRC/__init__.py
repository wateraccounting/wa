# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/JRC

Description:
This module downloads JRC water occurrence data from http://storage.googleapis.com/global-surface-water/downloads/. 
Use the JRC.Occurrence function to
download and create a water occurrence image in Gtiff format.
The data represents the period 1984-2015.

Examples:
from wa.Collect import JRC
JRC.Occurrence(Dir='C:/Temp3/', latlim=[41, 45], lonlim=[-8, -5])
"""

from .Occurrence import main as Occurrence

__all__ = ['Occurrence']

__version__ = '0.1'
