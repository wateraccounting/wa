# -*- coding: utf-8 -*-
"""
Authors: Bert Coerver
         UNESCO-IHE 2017
Contact: b.coerver@un-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Sheets/sheet4
"""
import os
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import time
import subprocess

def create_sheet4(basin, period, units, data, output, template=False, tolerance = 0.01):
    """
    Create sheet 4 of the Water Accounting Plus framework.
    
    Parameters
    ----------
    basin : str
        The name of the basin.
    period : str
        The period of analysis.
    units : list
        A list with strings of the units of the data on sheet 4a and 4b
        respectively.
    data : list
        List with two values pointing to csv files that contains the water data. The csv file has to
        follow an specific format. A sample csv is available here:
        https://github.com/wateraccounting/wa/tree/master/Sheets/csv
    output : list
        Filehandles pointing to the jpg files to be created.
    template : list or boolean, optional
        A list with two entries of the svg files of the sheet. False
        uses the standard svg files. Default is False.
    tolerance : float, optional
        Range used when checked if different totals match with eachother.

    Examples
    --------
    >>> from wa.Sheets import *
    >>> create_sheet4(basin='Helmand', period='2007-2011',
                  units = ['km3/yr', 'km3/yr'],
                  data = [r'C:\Sheets\csv\Sample_sheet4_part12.csv',
                          r'C:\Sheets\csv\Sample_sheet4_part12.csv'],
                  output = [r'C:\Sheets\sheet_4_part1.png',
                            r'C:\Sheets\sheet_4_part2.png'])
    """
    # import WA+ modules
    import wa.General.raster_conversions as RC
    
    if data[0] is not None:
        df1 = pd.read_csv(data[0], sep=';')
    if data[1] is not None:
        df2 = pd.read_csv(data[1], sep=';')
    
    # Read csv part 1
    if data[0] is not None:
        p1 = dict()
        p1['sp_r01_c01'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].SUPPLY_SURFACEWATER),
                                   float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].SUPPLY_GROUNDWATER)])
        p1['sp_r02_c01'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].SUPPLY_SURFACEWATER),
                                   float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].SUPPLY_GROUNDWATER)])
        p1['sp_r03_c01'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].SUPPLY_SURFACEWATER),
                                   float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].SUPPLY_GROUNDWATER)])
        p1['sp_r04_c01'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].SUPPLY_SURFACEWATER),
                                   float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].SUPPLY_GROUNDWATER)])
        p1['sp_r05_c01'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].SUPPLY_SURFACEWATER),
                                   float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].SUPPLY_GROUNDWATER)])
        p1['sp_r06_c01'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].SUPPLY_SURFACEWATER),
                                   float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].SUPPLY_GROUNDWATER)])
        p1['sp_r07_c01'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].SUPPLY_SURFACEWATER),
                                   float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].SUPPLY_GROUNDWATER)])
        p1['sp_r08_c01'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Other")].SUPPLY_SURFACEWATER),
                                   float(df1.loc[(df1.LANDUSE_TYPE == "Other")].SUPPLY_GROUNDWATER)])
        
        p1['dm_r01_c01'] = float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].DEMAND)
        p1['dm_r02_c01'] = float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].DEMAND) 
        p1['dm_r03_c01'] = float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].DEMAND) 
        p1['dm_r04_c01'] = float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].DEMAND) 
        p1['dm_r05_c01'] = float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].DEMAND) 
        p1['dm_r06_c01'] = float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].DEMAND) 
        p1['dm_r07_c01'] = float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].DEMAND) 
        p1['dm_r08_c01'] = float(df1.loc[(df1.LANDUSE_TYPE == "Other")].DEMAND)
        
        p1['sp_r01_c02'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].CONSUMED_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].CONSUMED_OTHER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].NON_CONVENTIONAL_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].NON_RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].NON_RECOVERABLE_SURFACEWATER)])
        p1['sp_r02_c02'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].CONSUMED_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].CONSUMED_OTHER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].NON_CONVENTIONAL_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].NON_RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].NON_RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r03_c02'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].CONSUMED_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].CONSUMED_OTHER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].NON_CONVENTIONAL_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].NON_RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].NON_RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r04_c02'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].CONSUMED_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].CONSUMED_OTHER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].NON_CONVENTIONAL_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].NON_RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].NON_RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r05_c02'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].CONSUMED_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].CONSUMED_OTHER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].NON_CONVENTIONAL_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].NON_RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].NON_RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r06_c02'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].CONSUMED_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].CONSUMED_OTHER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].NON_CONVENTIONAL_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].NON_RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].NON_RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r07_c02'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].CONSUMED_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].CONSUMED_OTHER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].NON_CONVENTIONAL_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].NON_RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].NON_RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r08_c02'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Other")].CONSUMED_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Other")].CONSUMED_OTHER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Other")].NON_CONVENTIONAL_ET),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Other")].NON_RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Other")].NON_RECOVERABLE_SURFACEWATER)]) 
    
        p1['sp_r01_c03'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].RECOVERABLE_SURFACEWATER)])
        p1['sp_r02_c03'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r03_c03'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r04_c03'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r05_c03'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r06_c03'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r07_c03'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].RECOVERABLE_SURFACEWATER)]) 
        p1['sp_r08_c03'] = pd.np.sum([float(df1.loc[(df1.LANDUSE_TYPE == "Other")].RECOVERABLE_GROUNDWATER),
                                         float(df1.loc[(df1.LANDUSE_TYPE == "Other")].RECOVERABLE_SURFACEWATER)])
                                                 
        p1['wd_r01_c01'] = pd.np.nansum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].SUPPLY_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].SUPPLY_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].SUPPLY_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].SUPPLY_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].SUPPLY_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].SUPPLY_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].SUPPLY_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Other")].SUPPLY_GROUNDWATER)])
                               
        p1['wd_r02_c01'] = pd.np.nansum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].SUPPLY_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].SUPPLY_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].SUPPLY_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].SUPPLY_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].SUPPLY_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].SUPPLY_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].SUPPLY_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Other")].SUPPLY_SURFACEWATER)])
                               
        p1['wd_r03_c01'] = pd.np.nansum([p1['wd_r01_c01'],p1['wd_r02_c01']])
        
        p1['sp_r01_c04'] = pd.np.nansum([p1['sp_r01_c02'],p1['sp_r02_c02'],p1['sp_r03_c02'],p1['sp_r04_c02'],p1['sp_r05_c02'],p1['sp_r06_c02'],p1['sp_r07_c02'],p1['sp_r08_c02']])
        
        p1['of_r03_c02'] = pd.np.nansum([p1['sp_r01_c03'],p1['sp_r02_c03'],p1['sp_r03_c03'],p1['sp_r04_c03'],p1['sp_r05_c03'],p1['sp_r06_c03'],p1['sp_r07_c03'],p1['sp_r08_c03']])
        
        p1['of_r02_c01'] = pd.np.nansum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Other")].RECOVERABLE_SURFACEWATER)])
                               
        p1['of_r04_c01'] = pd.np.nansum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Other")].RECOVERABLE_GROUNDWATER)])
                               
        p1['of_r03_c01'] = pd.np.nansum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].NON_RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].NON_RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].NON_RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].NON_RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].NON_RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].NON_RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].NON_RECOVERABLE_SURFACEWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Other")].NON_RECOVERABLE_SURFACEWATER)])
                               
        p1['of_r05_c01'] = pd.np.nansum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].NON_RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].NON_RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].NON_RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].NON_RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].NON_RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].NON_RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].NON_RECOVERABLE_GROUNDWATER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Other")].NON_RECOVERABLE_GROUNDWATER)])
                               
        p1['of_r04_c02'] = pd.np.nansum([p1['of_r05_c01'],p1['of_r03_c01']])
        
        p1['sp_r02_c04'] = pd.np.nansum([p1['of_r02_c01'],p1['of_r04_c01']])
        
        p1['of_r09_c02'] = pd.np.nansum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].CONSUMED_OTHER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].CONSUMED_OTHER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].CONSUMED_OTHER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].CONSUMED_OTHER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].CONSUMED_OTHER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].CONSUMED_OTHER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].CONSUMED_OTHER),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Other")].CONSUMED_OTHER)])
    
        p1['of_r02_c02'] = pd.np.nansum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].NON_CONVENTIONAL_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].NON_CONVENTIONAL_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].NON_CONVENTIONAL_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].NON_CONVENTIONAL_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].NON_CONVENTIONAL_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].NON_CONVENTIONAL_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].NON_CONVENTIONAL_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Other")].NON_CONVENTIONAL_ET)])
                               
        p1['of_r01_c02'] = pd.np.nansum([float(df1.loc[(df1.LANDUSE_TYPE == "Irrigated crops")].CONSUMED_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Managed water bodies")].CONSUMED_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Industry")].CONSUMED_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Aquaculture")].CONSUMED_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Residential")].CONSUMED_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Greenhouses")].CONSUMED_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Power and Energy")].CONSUMED_ET),
                               float(df1.loc[(df1.LANDUSE_TYPE == "Other")].CONSUMED_ET)])
                               
        p1['of_r01_c01'] = pd.np.nansum([p1['of_r02_c02'],p1['of_r01_c02']])
    
    # Read csv part 2
    if data[1] is not None:
        p2 = dict()
        p2['sp_r01_c02'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].CONSUMED_ET),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].CONSUMED_OTHER)])
        p2['sp_r02_c02'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].CONSUMED_ET),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].CONSUMED_OTHER)])
        p2['sp_r03_c02'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].CONSUMED_ET),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].CONSUMED_OTHER)])
        p2['sp_r04_c02'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].CONSUMED_ET),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].CONSUMED_OTHER)])
        p2['sp_r05_c02'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].CONSUMED_ET),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].CONSUMED_OTHER)])
        p2['sp_r06_c02'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].CONSUMED_ET),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].CONSUMED_OTHER)])
        p2['sp_r07_c02'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].CONSUMED_ET),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].CONSUMED_OTHER)])
        p2['sp_r08_c02'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].CONSUMED_ET),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].CONSUMED_OTHER)])
        
        p2['sp_r01_c03'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].RECOVERABLE_GROUNDWATER)])
        p2['sp_r02_c03'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].RECOVERABLE_GROUNDWATER)])
        p2['sp_r03_c03'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].RECOVERABLE_GROUNDWATER)])
        p2['sp_r04_c03'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].RECOVERABLE_GROUNDWATER)])
        p2['sp_r05_c03'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].RECOVERABLE_GROUNDWATER)])
        p2['sp_r06_c03'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].RECOVERABLE_GROUNDWATER)])
        p2['sp_r07_c03'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].RECOVERABLE_GROUNDWATER)])
        p2['sp_r08_c03'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].RECOVERABLE_GROUNDWATER)])
        
        p2['sp_r01_c01'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].SUPPLY_GROUNDWATER)])
        p2['sp_r02_c01'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].SUPPLY_GROUNDWATER)])
        p2['sp_r03_c01'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].SUPPLY_GROUNDWATER)])
        p2['sp_r04_c01'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].SUPPLY_GROUNDWATER)])
        p2['sp_r05_c01'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].SUPPLY_GROUNDWATER)])
        p2['sp_r06_c01'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].SUPPLY_GROUNDWATER)])
        p2['sp_r07_c01'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].SUPPLY_GROUNDWATER)])
        p2['sp_r08_c01'] = pd.np.sum([float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].SUPPLY_GROUNDWATER)])
              
        
        p2['dm_r01_c01'] = float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].DEMAND)
        p2['dm_r02_c01'] = float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].DEMAND)
        p2['dm_r03_c01'] = float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].DEMAND)
        p2['dm_r04_c01'] = float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].DEMAND)
        p2['dm_r05_c01'] = float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].DEMAND)
        p2['dm_r06_c01'] = float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].DEMAND)
        p2['dm_r07_c01'] = float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].DEMAND)
        p2['dm_r08_c01'] = float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].DEMAND)
        
        p2['wd_r01_c01'] = pd.np.nansum([float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].SUPPLY_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].SUPPLY_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].SUPPLY_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].SUPPLY_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].SUPPLY_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].SUPPLY_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].SUPPLY_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].SUPPLY_GROUNDWATER)])
        
        p2['wd_r03_c01'] = pd.np.nansum([float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].SUPPLY_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].SUPPLY_SURFACEWATER)])
        
        p2['wd_r02_c01'] = pd.np.nansum([p2['wd_r01_c01'],p2['wd_r03_c01']])
        
        p2['sp_r01_c04'] = pd.np.nansum([p2['sp_r01_c02'],
                                   p2['sp_r02_c02'],
                                   p2['sp_r03_c02'],
                                   p2['sp_r04_c02'],
                                   p2['sp_r05_c02'],
                                   p2['sp_r06_c02'],
                                   p2['sp_r07_c02'],
                                   p2['sp_r08_c02']])
                                   
        p2['of_r03_c02'] = p2['sp_r02_c04'] = pd.np.nansum([p2['sp_r01_c03'],
                                   p2['sp_r02_c03'],
                                   p2['sp_r03_c03'],
                                   p2['sp_r04_c03'],
                                   p2['sp_r05_c03'],
                                   p2['sp_r06_c03'],
                                   p2['sp_r07_c03'],
                                   p2['sp_r08_c03']])
                                   
        p2['of_r01_c01'] = p2['of_r01_c02'] = pd.np.nansum([float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].CONSUMED_ET),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].CONSUMED_ET),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].CONSUMED_ET),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].CONSUMED_ET),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].CONSUMED_ET),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].CONSUMED_ET),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].CONSUMED_ET),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].CONSUMED_ET)])
        
        p2['of_r02_c02'] = pd.np.nansum([float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].CONSUMED_OTHER),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].CONSUMED_OTHER),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].CONSUMED_OTHER),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].CONSUMED_OTHER),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].CONSUMED_OTHER),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].CONSUMED_OTHER),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].CONSUMED_OTHER),
                                                float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].CONSUMED_OTHER)])
        
        
        p2['of_r03_c01'] = pd.np.nansum([float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].RECOVERABLE_SURFACEWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].RECOVERABLE_SURFACEWATER)]) 
        
        p2['of_r02_c01'] = pd.np.nansum([float(df2.loc[(df2.LANDUSE_TYPE == "Forests")].RECOVERABLE_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Shrubland")].RECOVERABLE_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Rainfed Crops")].RECOVERABLE_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Forest Plantations")].RECOVERABLE_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Water Bodies")].RECOVERABLE_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Wetlands")].RECOVERABLE_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Natural Grasslands")].RECOVERABLE_GROUNDWATER),
                                   float(df2.loc[(df2.LANDUSE_TYPE == "Other (Non-Manmade)")].RECOVERABLE_GROUNDWATER)]) 

    # Calculations & modify svgs
    if not template:
        path = os.path.dirname(os.path.abspath(__file__))
        svg_template_path_1 = os.path.join(path, 'svg', 'sheet_4_part1.svg')
        svg_template_path_2 = os.path.join(path, 'svg', 'sheet_4_part2.svg')
    else:
        svg_template_path_1 = os.path.abspath(template[0])
        svg_template_path_2 = os.path.abspath(template[1])
    
    if data[0] is not None:
        tree1 = ET.parse(svg_template_path_1)
        xml_txt_box = tree1.findall('''.//*[@id='basin1']''')[0]
        xml_txt_box.getchildren()[0].text = 'Basin: ' + basin
        
        xml_txt_box = tree1.findall('''.//*[@id='period1']''')[0]
        xml_txt_box.getchildren()[0].text = 'Period: ' + period
        
        xml_txt_box = tree1.findall('''.//*[@id='units1']''')[0]
        xml_txt_box.getchildren()[0].text = 'Part 1: Manmade ({0})'.format(units[0])
        
        for key in p1.keys():
            xml_txt_box = tree1.findall(".//*[@id='{0}']".format(key))[0]
            if not pd.isnull(p1[key]):
                xml_txt_box.getchildren()[0].text = '%.2f' % p1[key]
            else:
                xml_txt_box.getchildren()[0].text = '-'
                
    if data[1] is not None:
        tree2 = ET.parse(svg_template_path_2)
        xml_txt_box = tree2.findall('''.//*[@id='basin2']''')[0]
        xml_txt_box.getchildren()[0].text = 'Basin: ' + basin
        
        xml_txt_box = tree2.findall('''.//*[@id='period2']''')[0]
        xml_txt_box.getchildren()[0].text = 'Period: ' + period
        
        xml_txt_box = tree2.findall('''.//*[@id='units2']''')[0]
        xml_txt_box.getchildren()[0].text = 'Part 2: Natural Landuse ({0})'.format(units[1])
        
        for key in p2.keys():
            xml_txt_box = tree2.findall(".//*[@id='{0}']".format(key))[0]
            if not pd.isnull(p2[key]):
                xml_txt_box.getchildren()[0].text = '%.2f' % p2[key]
            else:
                xml_txt_box.getchildren()[0].text = '-'    

    ET.register_namespace("", "http://www.w3.org/2000/svg")
    
    # Get the paths based on the environment variable
    if os.name == 'posix':
        Path_Inkscape = 'inkscape'
        
    else:
        WA_env_paths = os.environ["WA_PATHS"].split(';')
        Inkscape_env_path = WA_env_paths[1]
        Path_Inkscape = os.path.join(Inkscape_env_path,'inkscape.exe')
    
    
    if data[0] is not None:
        tempout_path = output[0].replace('.pdf', '_temporary.svg')
        tree1.write(tempout_path)
        fullCmd = (' ').join([Path_Inkscape, tempout_path,'--export-pdf='+output[0], '-d 300'])
        RC.Run_command_window(fullCmd)  
        time.sleep(10)
        os.remove(tempout_path)
        
    if data[1] is not None:
        tempout_path = output[1].replace('.pdf', '_temporary.svg')
        tree2.write(tempout_path)
        fullCmd = (' ').join([Path_Inkscape, tempout_path,'--export-pdf='+output[1], '-d 300'])
        RC.Run_command_window(fullCmd)   
        time.sleep(10)
        os.remove(tempout_path)