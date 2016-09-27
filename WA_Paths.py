# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: -
"""

def Paths(Type=None):
    
    User_Path = {
    'GDAL'                 :   'C:\Program Files (x86)\GDAL',            #folder
    '7z.exe'               :   'C:\Program Files (x86)\GDAL\7z.exe',     #complete path to executable
    'curl.exe'             :   'C:\Program Files (x86)\GDAL\curl.exe'   #complete path to executable
    }
    
    Selected_Path = User_Path[Type]    
    
    return(Selected_Path)