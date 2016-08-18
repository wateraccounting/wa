# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 09:27:36 2016

@author: tih
"""

def Accounts(Type=None):
    
    User_Pass = {
    'GLDAS'                 :   ['',''], 
    'GLEAM'                 :   ['',''],
    'FTP_WA'                :	['','']		
    }
    
    Selected_Path = User_Pass[Type]    
    
    return(Selected_Path)