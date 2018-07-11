# -*- coding: utf-8 -*-
"""
Authors: Bert Coerver, Tim Hessels
         UNESCO-IHE 2018
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Three
"""
import csv
import numpy as np
import calendar
import datetime
import os
from dateutil.relativedelta import relativedelta
import wa


def Seasons(start_dates, end_dates, dir_nc_outname, lu_class, croptype, output_dir, ab):
    """
    Calculate Yields and WPs per season and save results in a csv-file.

    Parameters
    ----------
    start_dates : ndarray
        Array with datetime.date objects specifying the startdates of the growing seasons. See ndvi_profiles.py.
    end_dates : ndarray
        Array with datetime.date objects specifying the enddates of the growing seasons. See ndvi_profiles.py.
    dir_nc_outname : str
        Directory to all the netcdf data
    lu_class : int
        Landuseclass for which to calculate Y and WP.
    croptype : str
        Name of croptype, should be present in HIWC_dict.keys().
    output_dir : str
        Folder to save results
    ab : tuple, optional
        Two parameters used to split Yield into irrigation and precipitation yield, see split_Yield.

    Returns
    -------
    csv_filename : str
        Path to newly created csv-file.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_filename = os.path.join(output_dir, 'Yields_WPs_{0}.csv'.format(croptype))
    csv_file = open(csv_filename, 'wb')
    writer = csv.writer(csv_file, delimiter=';')

    writer.writerow(["Startdate", "Enddate", "Yield [kg/ha]", "Yield_pr [kg/ha]", "Yield_irr [kg/ha]", "WP [kg/m3]", "WP_blue [kg/m3]", "WP_green [kg/m3]", "WC [km3]", "WC_blue [km3]", "WC_green [km3]"])
    for startdate, enddate in zip(start_dates, end_dates):
        Yield, Yield_pr, Yield_irr, Wp, Wp_blue, Wp_green, Wc, Wc_blue, Wc_green = Season(startdate, enddate, dir_nc_outname, lu_class, croptype, ab)

        writer.writerow([startdate, enddate, Yield, Yield_pr, Yield_irr, Wp, Wp_blue, Wp_green, Wc, Wc_blue, Wc_green])

    csv_file.close()

    return csv_filename

def Season(startdate, enddate, dir_nc_outname, lu_class, croptype, ab = (1.0,0.9)):

    """
    Calculate Yields and WPs for one season.

    Parameters
    ----------
    startdate : object
        datetime.date object specifying the startdate of the growing season.
    enddate : ndarray
        datetime.date object specifying the enddate of the growing season.
    nc_outname : str
        Path all the data.
    lu_class : int
        Landuseclass for which to calculate Y and WP.
    croptype : str
        Name of croptype, should be present in HIWC_dict.keys().
    HIWC_dict : dict
        Dictionary with Harvest indices and Water Contents, see get_dictionaries.get_hi_and_ec().
    ab : tuple, optional
        Two parameters used to split Yield into irrigation and precipitation yield, see split_Yield.

    Returns
    -------
    Yield_Ave_Value : float
        The yield for the croptype.
    Yield_pr_Ave_Value : float
        The yield_precip for the croptype.
    Yield_irr_Ave_Value : float
        The yield_irri for the croptype.
    WP_Ave_Value : float
        The waterproductivity for the croptype.
    WPblue_Ave_Value : float
        The blue waterproductivity for the croptype.
    WPgreen_Ave_Value : float
        The green waterproductivity for the croptype.
    WC_Ave_Value : float
        The water consumption for the croptype.
    WCblue_Ave_Value : float
        The blue water consumption for the croptype.
    WCgreen_Ave_Value : float
        The green water consumption for the croptype.
    """

    import wa.Functions.Three as Three
    import wa.Functions.Start.Get_Dictionaries as GD
    import wa.General.raster_conversions as RC

    # Open the HIWC dict
    HIWC_dict = GD.get_hi_and_ec()

    # Get Harvest Index and Moisture content for a specific crop
    harvest_index = HIWC_dict[croptype][0]
    moisture_content = HIWC_dict[croptype][1]

    # Get the start and enddate current season
    current = datetime.date(startdate.year, startdate.month, 1)
    end_month = datetime.date(enddate.year, enddate.month, 1)

    req_dates = np.array([current])
    while current < end_month:
        current = current + relativedelta(months = 1)
        req_dates = np.append(req_dates, current)

    # Define input one nc file
    nc_outname_start = os.path.join(dir_nc_outname, "%d.nc" %(int(startdate.year)))
    nc_outname_end = os.path.join(dir_nc_outname, "%d.nc" %(int(enddate.year)))

    if not (os.path.exists(nc_outname_start) or os.path.exists(nc_outname_end)):
        date = req_dates[0]
        print("{0} missing in input data, skipping this season".format(date))
        Yield_Ave_Value = Yield_pr_Ave_Value = Yield_irr_Ave_Value = WP_Ave_Value = WPblue_Ave_Value = WPgreen_Ave_Value = WC_Ave_Value = WCblue_Ave_Value = WCgreen_Ave_Value = np.nan

    else:

        # Calculate the monthly fraction (if season is not whithin the whole month)
        fractions = np.ones(np.shape(req_dates))

        # The get the start month and end month fraction and report those to fraction
        start_month_length = float(calendar.monthrange(startdate.year, startdate.month)[1])
        end_month_length = float(calendar.monthrange(enddate.year, enddate.month)[1])

        fractions[0] = (start_month_length - startdate.day + 1) / start_month_length
        fractions[-1] = (enddate.day -1) / end_month_length

        # Get total sum NDM over the growing season
        NDM_array = RC.Open_ncs_array(dir_nc_outname, "Normalized_Dry_Matter", startdate.replace(day=1), enddate)
        NDM = np.nansum(NDM_array * fractions[:,None,None], axis=0)
        del NDM_array

        # Get total sum ET blue over the growing season
        ETgreen_array = RC.Open_ncs_array(dir_nc_outname, "Green_Evapotranspiration", startdate.replace(day=1), enddate)
        ETgreen = np.nansum(ETgreen_array * fractions[:,None,None], axis=0)
        del ETgreen_array

        # Get total sum ET green over the growing season
        ETblue_array = RC.Open_ncs_array(dir_nc_outname, "Blue_Evapotranspiration", startdate.replace(day=1), enddate)
        ETblue = np.nansum(ETblue_array * fractions[:,None,None], axis=0)
        del ETblue_array

        # Get total sum Precipitation over the growing season
        P_array = RC.Open_ncs_array(dir_nc_outname, "Precipitation", startdate.replace(day=1), enddate)
        P = np.nansum(P_array * fractions[:,None,None], axis=0)
        del P_array

        # Open Landuse map
        LULC = RC.Open_nc_array(nc_outname_start, "Landuse")

        # only select the pixels for this Landuse class
        NDM[NDM == 0] = np.nan
        NDM[LULC != lu_class] = ETblue[LULC != lu_class] = ETgreen[LULC != lu_class] =  np.nan

        # Calculate Yield
        Y_Array = (harvest_index * NDM) / (1 - moisture_content)

        # Calculate fractions of ETblue and green and blue Yield
        ETblue_fraction = ETblue / (ETblue + ETgreen)
        p_fraction = P / np.nanmax(P)
        fraction = Three.SplitYield.P_ET_based(p_fraction, ETblue_fraction, ab[0], ab[1])

        # Calculate yield from irrigation and precipitation
        Yirr_Array = Y_Array * fraction
        Ypr_Array = Y_Array - Yirr_Array

        '''
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
        '''

        # calculate average Yields
        Yield_Ave_Value = np.nanmean(Y_Array)
        Yield_pr_Ave_Value = np.nanmean(Ypr_Array)
        Yield_irr_Ave_Value = np.nanmean(Yirr_Array)

        # calculate average blue and green ET
        ETblue_Ave_Value = np.nanmean(ETblue)
        ETgreen_Ave_Value = np.nanmean(ETgreen)

        # Calculate Areas for one pixel
        areas_m2 = wa.Functions.Start.Area_converter.Degrees_to_m2(nc_outname_start)

        # Calculate the total area in km2
        areas_m2[LULC != lu_class] = np.nan
        areas_km2 = areas_m2/1000**2
        print('{0}: {1} km2'.format(croptype, np.nansum(areas_km2)))

        # Calculate the Water consumpution in km3
        WCblue_Ave_Value = np.nansum(ETblue_Ave_Value /1000**2 * areas_km2)
        WCgreen_Ave_Value = np.nansum(ETgreen_Ave_Value /1000**2 * areas_km2)
        WC_Ave_Value = WCblue_Ave_Value + WCgreen_Ave_Value

        # Calculate water productivity
        WP_Ave_Value = Yield_Ave_Value / ((ETblue_Ave_Value + ETgreen_Ave_Value) * 10)
        WPblue_Ave_Value = np.where(ETblue_Ave_Value == 0, [np.nan], [Yield_irr_Ave_Value / (ETblue_Ave_Value * 10)])[0]
        WPgreen_Ave_Value = np.where(ETgreen_Ave_Value == 0, [np.nan], [Yield_pr_Ave_Value / (ETgreen_Ave_Value * 10)])[0]

    return Yield_Ave_Value, Yield_pr_Ave_Value, Yield_irr_Ave_Value, WP_Ave_Value, WPblue_Ave_Value, WPgreen_Ave_Value, WC_Ave_Value, WCblue_Ave_Value, WCgreen_Ave_Value


def Create_WP_Y_CSV(csv_fh, output_dir, croptype):
    """
    Calculate yearly Yields and Water Productivities from seasonal values (created with calc_Y_WP_seasons) and store
    results in a csv-file.

    Parameters
    ----------
    csv_fh : str
        csv_file with seasonal values (see calc_Y_WP_seasons)
    output_dir : str
        Folder to store results.
    croptype : str
        Name of the crop for which the Y and WP have been calculated.

    Returns
    -------
    csv_filename : str
        Path to the new csv-file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    start_dates, end_dates, Y, Yirr, Ypr, WP, WPblue, WPgreen, WC, WC_blue, WC_green = read_csv(csv_fh)

    years = np.unique(np.array([date.year for date in np.append(start_dates, end_dates)]))

    csv_filename = os.path.join(output_dir, 'Yearly_Yields_WPs_{0}.csv'.format(croptype))
    csv_file = open(csv_filename, 'wb')
    writer = csv.writer(csv_file, delimiter=';')
    writer.writerow(["Startdate", "Enddate", "Yield [kg/ha]", "Yield_pr [kg/ha]", "Yield_irr [kg/ha]", "WP [kg/m3]", "WP_blue [kg/m3]", "WP_green [kg/m3]", "WC [km3]", "WC_blue [km3]", "WC_green [km3]"])

    for year in years:

        starts, ends = (np.array([start_date for start_date, end_date in zip(start_dates, end_dates) if start_date.year == year or end_date.year == year]),
                        np.array([end_date for start_date, end_date in zip(start_dates, end_dates) if start_date.year == year or end_date.year == year]))

        boundary = datetime.date(year, 1, 1)

        year_length = 366 if calendar.isleap(year) else 365

        lengths_total_season = [float(abs((end - start).days)) for start, end in zip(starts, ends)]

        lengths_within_year = np.array([min(year_length, abs((boundary - end).days)) - abs(min(0, (boundary - start).days)) for start, end in zip(starts, ends)])

        fractions = lengths_within_year / lengths_total_season

        y = np.sum(np.array([Y[start_dates == start][0] for start in starts]) * fractions)
        yirr = np.sum(np.array([Yirr[start_dates == start][0] for start in starts]) * fractions)
        ypr = np.sum(np.array([Ypr[start_dates == start][0] for start in starts]) * fractions)

        wc = np.sum(np.array([WC[start_dates == start][0] for start in starts]) * fractions)
        wcblue = np.sum(np.array([WC_blue[start_dates == start][0] for start in starts]) * fractions)
        wcgreen = np.sum(np.array([WC_green[start_dates == start][0] for start in starts]) * fractions)

        wp = np.average(np.array([WP[start_dates == start][0] for start in starts]), weights = fractions)
        wpblue = np.average(np.array([WPblue[start_dates == start][0] for start in starts]), weights = fractions)
        wpgreen = np.average(np.array([WPgreen[start_dates == start][0] for start in starts]), weights = fractions)

        writer.writerow([datetime.date(year,1,1), datetime.date(year,12,31), y, ypr, yirr, wp, wpblue, wpgreen, wc, wcblue, wcgreen])

    csv_file.close()

    return csv_filename

