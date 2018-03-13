# -*- coding: utf-8 -*-
"""
Authors: Gonzalo E. Espinoza-Dávalos
         IHE Delft 2017
Contact: g.espinoza@un-ihe.org
Repository: https://github.com/gespinoza/waterpix
Module: waterpix
"""

from __future__ import division
from math import exp, sqrt
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.optimize import fsolve
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri

np = pd.np


def calculate_first_round(df, pixel_pars, infz_bounds,
                          tolerance_yearly_waterbal):
    '''
    Calculates the water balance for a single cell and a single year on
    green pixels
    '''
    # Pixel parameters
    thetasat, rootdepth, qratio, baseflow_filter = pixel_pars
    # LAI and soil moisture calculations
    df = lai_and_soil_calculations(df, thetasat, rootdepth)
    # Check P-ET-dsm
    p_et_dsm = sum(df['p']) - sum(df['et']) - sum(df['dsm'])
    if p_et_dsm <= 0:
        df = return_empty_df_columns(df)
        second_round = 20
    elif np.isnan(p_et_dsm):
        df = return_empty_df_columns(df)
        second_round = 0
    else:
        # Vegetation and interception calculations
        df = veg_int_calc(df)
        # Numeric solver
        minerror_infz = minimize_scalar(flows_calculations_first_round,
                                        bounds=infz_bounds,
                                        args=(df, (qratio, baseflow_filter,
                                                   p_et_dsm), True),
                                        method='bounded')
        # Flows calculation
        df = flows_calculations_first_round(minerror_infz.x, df,
                                            (qratio, baseflow_filter,
                                             p_et_dsm), False)
        # Water balance fix for when percolation is artificially set to 0
        maski = (df['p'] - df['et'] - df['Qsw'] - df['dsm']) < 0
        if np.any(maski):
            df['Qsw'][maski] = df['p'][maski] - df['et'][maski] - df['dsm'][maski]
        df['Qsw'] = df['Qsw'].apply(pos_func, 'columns')    
            
        if sqrt(minerror_infz.fun) > tolerance_yearly_waterbal:
            df = return_empty_df_columns(df)
            second_round = 30
        else:
            df['Qtot'] = df['Qsw'] + df['Qgw']
            second_round = 0
    # Total runoff
    df_out = df[['Qsw', 'Qgw', 'Qtot', 'dsm', 'infz', 'thetarz', 'perc']]
    # Return data frame and second_round boolean
    return df_out, second_round


def flows_calculations_first_round(infz, df, pixel_pars,
                                   return_error):
    '''
    Perform a first-round single iteration of the water balance (unbalanced)
    at a pixel
    '''
    # Pixel parameters
    qratio, baseflow_filter, p_et_dsm = pixel_pars
    # Calibration parameter
    df['infz'] = infz
    # Runoff
    df['Qsw'] = df['P_Int_2'] / (df['p'] - df['interception'] +
                                 df['infz'] * (df['thetasat'] - df['theta0']))
    df['Qgw'] = baseflow_calculation(np.array(df['Qsw']),
                                     baseflow_filter, qratio)
    # Remaining term of the water balance
    df['Rest_Term'] = df['p'] - df['et'] - df['Qsw'] - df['dsm']
    df['Rest_Term_pos'] = df['Rest_Term'].apply(pos_func, 'columns')
#    rest_term_sum = df['Rest_Term_pos'].sum()
#    # Correction of percolation using baseflow
#    if rest_term_sum > 0:
#        corr_factor = max(1, df['Qgw'].sum()/rest_term_sum)
#    else:
#        corr_factor = 1
#    df['perc'] = corr_factor * df['Rest_Term'].apply(pos_func, 'columns')
    df['perc'] = df['Rest_Term_pos']
    # Error calculation
    flows = sum(df['Qsw']) + sum(df['Qgw'])
#    flows = sum(df['Qsw']) +sum(df['Rest_Term'] )
    
    error = (p_et_dsm - flows) ** 2
    # Return error or data frame
    if return_error:
        return abs(error)
    else:
        return df


