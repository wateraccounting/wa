# -*- coding: utf-8 -*-
"""
Created on Wed May 03 13:33:58 2017

@author: tih
"""
def Calc_Regions(Name_NC_Basin_CR, input_JRC, sensitivity, Boundaries):

    import numpy as np

    import wa.General.raster_conversions as RC

    # Get JRC array and information
    Array = RC.Open_tiff_array(input_JRC)
    Geo_out, proj, size_X, size_Y = RC.Open_array_info(input_JRC)

    # Get Basin boundary based on LU
    Array_LU = RC.Open_nc_array(Name_NC_Basin_CR)
    LU_array=RC.resize_array_example(Array_LU,Array)
    basin_array = np.zeros(np.shape(LU_array))
    basin_array[LU_array>0] = 1
    del LU_array

    # find all pixels with water occurence
    Array[basin_array<1]=0
    Array[Array<30] = 0     
    Array[Array>=30] = 1    
    del basin_array

    # sum larger areas to find lakes
    x_size=np.round(int(np.shape(Array)[0])/30)
    y_size=np.round(int(np.shape(Array)[1])/30)
    sum_array = np.zeros([x_size, y_size])

    for i in range(0,len(sum_array)):
        for j in range(0,len(sum_array[1])):
            sum_array[i,j]=np.sum(Array[i*30:(i+1)*30,j*30:(j+1)*30])

    del Array
        
    lakes = np.argwhere(sum_array>=sensitivity)
    lake_info = np.zeros([1,4])

    i = 0 
    k = 1

    # find all neighboring pixels
    for lake in lakes:
        added = 0
        for j in range(0,k):
            if (lake[0] >= lake_info[j,0] and lake[0] <= lake_info[j,1] and lake[1] >= lake_info[j,2] and lake[1] <= lake_info[j,3]):
                lake_info[j,0]=np.maximum(np.minimum(lake_info[j,0],lake[0]-8),0)
                lake_info[j,1]=np.minimum(np.maximum(lake_info[j,1],lake[0]+8),x_size)            
                lake_info[j,2]=np.maximum(np.minimum(lake_info[j,2],lake[1]-8),0)
                lake_info[j,3]=np.minimum(np.maximum(lake_info[j,3],lake[1]+8),y_size)
                added = 1
            
        if added == 0:
            lake_info_one = np.zeros([4])
            lake_info_one[0] = np.maximum(0, lake[0]-8)
            lake_info_one[1] = np.minimum(x_size, lake[0]+8)
            lake_info_one[2] = np.maximum(0, lake[1]-8)
            lake_info_one[3] = np.minimum(y_size, lake[1]+8)
            lake_info = np.append(lake_info,lake_info_one)
            lake_info = np.resize(lake_info, (k+1,4))
            k += 1

        
    # merge all overlaping regions
    p = 0 
    lake_info_end = np.zeros([1,4])
       
    for i in range(1,k):
        added = 0
        lake_info_one = lake_info[i,:]     
        lake_y_region = range(int(lake_info_one[0]),int(lake_info_one[1]+1))
        lake_x_region = range(int(lake_info_one[2]),int(lake_info_one[3]+1))

        for j in range(0,p+1):
            if len(lake_y_region)+len(range(int(lake_info_end[j,0]),int(lake_info_end[j,1]+1))) is not len(np.unique(np.append(lake_y_region,range(int(lake_info_end[j,0]),int(lake_info_end[j,1]+1))))) and len(lake_x_region)+len(range(int(lake_info_end[j,2]),int(lake_info_end[j,3]+1))) is not len(np.unique(np.append(lake_x_region,range(int(lake_info_end[j,2]),int(lake_info_end[j,3]+1))))):
                lake_info_end[j,0] = np.min(np.unique(np.append(lake_y_region,range(int(lake_info_end[j,0]),int(lake_info_end[j,1]+1)))))
                lake_info_end[j,1] = np.max(np.unique(np.append(lake_y_region,range(int(lake_info_end[j,0]),int(lake_info_end[j,1]+1)))))            
                lake_info_end[j,2] = np.min(np.unique(np.append(lake_x_region,range(int(lake_info_end[j,2]),int(lake_info_end[j,3]+1)))))
                lake_info_end[j,3] = np.max(np.unique(np.append(lake_x_region,range(int(lake_info_end[j,2]),int(lake_info_end[j,3]+1)))))            
                added = 1

        if added == 0:
            lake_info_one = lake_info[i,:] 
            lake_info_end = np.append(lake_info_end,lake_info_one)
            lake_info_end = np.resize(lake_info_end, (p+2,4))
        
            p += 1
        
    # calculate the area   
    Regions = np.zeros([p,4])
    pixel_x_size = Geo_out[1]*30    
    pixel_y_size = Geo_out[5]*30
    for region in range(1,p+1):
        Regions[region-1,0] = Geo_out[0] + pixel_x_size * lake_info_end[region,2]                     
        Regions[region-1,1] = Geo_out[0] + pixel_x_size * (lake_info_end[region,3] + 1)   
        Regions[region-1,2] = Geo_out[3] + pixel_y_size * (lake_info_end[region,1] + 1)        
        Regions[region-1,3] = Geo_out[3] + pixel_y_size * lake_info_end[region,0]    
                     
    return(Regions)  



