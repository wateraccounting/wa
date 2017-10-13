# -*- coding: utf-8 -*-
"""
Created on Mon Oct 09 14:02:12 2017

@author: tih
"""
import os
import pandas as pd
import gdal
import datetime
import glob
import numpy as np
import matplotlib.pyplot as plt
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC

input_folder_indicators = r"G:\SEBAL_02_to_03_2017_VIIRS\Indicators"
os.chdir(input_folder_indicators)
Dates = glob.glob('*')

input_folder = r"G:\SEBAL_02_to_03_2017_VIIRS"
input_folder_HANTS_SEBAL = os.path.join(input_folder, "Daily_SEBAL")
input_folder_Landsat = os.path.join(input_folder, "Landsat")

epsg_to = int(32629)
Example_dataset = r"G:\SEBAL_02_to_03_2017_VIIRS\DEM_sentinel4.tif"
Mask_dataset = r"G:\SEBAL_02_to_03_2017_VIIRS\Areas_perimeters_DEMsize_more.tif"
Mask_dataset2 = r"G:\SEBAL_02_to_03_2017_VIIRS\Areas_perimeters_DEMsize_more2.tif"


# Create example file for 30m
dest_30, ulx, lry, lrx, uly, epsg_to = RC.reproject_dataset_epsg(Example_dataset, 30, epsg_to, method = 1)
Array_30=dest_30.GetRasterBand(1).ReadAsArray()
geo = dest_30.GetGeoTransform()
Example_dataset_30 = r"G:\SEBAL_02_to_03_2017_VIIRS\DEM_sentinel_no_relief_30m.tif"

DC.Save_as_tiff(Example_dataset_30, Array_30, geo, epsg_to)

dest_30_Mask = RC.reproject_dataset_example(Mask_dataset, Example_dataset_30)
Mask_30 = dest_30_Mask.GetRasterBand(1).ReadAsArray()
Mask_30[Mask_30>0]=1
dest_30_Mask2 = RC.reproject_dataset_example(Mask_dataset2, Example_dataset_30)
Mask_30_2 = dest_30_Mask2.GetRasterBand(1).ReadAsArray()
Mask_30_2[Mask_30_2>0]=1
        
# Create example file for 100m
dest_100, ulx, lry, lrx, uly, epsg_to = RC.reproject_dataset_epsg(Example_dataset, 100, epsg_to, method = 1)
Array_100=dest_100.GetRasterBand(1).ReadAsArray()
geo = dest_100.GetGeoTransform()
Example_dataset_100 = r"G:\SEBAL_02_to_03_2017_VIIRS\DEM_sentinel_no_relief_100m.tif"

DC.Save_as_tiff(Example_dataset_100, Array_100, geo, epsg_to)
dest_100_Mask = RC.reproject_dataset_example(Mask_dataset, Example_dataset_100)
Mask_100 = dest_100_Mask.GetRasterBand(1).ReadAsArray()
Mask_100[Mask_100>0]=1

dest_100_Mask2 = RC.reproject_dataset_example(Mask_dataset2, Example_dataset_100)
Mask_100_2 = dest_100_Mask2.GetRasterBand(1).ReadAsArray()
Mask_100_2[Mask_100_2>0]=1
        