def calculate_second_round(df, pixel_pars, default_eff,
                           tolerance_monthly_greenpx,
                           incrunoff_propfactor_bounds):
    '''
    Calculates the water balance for a single cell and a single year on
    blue pixels.
    '''
    # Pixel parameters
    (thetasat, rootdepth, qratio, infz, a, b,
     green_et_yr, blue_et_yr, baseflow_filter) = pixel_pars
    # LAI and soil moisture calculations
    df = lai_and_soil_calculations(df, thetasat, rootdepth)
    # Vegetation and interception calculations
    df = veg_int_calc(df)
    # Percolation
    df['perc'] = a * (df['thetarz']) ** b
    # Flows calculation
    df = flows_calculations_second_round(infz, df, (qratio, baseflow_filter,
                                                    green_et_yr, blue_et_yr),
                                         default_eff,
                                         tolerance_monthly_greenpx,
                                         incrunoff_propfactor_bounds)
    # Total runoff
    df['Qtot'] = df['Qsw'] + df['Qgw']
    # Output data frame
    df_out = df[['Qsw', 'delta_Qsw', 'Qgw', 'Qtot', 'dsm', 'infz', 'thetarz',
                 'perc', 'delta_perc', 'supply', 'eff', 'rainfed',
                 'et_blue','et_green']]
    # Return data frame
    return df_out


def flows_calculations_second_round(infz, df, pixel_pars, default_eff,
                                    tolerance_monthly_greenpx,
                                    incrunoff_propfactor_bounds):
    '''
    Perform a second-round single iteration of the water balance (unbalanced)
    at a pixel
    '''
    # Pixel parameters
    qratio, baseflow_filter, green_et_yr, blue_et_yr = pixel_pars
    # Calibration parameter
    df['infz'] = infz
    # ET blue/green partitioning using the budyko curve
    df['phi'] = df['eto']/df['p']
    df['phi'].replace([np.inf, -np.inf], np.nan)
    df['phi'] = df['phi'].apply(zeros_and_negatives, 'columns')
    df['budyko'] = df['phi'].apply(budyko, 'columns')
    df['et_green'] = pd.DataFrame([1.1*df['budyko']*df['p'], df['et']]).min()
    et_green_sum = df['et_green'].sum()
    if et_green_sum > 0:
        df['et_green'] = (green_et_yr/et_green_sum)*df['et_green']
    df['et_blue'] = df['et'] - df['et_green']
    et_blue_sum = df['et_blue'].sum()
    if et_blue_sum > 0:
        df['et_blue'] = (blue_et_yr/et_blue_sum)*df['et_blue']

    # Runoff
    df['Qsw_green'] = df['P_Int_2'] / (
        df['p'] - df['interception'] +
        df['infz'] * (df['thetasat'] - df['theta0']))
    # Remaining term of the water balance
    df['Rest_Term'] = df['p'] - df['et'] - df['Qsw_green'] - df['dsm']
    df['Rest_Term2'] = df['p'] - df['et_green'] - df['Qsw_green'] - df['dsm']
    df['Rest_Term_pos'] = df['Rest_Term'].apply(pos_func, 'columns')
    df['Rest_Term_pos2'] = df['Rest_Term2'].apply(pos_func, 'columns')
#    rest_term_sum = df['Rest_Term_pos'].sum()
    # Correction of percolation using baseflow
    df['Qgw_green'] = baseflow_calculation(np.array(df['Qsw_green']),
                                           baseflow_filter, qratio)