def Find_Area_Volume_Relation(region, input_JRC, DEM_dataset):
  
    # Find relation between V and A    
    
    import numpy as np
    import wa.General.raster_conversions as RC
    import wa.General.data_conversions as DC
    from scipy.optimize import curve_fit
    import matplotlib.pyplot as plt
    
    def func(x,a,b):
        """
        This function is used for finding relation area and volume
        
        """
        return(a*x**b)  
   
        
    def func3(x,a,b,c,d):
        """
        This function is used for finding relation area and volume
        
        """
        return(a*(x-c)**b+d)  

    #Array, Geo_out = RC.clip_data(input_JRC,latlim=[14.528,14.985],lonlim =[35.810,36.005])
    Array, Geo_out = RC.clip_data(input_JRC,latlim=[region[2],region[3]],lonlim =[region[0],region[1]])   # This reservoir was not filled when SRTM was taken  
    size_Y = int(np.shape([Array])[-2])
    size_X = int(np.shape([Array])[-1])
    
    Water_array = np.zeros(np.shape(Array))
    buffer_zone = 4
    Array[Array > 0] = 1
    for i in range(0,size_Y):
        for j in range(0,size_X):
            Water_array[i,j]=np.max(Array[np.maximum(0,i-buffer_zone):np.minimum(size_Y,i+buffer_zone+1),np.maximum(0,j-buffer_zone):np.minimum(size_X,j+buffer_zone+1)])
    del Array
    
    # Open DEM and reproject   
    
    # Save Example as memory file
    dest_example = DC.Save_as_MEM(Water_array, Geo_out, projection='WGS84')   

    # reproject DEM by using example
    dest_out=RC.reproject_dataset_example(DEM_dataset, dest_example, method=2)
    DEM=dest_out.GetRasterBand(1).ReadAsArray()
        
    # find DEM water heights
    DEM_water = np.zeros(np.shape(Water_array))
    DEM_water[Water_array != 1] = np.nan   
    DEM_water[Water_array == 1.] = DEM[Water_array == 1.] 
        
    # Get array with areas
    import wa.Functions.Start.Area_converter as Area
    dlat, dlon = Area.Calc_dlat_dlon(Geo_out, size_X, size_Y)
    area_in_m2 =  dlat * dlon
        
    # find volume and Area
    min_DEM_water = int(np.round(np.nanmin(DEM_water)))    
    max_DEM_water = int(np.round(np.nanmax(DEM_water)))      
     
    Reservoir_characteristics = np.zeros([1,5])
    i = 0   
    
    for height in range(min_DEM_water+1, max_DEM_water):
        DEM_water_below_height = np.zeros(np.shape(DEM_water))
        DEM_water[np.isnan(DEM_water)] = 1000000
        DEM_water_below_height[DEM_water < height] = 1                   
        pixels = np.sum(DEM_water_below_height)
       
        area = np.sum(DEM_water_below_height * area_in_m2)
        if height == min_DEM_water + 1:
            volume = 0.5 * area
            histogram = pixels 
            Reservoir_characteristics[:] = [height, pixels, area, volume, histogram]
        else:
            area_previous = Reservoir_characteristics[i, 2]
            volume_previous = Reservoir_characteristics[i, 3]
            volume = volume_previous + 0.5 * (area - area_previous) + 1 * area_previous
            histogram_previous = Reservoir_characteristics[i, 1]                                 
            histogram = pixels - histogram_previous 
            Reservoir_characteristics_one = [height, pixels, area, volume, histogram]
            Reservoir_characteristics = np.append(Reservoir_characteristics,Reservoir_characteristics_one)
            i += 1
            Reservoir_characteristics = np.resize(Reservoir_characteristics, (i+1,5))
       
    maxi = int(len(Reservoir_characteristics[:,3]))

    # find minimum value for reservoirs height (DEM is same value if reservoir was already filled whe SRTM was created)
    Historgram = Reservoir_characteristics[:,4]
    hist_mean = np.mean(Historgram)
    hist_std = np.std(Historgram)
    
    mini_tresh = hist_std * 5 + hist_mean
    
    Check_hist = np.zeros([len(Historgram)])
    Check_hist[Historgram>mini_tresh] = Historgram[Historgram>mini_tresh] 
    if np.max(Check_hist) != 0.0:
        col = np.argwhere(Historgram == np.max(Check_hist))[0][0]
        mini = col + 1
    else:
        mini = 0
    
    fitted = 0
    
    # find starting point reservoirs
    V0 = Reservoir_characteristics[mini,3]
    A0 = Reservoir_characteristics[mini,2]


    # Calculate the best maxi reservoir characteristics, based on the normal V = a*x**b relation
    while fitted == 0:
        try:
            if mini == 0:
                popt1, pcov1 = curve_fit(func, Reservoir_characteristics[mini:maxi,2], Reservoir_characteristics[mini:maxi,3])
            else:
                popt1, pcov1 = curve_fit(func, Reservoir_characteristics[mini:maxi,2] - A0, Reservoir_characteristics[mini:maxi,3]-V0)   
            fitted = 1
        except:
            maxi -= 1
        
        if maxi < mini:
            print 'ERROR: was not able to find optimal fit'
            fitted = 1
        

    # Remove last couple of pixels of maxi
    maxi_end = int(np.round(maxi - 0.2 * (maxi - mini)))   

    done = 0
    times = 0
    
    while done == 0 or times > 20 or maxi_end < mini:
        try:
            if mini == 0:
                popt, pcov = curve_fit(func, Reservoir_characteristics[mini:maxi_end,2], Reservoir_characteristics[mini:maxi_end,3])  
            else:
                popt, pcov = curve_fit(func3, Reservoir_characteristics[mini:maxi_end,2], Reservoir_characteristics[mini:maxi_end,3]) 
        
        except:
            maxi_end = int(maxi) 
            if mini == 0:
                popt, pcov = curve_fit(func, Reservoir_characteristics[mini:maxi_end,2], Reservoir_characteristics[mini:maxi_end,3])     
            else:
                popt, pcov = curve_fit(func3, Reservoir_characteristics[mini:maxi_end,2], Reservoir_characteristics[mini:maxi_end,3]) 
    

        if mini == 0:
            plt.plot(Reservoir_characteristics[mini:maxi_end,2], Reservoir_characteristics[mini:maxi_end,3], 'ro')
            t = np.arange(0., np.max(Reservoir_characteristics[:,2]), 1000)
            plt.plot(t, popt[0]*(t)**popt[1], 'g--')   
            plt.axis([0, np.max(Reservoir_characteristics[mini:maxi_end,2]), 0, np.max(Reservoir_characteristics[mini:maxi_end,3])]) 
            plt.show()   
            done = 1
    
        else:
            plt.plot(Reservoir_characteristics[mini:maxi_end,2], Reservoir_characteristics[mini:maxi_end,3], 'ro')
            t = np.arange(0., np.max(Reservoir_characteristics[:,2]), 1000)
            plt.plot(t, popt[0]*(t-popt[2])**popt[1] + popt[3], 'g--')   
            plt.axis([0, np.max(Reservoir_characteristics[mini:maxi_end,2]), 0, np.max(Reservoir_characteristics[mini:maxi_end,3])]) 
            plt.show()   
            Volume_error = popt[3]/V0 * 100 - 100
            print 'error Volume = %s percent' %Volume_error
            print 'error Area = %s percent' %(A0/popt[2] * 100 - 100)
    
            if Volume_error < 30 and Volume_error > -30:
                done = 1
            else:
                times += 1
                maxi_end -= 1
                print 'Another run is done in order to improve the result'
                
    if done == 0:
        popt = np.append(popt1, [A0, V0])
    
    if len(popt) == 2:
        popt = np.append(popt, [0, 0])
    
    return(popt)