# do 100m daily loop
i = 0
Total_RZ = np.zeros([len(Dates),7])
Total_T = np.zeros([len(Dates),7])
for date in Dates:
    
    year  = date.split('-')[0]
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])
    Day = "%d-%02d-%02d" %(int(year),int(month),int(day))
    DOY = datetime.datetime.strptime(Day,'%Y-%m-%d').timetuple().tm_yday
    input_folder_HANTS_day = os.path.join(input_folder_HANTS_SEBAL, "%d%02d%02d" %(int(year),int(month),int(day)))
    input_folder_RZ = os.path.join(input_folder_HANTS_day, "Output_soil_moisture", "PROBAV_VIIRS_Root_zone_moisture_100m_2017_%d.tif" %DOY)
    input_folder_thermal = os.path.join(input_folder_HANTS_day, "Output_temporary", "PROBAV_VIIRS_temp_corr_100m_2017_%d.tif" %DOY)
    input_folder_indicator = os.path.join(input_folder_HANTS_day, "Output_temporary", "PROBAV_VIIRS_temp_corr_100m_2017_%d.tif" %DOY)
    
    
    
    dest_RZ_100 = RC.reproject_dataset_example(input_folder_RZ, Example_dataset_100)
    dest_T_100 = RC.reproject_dataset_example(input_folder_thermal, Example_dataset_100)   
    Indicators = ['GVMI','LSWI','MSI','PSRI','SIMI','SWCI','VSDI']
    Array_RZ = dest_RZ_100.GetRasterBand(1).ReadAsArray()
    Array_T = dest_T_100.GetRasterBand(1).ReadAsArray()
    j = 0
    for Indicator in Indicators:
        input_folder_indicator = os.path.join(input_folder_indicators, date, '%s.tif' %Indicator)     
        dest_ind_100 = RC.reproject_dataset_example(input_folder_indicator, Example_dataset_100)       
        Array_ind = dest_ind_100.GetRasterBand(1).ReadAsArray()
        Array_ind_flatten = Array_ind.flatten()
        Array_RZ_flatten = Array_RZ.flatten()   
        Array_T_flatten = Array_T.flatten()           
        R_RZ = np.corrcoef(Array_ind_flatten,Array_RZ_flatten)
        R_T = np.corrcoef(Array_ind_flatten,Array_T_flatten)
        Total_RZ[i,j] = R_RZ[1,0]       
        Total_T[i,j] = R_T[1,0]
        
            

        t = np.linspace(1,int(np.shape(Array_ind_flatten)[0]),int(np.shape(Array_T_flatten)[0]))
      
        fig = plt.figure()
        plt.scatter(Array_ind_flatten,Array_T_flatten,s=0.5,c='r') 
        plt.xlabel("%s" %Indicator)
        plt.ylabel("Thermal")
        plt.title('%s' %R_T[1,0]) 
        
        #plt.show()
        fig.savefig('G:\SEBAL_02_to_03_2017_VIIRS\Pictures\VIIRS_Daily\%s_VS_T_%d.png' %(Indicator,DOY))
        plt.close()
    
    
        fig = plt.figure()
        plt.scatter(Array_ind_flatten,Array_RZ_flatten,s=0.5) 
        plt.xlabel("%s" %Indicator)
        plt.ylabel("RZ")
        plt.title('%s' %R_RZ[1,0])
    
        #plt.show()
        fig.savefig('G:\SEBAL_02_to_03_2017_VIIRS\Pictures\VIIRS_Daily\%s_VS_RZ_%d.png' %(Indicator,DOY))
        plt.close()
        
        j += 1
    i += 1
    
############################## pixel based #######################################################################    
Dates_dict = {'2017-02-01': 33, '2017-02-08': 33,'2017-02-18': 49,'2017-03-10': 65,'2017-03-20': 81,'2017-03-30': 97}   
    
