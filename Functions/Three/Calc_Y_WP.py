# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 17:34:54 2018

@author: tih
"""

import numpy as np
import calendar
import datetime
#import wa.Functions.Start.Get_Dictionaries as GD


def Seasons():
    """
    Calculate Yields and WPs per season and save results in a csv-file.
    
    Parameters
    ----------
    start_dates : ndarray
        Array with datetime.date objects specifying the startdates of the growing seasons. See ndvi_profiles.py.
    end_dates : ndarray
        Array with datetime.date objects specifying the enddates of the growing seasons. See ndvi_profiles.py.
    lu_fh : str
        Landuse map.
    lu_class : int
        Landuseclass for which to calculate Y and WP.
    croptype : str
        Name of croptype, should be present in HIWC_dict.keys().
    etgreen_fhs : ndarray
        Array with strings pointing to ETgreen maps.
    etgreen_dates : ndarray
        Array with datetime.date objects corresponding to etgreen_fhs.
    etblue_fhs : ndarray
        Array with strings pointing to ETblue maps.
    etblue_dates : ndarray
        Array with datetime.date objects corresponding to etblue_fhs.
    ndm_fhs : ndarray
        Array with strings pointing to Net-Dry-Matter maps.
    ndm_dates : ndarray
        Array with datetime.date objects corresponding to ndm_fhs.
    p_fhs : ndarray
        Array with strings pointing to P maps.
    p_dates : ndarray
        Array with datetime.date objects corresponding to p_fhs.
    output_dir : str
        Folder to save results
    HIWC_dict : dict
        Dictionary with Harvest indices and Water Contents, see get_dictionaries.get_hi_and_ec().
    ab : tuple, optional
        Two parameters used to split Yield into irrigation and precipitation yield, see split_Yield.
        
    Returns
    -------
    csv_filename : str
        Path to newly created csv-file.        
    """   
    
    Startdate = "2014-01-01"
    Enddate = "2014-12-31"
    
    Name_NC_LU = r'J:\\Create_Sheets\\Hong\\Simulations\\Simulation_1\\Sheet_3\\LU_Simulation1_.nc'
    Name_NC_ETref = r'J:\\Create_Sheets\\Hong\\Simulations\\Simulation_1\\Sheet_3\\ETref_Simulation1_monthly_mm_082013_122014.nc'
    Name_NC_ET = r'J:\\Create_Sheets\\Hong\\Simulations\\Simulation_1\\Sheet_3\\ET_Simulation1_monthly_mm_012014_122014.nc'
    Name_NC_P = r'J:\\Create_Sheets\\Hong\\Simulations\\Simulation_1\\Sheet_3\\Prec_Simulation1_monthly_mm_082013_122014.nc'
    Name_NC_NDM = r"J:\Create_Sheets\Hong\Simulations\Simulation_1\Sheet_3\NDM_Simulation1_monthly_kg_ha-1_012014_122014.nc"

    dict_crops = {'crops':   [r"J:\Create_Sheets\Hong\seasons_basin_crop35.csv", 'Rice - Rainfed', 'Cereals', '-', 35.0]}
    
    HIWC_dict = GD.get_hi_and_ec()
    #croptype =  
 
    #lu_fh, lu_class, croptype, HIWC_dict, ab = (1.0,1.0)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)    
    
    csv_filename = os.path.join(output_dir, 'Yields_WPs_{0}.csv'.format(croptype))
    csv_file = open(csv_filename, 'wb')
    writer = csv.writer(csv_file, delimiter=';')
    
    writer.writerow(["Startdate", "Enddate", "Yield [kg/ha]", "Yield_pr [kg/ha]", "Yield_irr [kg/ha]", "WP [kg/m3]", "WP_blue [kg/m3]", "WP_green [kg/m3]", "WC [km3]", "WC_blue [km3]", "WC_green [km3]"])
    for startdate, enddate in zip(start_dates, end_dates):
        Yield, Yield_pr, Yield_irr, Wp, Wp_blue, Wp_green, Wc, Wc_blue, Wc_green = Season(startdate, enddate, lu_fh, lu_class, croptype, etgreen_fhs, etgreen_dates, etblue_fhs, etblue_dates, ndm_fhs, ndm_dates, p_fhs, p_dates, HIWC_dict, ab = ab, output_dir = output_dir)
        
        writer.writerow([startdate, enddate, Yield, Yield_pr, Yield_irr, Wp, Wp_blue, Wp_green, Wc, Wc_blue, Wc_green])
    
    csv_file.close()
    
    return csv_filename


   
def Season(startdate, enddate, lu_fh, lu_class, croptype, etgreen_fhs, etgreen_dates, etblue_fhs, etblue_dates, ndm_fhs, ndm_dates, p_fhs, p_dates, HIWC_dict, ab = (1.0,1.0), output_dir = None):
    """
    Calculate Yields and WPs for one season.
    
    Parameters
    ----------
    startdate : object
        datetime.date object specifying the startdate of the growing season.
    enddate : ndarray
        datetime.date object specifying the enddate of the growing season.
    lu_fh : str
        Landuse map.
    lu_class : int
        Landuseclass for which to calculate Y and WP.
    croptype : str
        Name of croptype, should be present in HIWC_dict.keys().
    etgreen_fhs : ndarray
        Array with strings pointing to ETgreen maps.
    etgreen_dates : ndarray
        Array with datetime.date objects corresponding to etgreen_fhs.
    etblue_fhs : ndarray
        Array with strings pointing to ETblue maps.
    etblue_dates : ndarray
        Array with datetime.date objects corresponding to etblue_fhs.
    ndm_fhs : ndarray
        Array with strings pointing to Net-Dry-Matter maps.
    ndm_dates : ndarray
        Array with datetime.date objects corresponding to ndm_fhs.
    p_fhs : ndarray
        Array with strings pointing to P maps.
    p_dates : ndarray
        Array with datetime.date objects corresponding to p_fhs.
    output_dir : str
        Folder to save results
    HIWC_dict : dict
        Dictionary with Harvest indices and Water Contents, see get_dictionaries.get_hi_and_ec().
    ab : tuple, optional
        Two parameters used to split Yield into irrigation and precipitation yield, see split_Yield.
        
    Returns
    -------
    Yield : float
        The yield for the croptype.
    Yield_pr : float
        The yield_precip for the croptype.
    Yield_irr : float
        The yield_irri for the croptype.
    Wp : float
        The waterproductivity for the croptype.
    Wp_blue : float
        The blue waterproductivity for the croptype.
    Wp_green : float
        The green waterproductivity for the croptype.
    Wc : float
        The water consumption for the croptype.
    Wc_blue : float
        The blue water consumption for the croptype.
    Wc_green : float
        The green water consumption for the croptype.
    """
    common_dates = becgis.CommonDates([etblue_dates, etgreen_dates, p_dates, ndm_dates])
    
    harvest_index = HIWC_dict[croptype][0]  
    moisture_content = HIWC_dict[croptype][1]
    
    current = datetime.date(startdate.year, startdate.month, 1)
    end_month = datetime.date(enddate.year, enddate.month, 1)
    
    req_dates = np.array([current])
    while current < end_month:
        current = current + relativedelta(months = 1)
        req_dates = np.append(req_dates, current)
    
    season_complete = True
    for date in req_dates:
        season_complete = np.all([season_complete, date in common_dates])
        if not season_complete:
            print("{0} missing in input data, skipping this season".format(date))
            
    if season_complete:
    
        fractions = np.ones(np.shape(req_dates))
        
        start_month_length = float(calendar.monthrange(startdate.year, startdate.month)[1])
        end_month_length = float(calendar.monthrange(enddate.year, enddate.month)[1])
        
        fractions[0] = (start_month_length - startdate.day + 1) / start_month_length
        fractions[-1] = (enddate.day -1) / end_month_length
        
        NDMs = np.stack([becgis.OpenAsArray(ndm_fhs[ndm_dates == date][0], nan_values = True) * fraction for date, fraction in zip(req_dates, fractions)], axis=2)
        NDM = np.nansum(NDMs, axis=2)
        del NDMs
        
        ETGREENs = np.stack([becgis.OpenAsArray(etgreen_fhs[etgreen_dates == date][0], nan_values = True) * fraction for date, fraction in zip(req_dates, fractions)], axis=2)
        ETGREEN = np.nansum(ETGREENs, axis=2)
        del ETGREENs
        
        ETBLUEs = np.stack([becgis.OpenAsArray(etblue_fhs[etblue_dates == date][0], nan_values = True) * fraction for date, fraction in zip(req_dates, fractions)], axis=2)
        ETBLUE = np.nansum(ETBLUEs, axis=2)
        del ETBLUEs
        
        Ps = np.stack([becgis.OpenAsArray(p_fhs[p_dates == date][0], nan_values = True) * fraction for date, fraction in zip(req_dates, fractions)], axis=2)
        P = np.nansum(Ps, axis=2)
        del Ps
        
        LULC = becgis.OpenAsArray(lu_fh)
        
        NDM[NDM == 0] = np.nan
        NDM[LULC != lu_class] = ETBLUE[LULC != lu_class] = ETGREEN[LULC != lu_class] =  np.nan
        
        Y = (harvest_index * NDM) / (1 - moisture_content)
        
        etbfraction = ETBLUE / (ETBLUE + ETGREEN)
        pfraction = P / np.nanmax(P)
        fraction = split_Yield(pfraction, etbfraction, ab[0], ab[1])
        
        Yirr = Y * fraction
        Ypr = Y - Yirr

        if output_dir:
            x = y = np.arange(0.0, 1.1, 0.1)
            XX, YY = np.meshgrid(x, y)
            Z = split_Yield(XX,YY, ab[0], ab[1])
            plt.figure(1, figsize = (12,10))
            plt.clf()
            cmap = LinearSegmentedColormap.from_list('mycmap', ['#6bb8cc','#a3db76','#d98d8e'])
            plt.contourf(XX,YY,Z,np.arange(0.0,1.1,0.1), cmap = cmap)
            plt.colorbar(ticks = np.arange(0.0,1.1,0.1), label= 'Yirr as fraction of total Y [-]', boundaries = [0,1])
            plt.xlabel('Normalized Precipitation [-]')
            plt.ylabel('ETblue/ET [-]')
            plt.title('Split Yield into Yirr and Ypr')
            plt.suptitle('Z(X,Y) = -(((Y-1) * a)^2 - ((X-1) * b)^2) + 0.5 with a = {0:.2f} and b = {1:.2f}'.format(ab[0],ab[1]))
            plt.scatter(pfraction, etbfraction, color = 'w', label = croptype, edgecolors = 'k')
            plt.legend()
            plt.xlim((0,1))
            plt.ylim((0,1))
            plt.savefig(os.path.join(output_dir, '{0}_{1}_{2}_cloud.png'.format(croptype, req_dates[0], req_dates[-1])))

        Yield = np.nanmean(Y)
        Yield_pr = np.nanmean(Ypr)
        Yield_irr = np.nanmean(Yirr)
        
        Et_blue = np.nanmean(ETBLUE)
        Et_green = np.nanmean(ETGREEN)
        
        areas = becgis.MapPixelAreakm(lu_fh)
        Wc_blue = np.nansum(ETBLUE / 1000**2 * areas)
        Wc_green = np.nansum(ETGREEN / 1000**2 * areas)
        Wc = Wc_blue + Wc_green
        
        areas[LULC != lu_class] = np.nan
        print('{0}: {1} km2'.format(croptype, np.nansum(areas)))
        
        Wp = Yield / ((Et_blue + Et_green) * 10)
        Wp_blue = np.where(Et_blue == 0, [np.nan], [Yield_irr / (Et_blue * 10)])[0]
        Wp_green = np.where(Et_green == 0, [np.nan], [Yield_pr / (Et_green * 10)])[0]
        
    else:
        
        Yield = Yield_pr = Yield_irr = Wp = Wp_blue = Wp_green = Wc = Wc_blue = Wc_green = np.nan
        
    return Yield, Yield_pr, Yield_irr, Wp, Wp_blue, Wp_green, Wc, Wc_blue, Wc_green



def import_growing_seasons(csv_fh):
    """
    Reads an csv file with dates, see example for format of the csv file.
    
    Parameters
    ----------
    csv_fh : str
        Filehandle pointing to csv-file
        
    Returns
    -------
    start_dates : ndarray
        List with datetime.date objects
    end_dates : ndarray
        List with datetime.date object
    
    Examples
    --------
    The csv file should be like:
    >>> Start;End<new_line> 
            04/11/2000;17/02/2001<new_line>
            03/05/2001;02/07/2001<new_line>
            29/11/2001;27/02/2002<new_line>
            etc.
    
    """
    start_dates = np.array([])
    end_dates = np.array([])

    with open(csv_fh) as csvfile:
         reader = csv.reader(csvfile, delimiter=';')
         for row in reader:
             if np.all([row[0] != 'Start', row[1] != 'End']):
                 start_dates = np.append(start_dates, datetime.datetime.strptime(row[0], '%d/%m/%Y').date())
                 end_dates = np.append(end_dates, datetime.datetime.strptime(row[1], '%d/%m/%Y').date())
    
    return start_dates, end_dates