def GEE_calc_reservoir_area(region, Startdate, Enddate):

    import ee
    ee.Initialize()

    import calendar
    import pandas as pd

    # Needed input
    region = ee.Geometry(ee.Geometry.Rectangle(region[0],region[2],region[1],region[3]))

    # Functions that will be used by the GEE
    def reduceregion_sum(image):
        '''
        This function will calculate the amount of pixels (30by30m) that are defined as water for the whole ImageCollection
        '''
        Water = ee.Image(image.gt(1))
        areas = Water.reduceRegion(reducer=ee.Reducer.sum(),geometry= region, scale=30)
        mean_feature = ee.Feature(None, {'month': image.get('month'), 'year': image.get('year'), 'water': areas.get('water')})
        return mean_feature  

    def accumulate(image, list):
        '''
        This function will remove the data gaps in the JRC data by filling the gaps with the previous map
        '''
        mymask = image.gt(0)
        image = image.mask(mymask)
        previous = ee.Image(ee.List(list).get(-1))
        myimage = image.unmask(previous)
        result = myimage.set('system:time_start', image.get('system:time_start'))
        cumulative = ee.List(list).add(result)
        return cumulative

    # Open dataset
    JRC = ee.ImageCollection("JRC/GSW1_0/MonthlyHistory")

    # Create timestamps
    Start = pd.Timestamp(Startdate)
    End = pd.Timestamp(Enddate)
    startyear = Start.year
    endyear = End.year
    startmonth = Start.month
    endmonth = End.month

    # Get also the area of one month before startdate
    endmonth = endmonth + 1
    if endmonth == 13:
        endyear += 1
        endmonth = 1


    # set startdate
    startdate = ee.Date.fromYMD(startyear,startmonth,1)
    enddate = ee.Date.fromYMD(endyear,endmonth,calendar.monthrange(endyear,endmonth)[1])

    # Select the JRC that will be used
    JRC_timeFiltered = JRC.filterDate(startdate, enddate).filterBounds(region).sort('system:time_start', True)

    # first JRC map
    time0 = JRC.first().get('system:time_start')
    first = ee.List([ee.Image(0).set('system:time_start', time0).select([0], ['water'])]);

    # Fill in the gaps in the JRC data
    JRC_timeFiltered_GapFilled = ee.ImageCollection(ee.List(JRC_timeFiltered.iterate(accumulate, first)))

    # Calculate the pixel that are defined as water
    JRC_timeFiltered_GapFilled_PixelCounted = JRC_timeFiltered_GapFilled.map(reduceregion_sum).getInfo()

    # Read out the features
    all_values = list()
    for idx in JRC_timeFiltered_GapFilled_PixelCounted['features'][1:]:
        month_val = idx['properties']['month'] 
        year_val = idx['properties']['year'] 
        water_val = idx['properties']['water']    
        all_values.append([month_val, year_val, water_val])
    
    return(all_values)  
   