#    if rest_term_sum > 0:
#        corr_factor = max(1, df['Qgw_green'].sum()/rest_term_sum)
#    else:
#        corr_factor = 1
    corr_factor = 1
    df['perc_green'] = corr_factor * df['Rest_Term'].apply(pos_func, 'columns')
    # Check for months without supply and correct percolation
    for index, row in df.iterrows():
        if row['et'] - row['et_green'] < tolerance_monthly_greenpx:
            df.set_value(index, 'perc', row['perc_green'])
        else:
            df.set_value(index, 'perc', row['perc'])
            df['perc_green'] = corr_factor * df['Rest_Term2'].apply(pos_func, 'columns')
    # Incremental percolation
    df['delta_perc_diff'] = df['perc'] - df['perc_green']
    df['delta_perc'] = df['delta_perc_diff'].apply(pos_func, 'columns')
    # Check if ET blue is zero
    if df['et_blue'].sum() <= 0:
        # No supply
        df['delta_Qsw'] = 0.0
        df['Qsw'] = df['Qsw_green']
        df['Qgw'] = df['Qgw_green']
        df['supply'] = 0
        df['eff'] = -9999
        df['rainfed'] = 1
        df['et_blue'] = 0
        df['et_green'] = df['et']
    else:
        # Inc. runoff proportional to SCS equation, find equality factor
        minerror_f = minimize_scalar(incremental_runoff_calculation,
                                     bounds=incrunoff_propfactor_bounds,
                                     args=(df, infz,
                                           tolerance_monthly_greenpx, True),
                                     method='bounded')
        # Runoff calculations
        df = incremental_runoff_calculation(minerror_f.x, df, infz,
                                            tolerance_monthly_greenpx,
                                            False)
        # if delta_Qsw + row['delta_perc'] >= supply_value and
        # delta_Qsw < 0, that means Qsw is very small ~ 0
        df['delta_Qsw'] = df['delta_Qsw'].apply(pos_func, 'columns')
        # If negative supply or inc. runoff, assume default water use eff.
#        maski = (df['supply'] < 0) | (df['delta_Qsw'] +
#                                       df['delta_perc'] > df['supply'])
#        if np.any(maski):
##            df['Qsw'][maski] = df['Qsw_green'][maski] + \
##                df['delta_Qsw'][maski]
##            df['Qgw'] = baseflow_calculation(np.array(df['Qsw']),
##                                             baseflow_filter, qratio)
##            df['eff'][maski] = default_eff
##            df['supply'][maski] = (1/(1 - default_eff)) * (
##                df['delta_Qsw'][maski] + df['delta_perc'][maski])
#            df['eff'][maski] = default_eff         
#            df['supply'][maski] = 1/default_eff * df['et_blue'][maski]
#            df['delta_perc'][maski] = df['supply'][maski] * (1-default_eff) - \
#                df['delta_Qsw'][maski]
##            df['delta_Qsw'][maski] = df['supply'][maski] * (1-default_eff) - \
##                df['delta_perc'][maski]
#            df['Qsw'][maski] = df['Qsw_green'][maski] + \
#                df['delta_Qsw'][maski]
#            df['perc'][maski] = df['perc_green'][maski] + \
#                df['delta_perc'][maski]
#            maskj = (df['delta_perc'] <= 0)
#            if np.any(maskj):
#                df['delta_Qsw'][maskj] = 0
#                df['delta_perc'][maskj] = df['supply'][maskj] * (1-default_eff)
#                df['Qsw'][maskj] = df['Qsw_green'][maskj] + \
#                    df['delta_Qsw'][maskj]
#                df['perc'][maskj] = df['perc_green'][maskj] + \
#                    df['delta_perc'][maskj] 
        df['Qgw'] = baseflow_calculation(np.array(df['Qsw_green']),
                                             baseflow_filter, qratio)
    # Return data frame
    return df


def incremental_runoff_calculation(factor, df, infz,
                                   tolerance_monthly_greenpx,
                                   return_error):
    '''
    Calculate incremental runoff due water supply.
    '''
    rainfed = 1
    # Loop through months
    for index, row in df.iterrows():
        # Check for months without supply
        if row['et'] - row['et_green'] < tolerance_monthly_greenpx:
            # No supply
            df.set_value(index, 'delta_Qsw', 0.0)
            df.set_value(index, 'Qsw', row['Qsw_green'])
            df.set_value(index, 'Qgw', row['Qgw_green'])
            df.set_value(index, 'supply', 0)
            df.set_value(index, 'eff', -9999)
            df.set_value(index, 'et_green', row['et']) # cmi001
            df.set_value(index, 'et_blue', 0) # cmi001
        else:
            # Supply and incremental surface runoff
            delta_Qsw_func = lambda delta_Qsw_value: delta_Qsw_value - factor*(
                row['p'] - row['et'] - row['perc'] -
                row['Qsw_green'] - delta_Qsw_value)**2 / (
                    -(row['p'] - row['et'] - row['perc'] -
                      row['Qsw_green'] - delta_Qsw_value) +
                    infz*(row['thetasat'] - row['theta0']))
            delta_Qsw = max(0, fsolve(delta_Qsw_func, 0.0))
            delta_perc = row['delta_perc']