# do 100m daily loop
i = 0
Total_RZ_LS = np.zeros([len(Dates),7])
Total_T_LS = np.zeros([len(Dates),7])
for date in Dates:
    if date == '2017-02-01' or date == '2017-02-08':
        Mask_use_30 = Mask_30_2        
    else:
        Mask_use_30 = Mask_30
        
    year  = date.split('-')[0]
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])
    Day = "%d-%02d-%02d" %(int(year),int(month),int(day))
    DOY = datetime.datetime.strptime(Day,'%Y-%m-%d').timetuple().tm_yday
    input_folder_LS_day = os.path.join(input_folder_Landsat, "LC82010382017%03dLGN00_n_out" %Dates_dict[date])
    input_folder_RZ = os.path.join(input_folder_LS_day, "Output_soil_moisture", "L8_L8_Root_zone_moisture_30m_2017_%d.tif" %Dates_dict[date])
    input_folder_thermal = os.path.join(input_folder_LS_day, "Output_vegetation", "L8_L8_surface_temp_sharpened_30m_2017_%d.tif" %Dates_dict[date])
    
    
    
    dest_RZ_30 = RC.reproject_dataset_example(input_folder_RZ, Example_dataset_30)
    dest_T_30 = RC.reproject_dataset_example(input_folder_thermal, Example_dataset_30)   
    Indicators = ['GVMI','LSWI','MSI','PSRI','SIMI','SWCI','VSDI']
    Array_RZ = dest_RZ_30.GetRasterBand(1).ReadAsArray()
    Array_T = dest_T_30.GetRasterBand(1).ReadAsArray()
    j = 0
    for Indicator in Indicators:
        input_folder_indicator = os.path.join(input_folder_indicators, date, '%s.tif' %Indicator)     
        dest_ind_30 = RC.reproject_dataset_example(input_folder_indicator, Example_dataset_30)       
        Array_ind = dest_ind_30.GetRasterBand(1).ReadAsArray() * Mask_use_30
        Array_ind_flatten = Array_ind.flatten()
        Array_RZ_flatten = Array_RZ.flatten()   
        Array_T_flatten = Array_T.flatten()
        
        '''
        Array_min = np.percentile(Array_ind_flatten,0)
        Array_max = np.percentile(Array_ind_flatten,100)

        Array_RZ_flatten = Array_RZ_flatten[np.logical_and(Array_ind_flatten > Array_min,Array_ind_flatten < Array_max)]
        Array_T_flatten = Array_T_flatten[np.logical_and(Array_ind_flatten > Array_min,Array_ind_flatten < Array_max)]
            
        Array_ind_flatten = Array_ind_flatten[np.logical_and(Array_ind_flatten > Array_min,Array_ind_flatten < Array_max)]
        '''
        
        Array_RZ_flatten = Array_RZ_flatten[np.logical_and(Array_ind_flatten !=1.0, Array_ind_flatten !=0.0)]
        Array_T_flatten = Array_T_flatten[np.logical_and(Array_ind_flatten !=1.0, Array_ind_flatten !=0.0)] 
        Array_ind_flatten = Array_ind_flatten[np.logical_and(Array_ind_flatten !=1.0, Array_ind_flatten !=0.0)]

        Array_RZ_flatten = Array_RZ_flatten[np.logical_or(Array_ind_flatten > 0.0001, Array_ind_flatten < -0.0001)]
        Array_T_flatten = Array_T_flatten[np.logical_or(Array_ind_flatten > 0.0001, Array_ind_flatten < -0.0001)]
        Array_ind_flatten = Array_ind_flatten[np.logical_or(Array_ind_flatten > 0.0001, Array_ind_flatten < -0.0001)]

        Array_RZ_flatten = Array_RZ_flatten[np.logical_or(Array_ind_flatten > 1.0001, Array_ind_flatten < 0.9999)]
        Array_T_flatten = Array_T_flatten[np.logical_or(Array_ind_flatten > 1.0001, Array_ind_flatten < 0.9999)]
        Array_ind_flatten = Array_ind_flatten[np.logical_or(Array_ind_flatten > 1.0001, Array_ind_flatten < 0.9999)]

        if Indicator == 'SIMI':
            Array_RZ_flatten = Array_RZ_flatten[Array_ind_flatten < 9000]
            Array_T_flatten = Array_T_flatten[Array_ind_flatten < 9000]
            Array_ind_flatten = Array_ind_flatten[Array_ind_flatten < 9000]
                
                  
        R_RZ = np.corrcoef(Array_ind_flatten,Array_RZ_flatten)
        R_T = np.corrcoef(Array_ind_flatten,Array_T_flatten)
        Total_RZ_LS[i,j] = R_RZ[1,0]       
        Total_T_LS[i,j] = R_T[1,0]
        
            

        t = np.linspace(1,int(np.shape(Array_ind_flatten)[0]),int(np.shape(Array_T_flatten)[0]))
      
        fig = plt.figure()
        plt.scatter(Array_ind_flatten,Array_T_flatten,s=0.5,c='r') 
        plt.xlabel("%s" %Indicator)
        plt.ylabel("Thermal")
        plt.title('%s' %R_T[1,0]) 
        
        #plt.show()
        fig.savefig('G:\SEBAL_02_to_03_2017_VIIRS\Pictures\Landsat\%s_VS_T_%d.png' %(Indicator,DOY))
        plt.close()
    
    
        fig = plt.figure()
        plt.scatter(Array_ind_flatten,Array_RZ_flatten,s=0.5) 
        plt.xlabel("%s" %Indicator)
        plt.ylabel("RZ")
        plt.title('%s' %R_RZ[1,0])
    
        #plt.show()
        fig.savefig('G:\SEBAL_02_to_03_2017_VIIRS\Pictures\Landsat\%s_VS_RZ_%d.png' %(Indicator,DOY))
        plt.close()
        
        j += 1
    i += 1    
    
    