def Calc_Diff_Storage(Area_Reservoir_Values, popt):
    
    import numpy as np

    # Get the water area over time  
    Water_area_m2 = np.zeros([len(Area_Reservoir_Values),3])
    for i in range(0,len(Area_Reservoir_Values)):
        Water_area_m2[i,0] = Area_Reservoir_Values[i][0]   
        Water_area_m2[i,1] = Area_Reservoir_Values[i][1]
        Water_area_m2[i,2] = Area_Reservoir_Values[i][2]*30*30
 
    Check_water_area = Water_area_m2[1:,2] -  Water_area_m2[:-1,2]
    for i in range(0,len(Check_water_area)):
        if Check_water_area[i] == 0.0:
            p=i
            found_iter = 0
            for j in range(i, len(Check_water_area)):
                if Check_water_area[p] == 0.0:
                    p += 1
                else:
                    found_iter = 1
            if found_iter == 0:

                if len(Check_water_area) >= 12:
                    k = p-12
                    if Check_water_area[k] == 0:
                        p = i
 
                   
            Water_area_m2[i,2] = (Water_area_m2[p,2] + Water_area_m2[i-1,2])/(2) 
    
 
    # Get the Q-A relation   
    Water_volume_m3 = popt[0] * (Water_area_m2[:,2]) ** popt[1] 
    
    Diff_Water_Volume = np.zeros([len(Area_Reservoir_Values)-1,3])
    
    Diff_Water_Volume[:,:2] = Water_area_m2[1:,:2]
    
    Diff_Water_Volume[:,2] = - Water_volume_m3[:-1] + Water_volume_m3[1:]

    return(Diff_Water_Volume)
         

