# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/DEM


Description:
This module downloads DEM data from http://earlywarning.usgs.gov/hydrodata/.
Use the DEM functions to download and create DEM images in Gtiff format.

Examples:
from wa.Collect import DEM
DEM.HydroSHED(Dir='C:/TempDEM4/', latlim=[29, 32], lonlim=[-113, -109])
"""
from .HydroSHED import main as HydroSHED
from .HydroSHED_Dir import main as HydroSHED_Dir

__all__ = ['HydroSHED','HydroSHED_Dir']

__version__ = '0.1'