######################################### polygon based ##############################################################    
Mask_30_2 = dest_30_Mask2.GetRasterBand(1).ReadAsArray()
Mask_30 = dest_30_Mask.GetRasterBand(1).ReadAsArray()

def func(x,a,b):
    """
    This function is used for finding relation between indicator and RZ/T
    
    """
    return(a*x+b)     

Dates_dict = {'2017-02-01': 33, '2017-02-08': 49,'2017-02-18': 49,'2017-03-10': 65,'2017-03-20': 81,'2017-03-30': 97}   
    
# do 100m daily loop
i = 0
Total_RZ_LS = np.zeros([len(Dates),7])
Total_T_LS = np.zeros([len(Dates),7])
Total_RZ_Regression = np.zeros([len(Dates),7])
Total_RZ_Bias = np.zeros([len(Dates),7])
Total_T_Regression = np.zeros([len(Dates),7])
Total_T_Bias = np.zeros([len(Dates),7])
for date in Dates:
    if date == '2017-02-01' or date == '2017-02-08':
        Mask_use_30 = Mask_30_2        
    else:
        Mask_use_30 = Mask_30
        
    year  = date.split('-')[0]
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])
    Day = "%d-%02d-%02d" %(int(year),int(month),int(day))
    DOY = datetime.datetime.strptime(Day,'%Y-%m-%d').timetuple().tm_yday
    input_folder_LS_day = os.path.join(input_folder_Landsat, "LC82010382017%03dLGN00_n_out" %Dates_dict[date])
    input_folder_RZ = os.path.join(input_folder_LS_day, "Output_soil_moisture", "L8_L8_Root_zone_moisture_30m_2017_%d.tif" %Dates_dict[date])
    input_folder_thermal = os.path.join(input_folder_LS_day, "Output_vegetation", "L8_L8_surface_temp_sharpened_30m_2017_%d.tif" %Dates_dict[date])
    
    
    
    dest_RZ_30 = RC.reproject_dataset_example(input_folder_RZ, Example_dataset_30)
    dest_T_30 = RC.reproject_dataset_example(input_folder_thermal, Example_dataset_30)   
    Indicators = ['GVMI','LSWI','MSI','PSRI','SIMI','SWCI','VSDI']

    j = 0
    for Indicator in Indicators:
        input_folder_indicator = os.path.join(input_folder_indicators, date, '%s.tif' %Indicator)     
        dest_ind_30 = RC.reproject_dataset_example(input_folder_indicator, Example_dataset_30)
        k=0
        Array_ind_flatten = np.zeros(len(np.unique(Mask_use_30)[1:]))
        Array_RZ_flatten = np.zeros(len(np.unique(Mask_use_30)[1:]))
        Array_T_flatten = np.zeros(len(np.unique(Mask_use_30)[1:]))        
        for field in np.unique(Mask_use_30)[1:]:
            Array_RZ = dest_RZ_30.GetRasterBand(1).ReadAsArray()
            Array_T = dest_T_30.GetRasterBand(1).ReadAsArray()
       
            Mask_use_30_poly = np.zeros(Mask_use_30.shape)
            Mask_use_30_poly[Mask_use_30==field] = 1
            Array_ind = dest_ind_30.GetRasterBand(1).ReadAsArray() * Mask_use_30_poly
            Array_ind[np.logical_and(Array_ind < 0.0001, Array_ind > -0.0001)] = 0                                                                                 
            Array_ind[np.logical_and(Array_ind < 1.0001, Array_ind > 0.9999)] = 0
            
            if Indicator == 'SIMI':
                Array_ind[Array_ind > 9000] = 0
                Array_T[Array_ind > 9000] = 0
                Array_RZ[Array_ind > 9000] = 0

            Array_ind[Array_ind==0] = np.nan
            Array_ind_mean = np.nanmean(Array_ind)         
            Array_RZ[np.isnan(Array_ind)] = np.nan         
            Array_T[np.isnan(Array_ind)] = np.nan                                      
            Array_T_mean = np.nanmean(Array_T)                                                   
            Array_RZ_mean = np.nanmean(Array_RZ)                                                    
            Array_ind_flatten[k] = Array_ind_mean
            Array_RZ_flatten[k] = Array_RZ_mean                             
            Array_T_flatten[k] = Array_T_mean
                           
            k += 1                                     

        Array_RZ_flatten=Array_RZ_flatten[~np.isnan(Array_ind_flatten)] 
        Array_T_flatten=Array_T_flatten[~np.isnan(Array_ind_flatten)] 
        Array_ind_flatten=Array_ind_flatten[~np.isnan(Array_ind_flatten)]          

        Array_ind_flatten=Array_ind_flatten[~np.isnan(Array_T_flatten)]   
        Array_RZ_flatten=Array_RZ_flatten[~np.isnan(Array_T_flatten)] 
        Array_T_flatten=Array_T_flatten[~np.isnan(Array_T_flatten)] 

        Array_ind_flatten=Array_ind_flatten[~np.isnan(Array_RZ_flatten)]   
        Array_T_flatten=Array_T_flatten[~np.isnan(Array_RZ_flatten)] 
        Array_RZ_flatten=Array_RZ_flatten[~np.isnan(Array_RZ_flatten)] 
            
        R_RZ = np.corrcoef(Array_ind_flatten,Array_RZ_flatten)
        R_T = np.corrcoef(Array_ind_flatten,Array_T_flatten)
        Total_RZ_LS[i,j] = R_RZ[1,0]       
        Total_T_LS[i,j] = R_T[1,0]
        
        from scipy.optimize import curve_fit        
        poptRZ, pcovRZ = curve_fit(func, Array_ind_flatten, Array_RZ_flatten)
        poptT, pcovT = curve_fit(func, Array_ind_flatten, Array_T_flatten)
        
        Total_RZ_Regression[i,j] = poptRZ[0]       
        Total_RZ_Bias[i,j] = poptRZ[1]  
        Total_T_Regression[i,j] = poptT[0] 
        Total_T_Bias[i,j] = poptT[1]        

        t = np.linspace(1,int(np.shape(Array_ind_flatten)[0]),int(np.shape(Array_T_flatten)[0]))
      
        fig = plt.figure()
        plt.scatter(Array_ind_flatten,Array_T_flatten,s=3,c='r') 
        def graph(formula, x_range, Reg, Bias):  
            x = np.array(x_range)  
            y = my_formula(x, Reg, Bias)  # <- note now we're calling the function 'formula' with x
            plt.plot(x, y, 'c', linewidth=0.5)  
        
        def my_formula(x, Reg, Bias):
            return x * Reg + Bias
        graph(my_formula, np.linspace(np.min(Array_ind_flatten), np.max(Array_ind_flatten)),poptT[0] , poptT[1])     
        
        plt.xlabel("%s" %Indicator)
        plt.ylabel("Thermal")
        g1 = float("{0:.4f}".format(poptT[0]))
        g2 = float("{0:.4f}".format(poptT[1]))
        plt.title('Equation = %s * x + %s' %(g1 , g2))
        g3 = float("{0:.2f}".format(R_T[1,0]))
        plt.suptitle('R =  %s' %g3) 
        
        #plt.show()
        fig.savefig('G:\SEBAL_02_to_03_2017_VIIRS\Pictures\Landsat_Poly_more\%s_VS_T_%d.png' %(Indicator,DOY))
        plt.close()
    
    
        fig = plt.figure()
        plt.scatter(Array_ind_flatten,Array_RZ_flatten,s=3) 

        def graph(formula, x_range, Reg, Bias):  
            x = np.array(x_range)  
            y = my_formula(x, Reg, Bias)  # <- note now we're calling the function 'formula' with x
            plt.plot(x, y, 'r', linewidth=0.5)   
        
        def my_formula(x, Reg, Bias):
            return x*Reg + Bias
        graph(my_formula, np.linspace(np.min(Array_ind_flatten), np.max(Array_ind_flatten)),poptRZ[0] , poptRZ[1])     
        
        
        plt.xlabel("%s" %Indicator)
        plt.ylabel("RZ")
        g1 = float("{0:.4f}".format(poptRZ[0]))
        g2 = float("{0:.4f}".format(poptRZ[1]))
        plt.title('Equation = %s * x + %s' %(g1 , g2))
        g3 = float("{0:.2f}".format(R_RZ[1,0]))
        plt.suptitle('R = %s' %g3)         

        #plt.show()
        fig.savefig('G:\SEBAL_02_to_03_2017_VIIRS\Pictures\Landsat_Poly_more\%s_VS_RZ_%d.png' %(Indicator,DOY))
        plt.close()
        
        j += 1
    i += 1        
    