def Add_Reservoirs(Name_NC_Rivers ,Name_NC_Acc_Pixels, Diff_Water_Volume, River_dict, Discharge_dict,  Regions, Example_dataset):
 
    import numpy as np
    
    import wa.General.raster_conversions as RC
    import wa.General.data_conversions as DC
    
    # Extract Rivers data from NetCDF file
    Rivers = RC.Open_nc_array(Name_NC_Rivers)

    # Open data array info based on example data
    geo_out, epsg, size_X, size_Y = RC.Open_array_info(Example_dataset)

    # Extract flow direction data from NetCDF file
    acc_pixels = RC.Open_nc_array(Name_NC_Acc_Pixels)

    # Create ID Matrix
    y,x = np.indices((size_Y, size_X))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y,size_X),mode='clip').reshape(x.shape))+1
    del  x, y
    
    Acc_Pixels_Rivers = Rivers * acc_pixels
    ID_Rivers = Rivers * ID_Matrix
        
    Amount_of_Reservoirs = len(Regions)  
 
    Reservoir_is_in_River = np.ones([len(Regions),3]) * -9999
    
    for reservoir in range(0,Amount_of_Reservoirs):
        
        region = Regions[reservoir,:]

        dest = DC.Save_as_MEM(Acc_Pixels_Rivers, geo_out, projection='WGS84')   
        Rivers_Acc_Pixels_reservoir, Geo_out = RC.clip_data(dest,latlim=[region[2],region[3]],lonlim =[region[0],region[1]])  

        dest = DC.Save_as_MEM(ID_Rivers, geo_out, projection='WGS84')   
        Rivers_ID_reservoir, Geo_out = RC.clip_data(dest,latlim=[region[2],region[3]],lonlim =[region[0],region[1]])  


        size_Y_reservoir, size_X_reservoir = np.shape(Rivers_Acc_Pixels_reservoir)
        IDs_Edges = []
        IDs_Edges = np.append(IDs_Edges,Rivers_Acc_Pixels_reservoir[0,:])
        IDs_Edges = np.append(IDs_Edges,Rivers_Acc_Pixels_reservoir[:,0])
        IDs_Edges = np.append(IDs_Edges,Rivers_Acc_Pixels_reservoir[int(size_Y_reservoir)-1,:])
        IDs_Edges = np.append(IDs_Edges,Rivers_Acc_Pixels_reservoir[:,int(size_X_reservoir)-1])
        Value_Reservoir = np.max(np.unique(IDs_Edges))

        y_pix_res,x_pix_res = np.argwhere(Rivers_Acc_Pixels_reservoir==Value_Reservoir)[0]
        ID_reservoir = Rivers_ID_reservoir[y_pix_res,x_pix_res]



        # Find exact reservoir area in river directory
        for River_part in River_dict.iteritems():
            if len(np.argwhere(River_part[1] == ID_reservoir)) > 0:
                 Reservoir_is_in_River[reservoir, 0] = np.argwhere(River_part[1] == ID_reservoir) #River_part_good
                 Reservoir_is_in_River[reservoir, 1] = River_part[0]  #River_Add_Reservoir
                 Reservoir_is_in_River[reservoir, 2] = 1           #Reservoir_is_in_River
 
    
    numbers = abs(Reservoir_is_in_River[:,1].argsort() - len(Reservoir_is_in_River)+1)
        
        
    for number in range(0,len(Reservoir_is_in_River)):
    
        row_reservoir = np.argwhere(numbers==number)[0][0]
        
        if not Reservoir_is_in_River[row_reservoir,2] == -9999:
     
            # Get discharge into the reservoir:
            Flow_in_res_m3 = Discharge_dict[int(Reservoir_is_in_River[row_reservoir,1])][:,int(Reservoir_is_in_River[row_reservoir,0])]

            # Get difference reservoir
            Change_Reservoir_m3 = Diff_Water_Volume[row_reservoir,:,2]

            # Total Change outflow
            Change_outflow_m3 = np.minimum(Flow_in_res_m3, Change_Reservoir_m3)
        
            Difference = Change_outflow_m3 - Change_Reservoir_m3
            if abs(np.sum(Difference))>10000 and np.sum(Change_Reservoir_m3[Change_outflow_m3>0])>0:
                Change_outflow_m3[Change_outflow_m3<0] = Change_outflow_m3[Change_outflow_m3<0]*np.sum(Change_outflow_m3[Change_outflow_m3>0])/np.sum(Change_Reservoir_m3[Change_outflow_m3>0]) 

            # Find key name (which is also the lenght of the river dictionary)
            i = len(River_dict)

            #River_with_reservoirs_dict[i]=list((River_dict[River_Add_Reservoir][River_part_good[0][0]:]).flat) < MAAK DIRECTORIES ARRAYS OP DEZE MANIER DAN IS DE ARRAY 1D
            River_dict[i]=River_dict[int(Reservoir_is_in_River[row_reservoir,1])][int(Reservoir_is_in_River[row_reservoir,0]):]
            River_dict[int(Reservoir_is_in_River[row_reservoir,1])] = River_dict[int(Reservoir_is_in_River[row_reservoir,1])][:int(Reservoir_is_in_River[row_reservoir,0])+1]

            Discharge_dict[i]=Discharge_dict[int(Reservoir_is_in_River[row_reservoir,1])][:,int(Reservoir_is_in_River[row_reservoir,0]):]
            Discharge_dict[int(Reservoir_is_in_River[row_reservoir,1])] = Discharge_dict[int(Reservoir_is_in_River[row_reservoir,1])][:,:int(Reservoir_is_in_River[row_reservoir,0])+1] - Change_outflow_m3[:,None]
            Next_ID = River_dict[int(Reservoir_is_in_River[row_reservoir,1])][0]
              
            while int(Next_ID) != int(River_dict[0][0]):
                for River_part in River_dict.iteritems():
                    if River_part[-1][-1] == Next_ID:
                        Next_ID = River_part[-1][0] 
                        item = River_part[0]
                        Discharge_dict[item][:] = Discharge_dict[item][:,:] - Change_outflow_m3[:,None]
                        print(item)
  
    return(Discharge_dict, River_dict)    