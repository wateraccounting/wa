# -*- coding: utf-8 -*-
"""
Created on Thu Feb 02 10:16:37 2017

@author: tih
"""
import time
###################### user defined parameters ################################

# Define Basin
Basin = 'Kali-Sindh'                            #'Kali-Sindh' or 'Mara' or 'Tekezze-Atbara''VGTB'  

# Define Products
P_Product = 'CHIRPS'                  # 'TRMM' or 'CHIRPS' 
ET_Product = 'ETensV1_0'              # 'ETensV1_0' or 'MOD16'
LAI_Product = 'MOD15'                 # 'MOD15'
NDM_Product = 'MOD17'                 # 'MOD17' 

# Define resolutions
Startdate = '2008-01-01'
Enddate = '2008-12-31'
Simulation = 1                        # Simulation number

# Define additional input Sheet 5
Inflow_Text_Files = []

########################## Calculate Sheets ###################################

time_start = time.time()

#Sheet 1

#Sheet 2
time_start2 = time.time()
import wa.Generator.Sheet2.main as Sheet2
Sheet2.Calculate(Basin, P_Product, ET_Product, LAI_Product, NDM_Product, Startdate, Enddate, Simulation)
print 'Sheet 2 calculated in ', time.time() - time_start2, 'Seconds'
print 'Total calculation time is ', time.time() - time_start, 'Seconds'

#Sheet 3

#Sheet 4

#Sheet 5
time_start5 = time.time()
import wa.Generator.Sheet5.main as Sheet5
Sheet5.Calculate(Basin, P_Product, ET_Product, Inflow_Text_Files, Startdate, Enddate, Simulation)
print 'Sheet 5 calculated in ', time.time() - time_start5, 'Seconds'
print 'Total calculation time is ', time.time() - time_start, 'Seconds'
                                             
#Sheet 6