#            supply_value = max(row['et_blue']+ delta_Qsw + delta_perc,
#                               -(row['p'] - row['et'] - row['perc'] -
#                                 row['Qsw_green'] - delta_Qsw - row['dsm']))
            supply_value = row['et_blue']+ delta_Qsw + delta_perc
            supply_value_wb = -(row['p'] - row['et'] - row['perc'] -
                                 row['Qsw_green'] - delta_Qsw - row['dsm'])
            green_perc_err = supply_value - supply_value_wb
            new_perc_green = max(row['perc_green'] + green_perc_err,0)
#            new_perc_green[np.where(new_perc_green<0)] = 0
            new_perc = new_perc_green + delta_perc
#            supply_value = (row['et_blue']+ delta_Qsw + delta_perc)
#            supply_diff = row['et_blue']+ delta_Qsw + delta_perc + (
#                    row['p'] - row['et'] - row['perc'] -
#                    row['Qsw_green'] - delta_Qsw - row['dsm'])
#
#            supply_value = max(row['et_blue'],
#                               -(row['p'] - row['et'] - row['perc'] -
#                                 row['Qsw_green'] - delta_Qsw))
            # Calculation
            
            eff = (supply_value - delta_Qsw - delta_perc)/supply_value
            # Compute values
            Qsw = row['Qsw_green'] + delta_Qsw
            # If Qsw used instead of Qsw_green the values of Qgw are very large
#            Qgw = row['Qsw_green'] / row['qratio'] - row['Qsw_green']
            # Save values
            df.set_value(index, 'delta_Qsw', delta_Qsw)
            df.set_value(index, 'Qsw', Qsw)
#            df.set_value(index, 'Qgw', Qgw)
            df.set_value(index, 'supply', supply_value)
            df.set_value(index, 'eff', eff)
            df.set_value(index, 'perc_green', new_perc_green)
            df.set_value(index, 'perc', new_perc)
            rainfed = 0
    # Store rainfed value
    df['rainfed'] = rainfed
    # Error calculation
    error = (sum(df['delta_Qsw']) - sum(df['qratio']*df['supply']) -
             sum(df['qratio']*(df['p'] - df['et'] - df['dsm'])) -
             sum(df['Qsw_green'])) ** 2

    # Return error or data frame
    if return_error:
        return abs(error)
    else:
        return df


def lai_and_soil_calculations(df, thetasat, rootdepth):
    '''
    Calculate thetasat, lai, and soil moisture parameters
    '''
    # Thetasat and soil moisture
    df['thetasat'] = thetasat
    df['lai'] = df['lai'].apply(zeros_and_negatives, 'columns')
    df['lai_0'] = df['lai'].fillna(0)
    # Soil moisture calculations
    df['theta0'] = thetasat * df['swi']/100.0
    df['thetao'] = thetasat * df['swio']/100.0
    df['thetax'] = thetasat * df['swix']/100.0
    # Argument for exponential function
    df['exp_arg'] = df.apply(lambda row: exp_arg_func(row['theta0'],
                                                      row['thetasat'],
                                                      row['lai_0']),
                             'columns')
    df['exp_argo'] = df.apply(lambda row: exp_arg_func(row['thetao'],
                                                       row['thetasat'],
                                                       row['lai_0']),
                              'columns')
    df['exp_argx'] = df.apply(lambda row: exp_arg_func(row['thetax'],
                                                       row['thetasat'],
                                                       row['lai_0']),
                              'columns')
    # Soil moisture values - root zone
    df['thetarz'] = (0.1*df['lai_0'] +
                     (1-0.1*df['lai_0']) * (df['exp_arg']))*df['thetasat']
    df['thetarzo'] = (0.1*df['lai_0'] +
                      (1-0.1*df['lai_0']) * (df['exp_argo']))*df['thetasat']
    df['thetarzx'] = (0.1*df['lai_0'] +
                      (1-0.1*df['lai_0']) * (df['exp_argx']))*df['thetasat']
    # Change in storage
    df['dsm'] = rootdepth*(df['thetarzx'] - df['thetarzo'])
    return df


