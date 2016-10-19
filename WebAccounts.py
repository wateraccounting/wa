# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 09:27:36 2016

@author: tih
"""

def Accounts(Type=None):
    
    User_Pass = {
    'NASA'                 :   ['TimHessels','WAteam1!'], 
    'GLEAM'                 :   ['gleamuser','GLEAMdah#s2016'],
    'FTP_WA'                :	 ['THessels','painole_2016!']		
    }
    
    Selected_Path = User_Pass[Type]    
    
    return(Selected_Path)