def read_csv(csv_fh):
    """
    Reads and csv file generated by the function calc_Y_WP_seasons and returns the
    values as np.arrays.

    Parameters
    ----------
    csv_fh : str
        Filehandle pointing to a csv-file generated by calc_Y_WP_seasons.

    Returns
    -------
    start_dates : ndarray
        Array containing datetime.date objects.
    end_dates : ndarray
        Array containing datetime.date objects.
    Y : ndarray
        Array containing Yield data.
    Yirr : ndarray
        Array containing Yield from irrigation data.
    Ypr : ndarray
        Array containing Yield from precipitation data.
    WP : ndarray
        Array containing Water Productivity data.
    WPblue : ndarray
        Array containing Blue WP data.
    WPgreen : ndarray
        Array containing Green WP data.
    """
    start_dates = np.array([])
    end_dates = np.array([])
    Y = np.array([])
    Yirr = np.array([])
    Ypr = np.array([])
    WP = np.array([])
    WPblue = np.array([])
    WPgreen = np.array([])
    WC = np.array([])
    WC_green = np.array([])
    WC_blue = np.array([])

    with open(csv_fh) as csvfile:
         reader = csv.reader(csvfile, delimiter=';')
         for row in reader:
             if np.all([row[2] != 'nan', row[0] != 'Startdate']):
                 try:
                     start_dates = np.append(start_dates, datetime.datetime.strptime(row[0], '%Y-%m-%d').date())
                     end_dates = np.append(end_dates, datetime.datetime.strptime(row[1], '%Y-%m-%d').date())
                 except:
                     start_dates = np.append(start_dates, datetime.datetime.strptime(row[0], '%d/%m/%Y').date())
                     end_dates = np.append(end_dates, datetime.datetime.strptime(row[1], '%d/%m/%Y').date())
                 Y = np.append(Y, float(row[2]))
                 Ypr = np.append(Ypr, float(row[3]))
                 Yirr = np.append(Yirr, float(row[4]))
                 WP = np.append(WP, float(row[5]))
                 WPblue = np.append(WPblue, float(row[6]))
                 WPgreen = np.append(WPgreen, float(row[7]))
                 WC = np.append(WC, float(row[8]))
                 WC_blue = np.append(WC_blue, float(row[9]))
                 WC_green = np.append(WC_green, float(row[10]))


    return start_dates, end_dates, Y, Yirr, Ypr, WP, WPblue, WPgreen, WC, WC_blue, WC_green