def veg_int_calc(df):
    '''
    Calculate vegetation cover, interception, and (P - I)^2
    '''
    # Vegetation cover
    df['vc'] = df['lai'].apply(vc_func, 'columns')
    # Interception
    df['interception'] = df.apply(lambda row:
                                  interc_func(row['p'], row['rainydays'],
                                              row['lai'],
                                              row['vc']), 'columns')
    # Squared term
    df['P_Int_2'] = (df['p'] - df['interception']) ** 2
    # Return data frame
    return df


def return_empty_df_columns(df):
    '''
    Add empty fields for the required headers in the data frame
    '''
    # Columns
    col_names = list(df.columns.values)
    cols = []
    for hvar in ['Qtot', 'Qsw', 'Qgw', 'infz', 'supply',
                 'dsm', 'thetarz', 'perc']:
        if hvar not in col_names:
            cols.append(hvar)
    # Data frame concatenation
    df = pd.concat([df, pd.DataFrame(index=range(12),
                                     columns=cols)],
                   axis=1)
    # Return data frame
    return df


def zeros_and_negatives(val):
    '''
    Replace zeros and negative values to nans
    '''
    if val <= 0:
        return np.nan
    else:
        return val


def vc_func(lai):
    '''
    Calculate the vegetation cover given the leaf area index.
    '''
    value = 1 - exp(-0.55*lai)
    return value


def exp_arg_func(theta0, thetasat, lai):
    '''
    Compute the exponential argument in the calculation of the root depth
    soil moisture.
    '''
    value = 1 - exp((theta0/thetasat) * (-0.5*lai - 1))
    return value


def interc_func(p, rainydays, lai, vc):
    '''
    Calculates the interception
    '''
    if pd.isnull(lai) or rainydays == 0.0:
        value = 0.0
    else:
        value = lai * (1 - 1/(1 + ((p/rainydays*vc)/lai)))*rainydays
    return value


def pos_func(val):
    """
    Force positive values only
    """
    value = max(val, 0)
    return value


def baseflow_calculation(qsw_vector, filter_par, qratio):
    '''
    Calculate the baseflow using the runoff ratio and the surface runoff
    '''
    Qgw_tot = qsw_vector.sum() * (1-qratio)/qratio
    q0 = fsolve(baseflow_function, 0.0, [qsw_vector, filter_par,
                                         qratio, Qgw_tot, True])
    Qgw_vector = baseflow_function(q0, [qsw_vector, filter_par,
                                        qratio, Qgw_tot, False])
    return Qgw_vector


def baseflow_function(q0, args):
    '''
    Balance baseflow values in a yearly basis
    '''
    qsw_vector, filter_par, qratio, Qgw_tot, return_error = args
    q_temp = np.array(12 * [np.nan])
    q_temp[0] = filter_par*q0 + 0.5*(1 + filter_par)*(
        qsw_vector[0] - qsw_vector[-1])
    for i in range(1, 12):
        q_temp[i] = filter_par*q_temp[i-1] + 0.5*(1 + filter_par)*(
            qsw_vector[i] - qsw_vector[i-1])
    # Baseflow
    qgw_vector = (1-qratio)/qratio*(qsw_vector - q_temp)
    # Error calculation
    error = Qgw_tot - qgw_vector.sum()
    # Return error or vector
    if return_error:
        return error
    else:
        return qgw_vector


def replace_with_closest(vector, array, point, time_index):
    '''
    Replace nan values in a vectorwith the mean of the spatially closest values
    '''
    lati, loni = point
    ti1, ti2 = time_index
    counter = 0
    for i in range(ti1, ti2):
        if np.isnan(vector[counter]):
            vector[counter] = get_mean_neighbors(array[i, :, :], (lati, loni),
                                                 False)
        counter += 1
    return vector