input_folder_indicator = os.path.join(input_folder_indicators, date, '%s.tif' %Indicator)     
dest_ind_30 = RC.reproject_dataset_example(input_folder_indicator, Example_dataset_30)       
Array_ind = dest_ind_30.GetRasterBand(1).ReadAsArray()

input_folder_LS_day = os.path.join(input_folder_Landsat, "LC82010382017%03dLGN00_n_out" %Dates_dict[date])
input_folder_thermal = os.path.join(input_folder_LS_day, "Output_vegetation", "L8_L8_surface_temp_sharpened_30m_2017_%d.tif" %Dates_dict[date])
dest_T_30 = RC.reproject_dataset_example(input_folder_thermal, Example_dataset_30)       
Array_T = dest_T_30.GetRasterBand(1).ReadAsArray()


Array_ind_flatten = Array_ind.flatten()
Array_T_flatten = Array_T.flatten()

Array_T_flatten = Array_T_flatten[Array_ind_flatten!=-4.0000241e-06]
Array_ind_flatten = Array_ind_flatten[Array_ind_flatten!=-4.0000241e-06]

Array_ind_flatten = Array_ind_flatten[~np.isnan(Array_T_flatten)]
Array_T_flatten = Array_T_flatten[~np.isnan(Array_T_flatten)]

