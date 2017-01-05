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
    'Home'                 :   r'',   #directory to the wa folder
    'GDAL'                 :   r'',   #folder
    '7z.exe'               :   r'',   #complete path to executable
    'curl.exe'             :   r''    #complete path to executable
    }
    
    Selected_Path = User_Path[Type]    
    
    return(Selected_Path)