def get_mean_neighbors(array, index, include_cell):
    '''
    Calculate the mean cell value from neighboring cells
    '''
    x_i, y_i = index
    n_x, n_y = array.shape
    stay = True
    cells = 1
    while stay:
        neighbors_ls = get_neighbors(x_i, y_i, n_x, n_y, cells)
        if include_cell:
            neighbors_ls = neighbors_ls + [(x_i, y_i)]
        values_ls = [array[i] for i in neighbors_ls]
        if np.isnan(values_ls).all():
            cells += 1
        else:
            value = np.nanmean(values_ls)
            stay = False
    return value


def get_neighbors(x, y, n_x, n_y, cells):
    '''
    Get the indeces of neighboring cells
    '''
    neighbors_ls = [(x_i, y_i)
                    for x_i in range(x - 1 - cells + 1, x + 2 + cells - 1)
                    for y_i in range(y - 1 - cells + 1, y + 2 + cells - 1)
                    if (-1 < x <= n_x - 1 and -1 < y <= n_y - 1 and
                        (x != x_i or y != y_i) and
                        (0 <= x_i <= n_x - 1) and (0 <= y_i <= n_y - 1))]
    return neighbors_ls


def percolation_fit_calculation(rdsm, a, b):
    '''
    Percolation function of root depth soil moisture
    '''
    value = a * rdsm ** b
    return value


def percolation_fit_error(params, rdsm, perc):
    '''
    Error in percolation fit
    '''
    value = (percolation_fit_calculation(rdsm,
                                         params[0], params[1]) - perc) ** 2
    return value


def budyko(phi):
    '''
    Calculate the evaporative index from the dryness index using the
    budyko curve
    '''
    res = np.sqrt(phi*np.tanh(1/phi)*(1-np.exp(-phi)))
    return res


def monthly_reducer(array, periods, nodata_value=-9999):
    '''
    Reduce the size of the yearly array into the input periods
    '''
    array = np.array(array)
    mpp = int(12/periods)
    d, j, k = array.shape
    array[np.isclose(array, nodata_value)] = np.nan
    array_out = np.empty((periods, j, k))
    for i in range(periods):
        i_1 = i*mpp
        i_2 = i*mpp + mpp
        array_out[i] = np.sum(array[i_1:i_2, :, :], axis=0)
    return array_out


def array_interpolation(lon_ls, lat_ls, infz_array_in, min_infz,
                        return_single_value):
    '''
    Interpolate missing values in an array using kriging in R
    '''
    # Replace values smaller than the minimum
    infz_array_in[infz_array_in < min_infz] = np.nan
    # Total values in array
    n_values = np.isfinite(infz_array_in).sum()
    # Load function
    pandas2ri.activate()
    robjects.r('''
                library(gstat)
                library(sp)
                library(automap)
                kriging_interpolation <- function(x_vec, y_vec, values_arr,
                                                  n_values){
                  # Parameters
                  shape <- dim(values_arr)
                  counter <- 1
                  df <- data.frame(X=numeric(n_values),
                                   Y=numeric(n_values),
                                   INFZ=numeric(n_values))
                  # Save values into a data frame
                  for (i in seq(shape[2])) {
                    for (j in seq(shape[1])) {
                      if (is.finite(values_arr[j, i])) {
                        df[counter,] <- c(x_vec[i], y_vec[j], values_arr[j, i])
                        counter <- counter + 1
                      }
                    }
                  }
                  # Grid
                  coordinates(df) = ~X+Y
                  int_grid <- expand.grid(x_vec, y_vec)
                  names(int_grid) <- c("X", "Y")
                  coordinates(int_grid) = ~X+Y
                  gridded(int_grid) = TRUE
                  # Kriging
                  krig_output <- autoKrige(INFZ~1, df, int_grid)
                  # Array
                  values_out <- matrix(krig_output$krige_output$var1.pred,
                                       nrow=length(y_vec),
                                       ncol=length(x_vec),
                                       byrow = TRUE)
                  return(values_out)
                }
                ''')
    kriging_interpolation = robjects.r['kriging_interpolation']
    # Execute kriging function and get array
    r_array = kriging_interpolation(lon_ls, lat_ls, infz_array_in, n_values)
    infz_array_out = np.array(r_array)
    # Return
    if not return_single_value:
        return infz_array_out
    else:
        x, y = return_single_value
        return infz_array_out[y, x]