import matplotlib.pyplot as plt 
plt.figure(1)
plt.hist(Array_ind_flatten, bins='auto')
plt.xlim(xmin=np.percentile(Array_ind_flatten,1)-0.05, xmax =np.percentile(Array_ind_flatten,99)+0.05)

plt.figure(2)
plt.hist(Array_T_flatten, bins='auto')
plt.xlim(xmin=np.percentile(Array_T_flatten,1)-0.05, xmax =np.percentile(Array_T_flatten,99)+0.05)


x1 = np.percentile(Array_ind_flatten,30)
x2 = np.percentile(Array_ind_flatten,80)
y1 = np.percentile(Array_T_flatten,40)
y2 = np.percentile(Array_T_flatten,90)

coeff = - (y2-y1)/(x2-x1)
IND = np.zeros(10000)
THER = np.zeros(10000)
for i in range(0,10000):
    IND[i] = np.percentile(Array_ind_flatten,i/100)   
    THER[i] = np.percentile(Array_T_flatten,i/100)   
THER = np.flipud(THER)
Array_T_new = np.zeros(Array_T.shape)
 
def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]                   
                   
   
for y in range(0, Array_T.shape[0]):
    for x in range(0, Array_T.shape[1]):
        
        value = Array_ind[y, x]
        index = find_nearest(IND,value)
        index_number = np.argwhere((IND==index))[0,0]   
        Array_T_new[y, x] = THER[index_number]
        
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC                   
geo_out, proj, size_X, size_Y = RC.Open_array_info(Example_dataset_30)                   
Filename_out = r"G:\SEBAL_02_to_03_2017_VIIRS\Simulated_pictures\simulated_test.tif"

DC.Save_as_tiff(Filename_out, Array_T_new, geo_out, proj)











################################ apply historgram on whole image ##########################

input_folder_indicators = r"G:\SEBAL_02_to_03_2017_VIIRS\Indicators"
os.chdir(input_folder_indicators)
Dates = glob.glob('*')

