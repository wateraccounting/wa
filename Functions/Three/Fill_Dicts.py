# -*- coding: utf-8 -*-
"""
Authors: Bert Coerver, Tim Hessels
         UNESCO-IHE 2018
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Four
"""


def Crop_Dictionaries(wp_y_irrigated_dictionary, wp_y_rainfed_dictionary, dict_crops, nc_outname, output_dir):

    import os
    import wa.General.raster_conversions as RC
    import wa.Functions.Three as Three

    # open LULC map
    LULC_Array = RC.Open_nc_array(nc_outname, "Landuse")

    # dictory of the netcdf file
    dir_nc_outname = os.path.dirname(nc_outname)

    # loop over the crops calendars
    for crop in dict_crops['crops']:

        # Check if the croptype is located within the LULC map
        if crop[4] in LULC_Array:

            # Open the start and enddate of the cropping calendar
            start_dates, end_dates = import_growing_seasons(crop[0])
            result_seasonly = Three.Calc_Y_WP.Seasons(start_dates, end_dates, dir_nc_outname, crop[4], crop[1], output_dir, ab = (1.0,0.9))

            result = Three.Calc_Y_WP.Create_WP_Y_CSV(result_seasonly, os.path.join(output_dir, 'WP_Y_Yearly_csvs'), crop[1])
            if crop[4] > 50:
                wp_y_irrigated_dictionary[crop[2]][crop[3]] = result
            else:
                wp_y_rainfed_dictionary[crop[2]][crop[3]] = result

        else:
            print "skipping crop with lu-class {0}, not on LU-map".format(crop[4])
            continue

    return(wp_y_irrigated_dictionary, wp_y_rainfed_dictionary)


def Non_Crop_Dictionaries(wp_y_non_crop_dictionary, dict_non_crops):

    import numpy as np

    if len(dict_non_crops['non_crop']) > 0:
        try:
            wp_y_non_crop_dictionary['Livestock']['Meat'] = dict_non_crops['non_crop'][np.where([i == "meat" for number, (i, non_crop) in enumerate(dict_non_crops['non_crop'])])[0][0]][1]
        except:
            wp_y_non_crop_dictionary['Livestock']['Meat'] = None
        try:
            wp_y_non_crop_dictionary['Livestock']['Milk'] = dict_non_crops['non_crop'][np.where([i == "milk" for number, (i, non_crop) in enumerate(dict_non_crops['non_crop'])])[0][0]][1]
        except:
            wp_y_non_crop_dictionary['Livestock']['Milk'] = None
        try:
            wp_y_non_crop_dictionary['Fish (Aquaculture)']['-'] = dict_non_crops['non_crop'][np.where([i == "aquaculture" for number, (i, non_crop) in enumerate(dict_non_crops['non_crop'])])[0][0]][1]
        except:
            wp_y_non_crop_dictionary['Fish (Aquaculture)']['-'] = None
        try:
            wp_y_non_crop_dictionary['Timber']['-'] = dict_non_crops['non_crop'][np.where([i == "timber" for number, (i, non_crop) in enumerate(dict_non_crops['non_crop'])])[0][0]][1]
        except:
            wp_y_non_crop_dictionary['Timber']['-'] = None

    return(wp_y_non_crop_dictionary)

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

    import datetime
    import numpy as np
    import csv

    start_dates = np.array([])
    end_dates = np.array([])

    with open(csv_fh) as csvfile:
         reader = csv.reader(csvfile, delimiter=';')
         for row in reader:
             if np.all([row[0] != 'Start', row[1] != 'End']):
                 start_dates = np.append(start_dates, datetime.datetime.strptime(row[0], '%d/%m/%Y').date())
                 end_dates = np.append(end_dates, datetime.datetime.strptime(row[1], '%d/%m/%Y').date())

    return start_dates, end_dates