input_folder = r"G:\SEBAL_02_to_03_2017_VIIRS"
input_folder_HANTS_SEBAL = os.path.join(input_folder, "Daily_SEBAL")
input_folder_Landsat = os.path.join(input_folder, "Landsat")

epsg_to = int(32629)
Example_dataset = r"G:\SEBAL_02_to_03_2017_VIIRS\DEM_IRR_indicator.tif"

# Create example file for 30m
dest_30, ulx, lry, lrx, uly, epsg_to = RC.reproject_dataset_epsg(Example_dataset, 30, epsg_to, method = 1)
Array_30=dest_30.GetRasterBand(1).ReadAsArray()
geo = dest_30.GetGeoTransform()
Example_dataset_30 = r"G:\SEBAL_02_to_03_2017_VIIRS\DEM_sentinel_no_relief_30m_whole_indicator.tif"

DC.Save_as_tiff(Example_dataset_30, Array_30, geo, epsg_to)
geo_out, proj, size_X, size_Y = RC.Open_array_info(Example_dataset_30)
Indicator = "GVMI"
date = Dates[2]
year  = date.split('-')[0]
month = int(date.split('-')[1])
day = int(date.split('-')[2])
DateName = "%s%02d%02d" %(year,month,day)

# reproject Indicator to DEM size
input_folder_indicator = os.path.join(input_folder_indicators, date, '%s.tif' %Indicator)     
dest_ind_whole = RC.reproject_dataset_example(input_folder_indicator, Example_dataset_30)
Indicator_whole = dest_ind_whole.GetRasterBand(1).ReadAsArray()

# reproject T to DEM size
input_folder_thermal = os.path.join(input_folder_LS_day, "Output_vegetation", "L8_L8_surface_temp_sharpened_30m_2017_%d.tif" %Dates_dict[date])
dest_ind_whole = RC.reproject_dataset_example(input_folder_thermal, Example_dataset_30)
T_whole = dest_ind_whole.GetRasterBand(1).ReadAsArray()

# Create flat array
Array_ind_flatten = Indicator_whole.flatten()
Array_T_flatten = T_whole.flatten()

Array_T_flatten = Array_T_flatten[Array_ind_flatten!=-4.0000241e-06]
Array_ind_flatten = Array_ind_flatten[Array_ind_flatten!=-4.0000241e-06]

Array_ind_flatten = Array_ind_flatten[~np.isnan(Array_T_flatten)]
Array_T_flatten = Array_T_flatten[~np.isnan(Array_T_flatten)]

'''
import matplotlib.pyplot as plt 
plt.figure(1)
plt.hist(Array_ind_flatten, bins='auto')
plt.xlim(xmin=np.percentile(Array_ind_flatten,1)-0.05, xmax =np.percentile(Array_ind_flatten,99)+0.05)

plt.figure(2)
plt.hist(Array_T_flatten, bins='auto')
plt.xlim(xmin=np.percentile(Array_T_flatten,1)-0.05, xmax =np.percentile(Array_T_flatten,99)+0.05)
'''

IND = np.zeros(10000)
THER = np.zeros(10000)
for i in range(0,10000):
    IND[i] = np.percentile(Array_ind_flatten,i/100)   
    THER[i] = np.percentile(Array_T_flatten,i/100)   
THER = np.flipud(THER)
Array_T_new = np.zeros(T_whole.shape)

# Iterate over every pixel to get new simulated value
for y in range(0, Indicator_whole.shape[0]):
    print(y)
    for x in range(0, Indicator_whole.shape[1]):
        
        value = Indicator_whole[y, x]
        index = find_nearest(IND,value)
        index_number = np.argwhere((IND==index))[0,0]   
        Array_T_new[y, x] = THER[index_number]

Filename_out = r"G:\SEBAL_02_to_03_2017_VIIRS\Simulated_pictures\simulated_test_whole_image%s.tif" %DateName
geo_out, proj, size_X, size_Y = RC.Open_array_info(Example_dataset_30)                   

DC.Save_as_tiff(Filename_out, Array_T_new, geo_out, proj)
                   
                   
                   


    