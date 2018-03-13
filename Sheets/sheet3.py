# -*- coding: utf-8 -*-
"""
Authors: Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Sheets/sheet1
"""

import os
import pandas as pd
import time
import xml.etree.ElementTree as ET
import subprocess

def create_sheet3(basin, period, units, data, output, template=False):
    """

    Keyword arguments:
    basin -- The name of the basin
    period -- The period of analysis
    units -- A list with the units of the data:
             [<water consumption>, <land productivity>, <water productivity>]
    data -- A csv file that contains the water data. The csv file has to
            follow an specific format. A sample csv is available in the link:
            https://github.com/wateraccounting/wa/tree/master/Sheets/csv
    output -- A list (length 2) with the output paths of the jpg files
              for the two parts of the sheet
    template -- A list (length 2) of the svg files of the sheet.
                Use False (default) to use the standard svg files.

    Example:
    from wa.Sheets import *
    create_sheet3(basin='Helmand', period='2007-2011',
                  units=['km3/yr', 'kg/ha/yr', 'kg/m3'],
                  data=[r'C:\Sheets\csv\Sample_sheet3_part1.csv',
                        r'C:\Sheets\csv\Sample_sheet3_part2.csv'],
                  output=[r'C:\Sheets\sheet_3_part1.jpg',
                          r'C:\Sheets\sheet_3_part2.jpg'])
    """

    # Read table

    df1 = pd.read_csv(data[0], sep=';')
    df2 = pd.read_csv(data[1], sep=';')

    # Data frames

    df1c = df1.loc[df1.USE == "CROP"]
    df1n = df1.loc[df1.USE == "NON-CROP"]

    df2c = df2.loc[df2.USE == "CROP"]
    df2n = df2.loc[df2.USE == "NON-CROP"]

    # Read csv file part 1
    crop_r01c01 = float(df1c.loc[(df1c.TYPE == "Cereals") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c01 = float(df1c.loc[(df1c.TYPE == "Cereals") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c01 = float(df1c.loc[(df1c.TYPE == "Cereals") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c01 = crop_r02c01 + crop_r03c01

    crop_r01c02 = float(df1c.loc[(df1c.SUBTYPE == "Root/tuber crops") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c02 = float(df1c.loc[(df1c.SUBTYPE == "Root/tuber crops") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c02 = float(df1c.loc[(df1c.SUBTYPE == "Root/tuber crops") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c02 = crop_r02c02 + crop_r03c02

    crop_r01c03 = float(df1c.loc[(df1c.SUBTYPE == "Leguminous crops") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c03 = float(df1c.loc[(df1c.SUBTYPE == "Leguminous crops") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c03 = float(df1c.loc[(df1c.SUBTYPE == "Leguminous crops") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c03 = crop_r02c03 + crop_r03c03

    crop_r01c04 = float(df1c.loc[(df1c.SUBTYPE == "Sugar crops") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c04 = float(df1c.loc[(df1c.SUBTYPE == "Sugar crops") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c04 = float(df1c.loc[(df1c.SUBTYPE == "Sugar crops") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c04 = crop_r02c04 + crop_r03c04

    crop_r01c05 = float(df1c.loc[(df1c.TYPE == "Non-cereals") &
                        (df1c.SUBCLASS == "ET") &
                        (df1c.SUBTYPE == "Merged")].WATER_CONSUMPTION)
    crop_r02c05 = float(df1c.loc[(df1c.TYPE == "Non-cereals") &
                        (df1c.SUBCLASS == "ET rainfall") &
                        (df1c.SUBTYPE == "Merged")].WATER_CONSUMPTION)
    crop_r03c05 = float(df1c.loc[(df1c.TYPE == "Non-cereals") &
                        (df1c.SUBCLASS == "Incremental ET") &
                        (df1c.SUBTYPE == "Merged")].WATER_CONSUMPTION)
    crop_r04c05 = crop_r02c05 + crop_r03c05

    crop_r01c06 = float(df1c.loc[(df1c.SUBTYPE == "Vegetables & melons") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c06 = float(df1c.loc[(df1c.SUBTYPE == "Vegetables & melons") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c06 = float(df1c.loc[(df1c.SUBTYPE == "Vegetables & melons") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c06 = crop_r02c06 + crop_r03c06

    crop_r01c07 = float(df1c.loc[(df1c.SUBTYPE == "Fruits & nuts") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c07 = float(df1c.loc[(df1c.SUBTYPE == "Fruits & nuts") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c07 = float(df1c.loc[(df1c.SUBTYPE == "Fruits & nuts") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c07 = crop_r02c07 + crop_r03c07

    crop_r01c08 = float(df1c.loc[(df1c.TYPE == "Fruit & vegetables") &
                        (df1c.SUBCLASS == "ET") &
                        (df1c.SUBTYPE == "Merged")].WATER_CONSUMPTION)
    crop_r02c08 = float(df1c.loc[(df1c.TYPE == "Fruit & vegetables") &
                        (df1c.SUBCLASS == "ET rainfall") &
                        (df1c.SUBTYPE == "Merged")].WATER_CONSUMPTION)
    crop_r03c08 = float(df1c.loc[(df1c.TYPE == "Fruit & vegetables") &
                        (df1c.SUBCLASS == "Incremental ET") &
                        (df1c.SUBTYPE == "Merged")].WATER_CONSUMPTION)
    crop_r04c08 = crop_r02c08 + crop_r03c08

    crop_r01c09 = float(df1c.loc[(df1c.TYPE == "Oilseeds") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c09 = float(df1c.loc[(df1c.TYPE == "Oilseeds") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c09 = float(df1c.loc[(df1c.TYPE == "Oilseeds") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c09 = crop_r02c09 + crop_r03c09

    crop_r01c10 = float(df1c.loc[(df1c.TYPE == "Feed crops") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c10 = float(df1c.loc[(df1c.TYPE == "Feed crops") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c10 = float(df1c.loc[(df1c.TYPE == "Feed crops") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c10 = crop_r02c10 + crop_r03c10

    crop_r01c11 = float(df1c.loc[(df1c.TYPE == "Beverage crops") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c11 = float(df1c.loc[(df1c.TYPE == "Beverage crops") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c11 = float(df1c.loc[(df1c.TYPE == "Beverage crops") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c11 = crop_r02c11 + crop_r03c11

    crop_r01c12 = float(df1c.loc[(df1c.TYPE == "Other crops") &
                        (df1c.SUBCLASS == "ET")].WATER_CONSUMPTION)
    crop_r02c12 = float(df1c.loc[(df1c.TYPE == "Other crops") &
                        (df1c.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    crop_r03c12 = float(df1c.loc[(df1c.TYPE == "Other crops") &
                        (df1c.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    crop_r04c12 = crop_r02c12 + crop_r03c12

    noncrop_r01c01 = float(df1n.loc[(df1n.TYPE == "Fish (Aquaculture)") &
                           (df1n.SUBCLASS == "ET")].WATER_CONSUMPTION)
    noncrop_r02c01 = float(df1n.loc[(df1n.TYPE == "Fish (Aquaculture)") &
                           (df1n.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    noncrop_r03c01 = float(df1n.loc[(df1n.TYPE == "Fish (Aquaculture)") &
                           (df1n.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    noncrop_r04c01 = noncrop_r02c01 + noncrop_r03c01

    noncrop_r01c02 = float(df1n.loc[(df1n.TYPE == "Timber") &
                           (df1n.SUBCLASS == "ET")].WATER_CONSUMPTION)
    noncrop_r02c02 = float(df1n.loc[(df1n.TYPE == "Timber") &
                           (df1n.SUBCLASS == "ET rainfall")].WATER_CONSUMPTION)
    noncrop_r03c02 = float(df1n.loc[(df1n.TYPE == "Timber") &
                           (df1n.SUBCLASS == "Incremental ET")].WATER_CONSUMPTION)
    noncrop_r04c02 = noncrop_r02c02 + noncrop_r03c02

    crop_r01 = pd.np.nansum([crop_r01c01, crop_r01c02, crop_r01c03,
                             crop_r01c04, crop_r01c05, crop_r01c06,
                             crop_r01c07, crop_r01c08, crop_r01c09,
                             crop_r01c10, crop_r01c11, crop_r01c12])

    crop_r02 = pd.np.nansum([crop_r02c01, crop_r02c02, crop_r02c03,
                             crop_r02c04, crop_r02c05, crop_r02c06,
                             crop_r02c07, crop_r02c08, crop_r02c09,
                             crop_r02c10, crop_r02c11, crop_r02c12])

    crop_r03 = pd.np.nansum([crop_r03c01, crop_r03c02, crop_r03c03,
                             crop_r03c04, crop_r03c05, crop_r03c06,
                             crop_r03c07, crop_r03c08, crop_r03c09,
                             crop_r03c10, crop_r03c11, crop_r03c12])

    crop_r04 = crop_r02 + crop_r03

    noncrop_r01 = pd.np.nansum([noncrop_r01c01, noncrop_r01c02])

    noncrop_r02 = pd.np.nansum([noncrop_r02c01, noncrop_r02c02])

    noncrop_r03 = pd.np.nansum([noncrop_r03c01, noncrop_r03c02])

    noncrop_r04 = noncrop_r02 + noncrop_r03

    ag_water_cons = crop_r01 + crop_r04 + noncrop_r01 + noncrop_r04

    # Read csv file part 2
    # Land productivity
    lp_r01c01 = float(df2c.loc[(df2c.TYPE == "Cereals") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c01 = float(df2c.loc[(df2c.TYPE == "Cereals") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c01 = float(df2c.loc[(df2c.TYPE == "Cereals") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c01 = float(df2c.loc[(df2c.TYPE == "Cereals") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r01c02 = float(df2c.loc[(df2c.SUBTYPE == "Root/tuber crops") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c02 = float(df2c.loc[(df2c.SUBTYPE == "Root/tuber crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c02 = float(df2c.loc[(df2c.SUBTYPE == "Root/tuber crops") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c02 = float(df2c.loc[(df2c.SUBTYPE == "Root/tuber crops") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r01c03 = float(df2c.loc[(df2c.SUBTYPE == "Leguminous crops") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c03 = float(df2c.loc[(df2c.SUBTYPE == "Leguminous crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c03 = float(df2c.loc[(df2c.SUBTYPE == "Leguminous crops") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c03 = float(df2c.loc[(df2c.SUBTYPE == "Leguminous crops") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r01c04 = float(df2c.loc[(df2c.SUBTYPE == "Sugar crops") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c04 = float(df2c.loc[(df2c.SUBTYPE == "Sugar crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c04 = float(df2c.loc[(df2c.SUBTYPE == "Sugar crops") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c04 = float(df2c.loc[(df2c.SUBTYPE == "Sugar crops") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r01c05 = float(df2c.loc[(df2c.TYPE == "Non-cereals") &
                      (df2c.SUBCLASS == "Yield") &
                      (df2c.SUBTYPE == "Merged")].LAND_PRODUCTIVITY)
    lp_r02c05 = float(df2c.loc[(df2c.TYPE == "Non-cereals") &
                      (df2c.SUBCLASS == "Yield rainfall") &
                      (df2c.SUBTYPE == "Merged")].LAND_PRODUCTIVITY)
    lp_r03c05 = float(df2c.loc[(df2c.TYPE == "Non-cereals") &
                      (df2c.SUBCLASS == "Incremental yield") &
                      (df2c.SUBTYPE == "Merged")].LAND_PRODUCTIVITY)
    lp_r04c05 = float(df2c.loc[(df2c.TYPE == "Non-cereals") &
                      (df2c.SUBCLASS == "Total yield") &
                      (df2c.SUBTYPE == "Merged")].LAND_PRODUCTIVITY)

    lp_r01c06 = float(df2c.loc[(df2c.SUBTYPE == "Vegetables & melons") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c06 = float(df2c.loc[(df2c.SUBTYPE == "Vegetables & melons") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c06 = float(df2c.loc[(df2c.SUBTYPE == "Vegetables & melons") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c06 = float(df2c.loc[(df2c.SUBTYPE == "Vegetables & melons") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r01c07 = float(df2c.loc[(df2c.SUBTYPE == "Fruits & nuts") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c07 = float(df2c.loc[(df2c.SUBTYPE == "Fruits & nuts") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c07 = float(df2c.loc[(df2c.SUBTYPE == "Fruits & nuts") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c07 = float(df2c.loc[(df2c.SUBTYPE == "Fruits & nuts") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r01c08 = float(df2c.loc[(df2c.TYPE == "Fruit & vegetables") &
                      (df2c.SUBCLASS == "Yield") &
                      (df2c.SUBTYPE == "Merged")].LAND_PRODUCTIVITY)
    lp_r02c08 = float(df2c.loc[(df2c.TYPE == "Fruit & vegetables") &
                      (df2c.SUBCLASS == "Yield rainfall") &
                      (df2c.SUBTYPE == "Merged")].LAND_PRODUCTIVITY)
    lp_r03c08 = float(df2c.loc[(df2c.TYPE == "Fruit & vegetables") &
                      (df2c.SUBCLASS == "Incremental yield") &
                      (df2c.SUBTYPE == "Merged")].LAND_PRODUCTIVITY)
    lp_r04c08 = float(df2c.loc[(df2c.TYPE == "Fruit & vegetables") &
                      (df2c.SUBCLASS == "Total yield") &
                      (df2c.SUBTYPE == "Merged")].LAND_PRODUCTIVITY)

    lp_r01c09 = float(df2c.loc[(df2c.TYPE == "Oilseeds") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c09 = float(df2c.loc[(df2c.TYPE == "Oilseeds") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c09 = float(df2c.loc[(df2c.TYPE == "Oilseeds") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c09 = float(df2c.loc[(df2c.TYPE == "Oilseeds") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r01c10 = float(df2c.loc[(df2c.TYPE == "Feed crops") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c10 = float(df2c.loc[(df2c.TYPE == "Feed crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c10 = float(df2c.loc[(df2c.TYPE == "Feed crops") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c10 = float(df2c.loc[(df2c.TYPE == "Feed crops") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r01c11 = float(df2c.loc[(df2c.TYPE == "Beverage crops") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c11 = float(df2c.loc[(df2c.TYPE == "Beverage crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c11 = float(df2c.loc[(df2c.TYPE == "Beverage crops") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c11 = float(df2c.loc[(df2c.TYPE == "Beverage crops") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r01c12 = float(df2c.loc[(df2c.TYPE == "Other crops") &
                      (df2c.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r02c12 = float(df2c.loc[(df2c.TYPE == "Other crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r03c12 = float(df2c.loc[(df2c.TYPE == "Other crops") &
                      (df2c.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r04c12 = float(df2c.loc[(df2c.TYPE == "Other crops") &
                      (df2c.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r05c01 = float(df2n.loc[(df2n.SUBTYPE == "Meat") &
                      (df2n.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r06c01 = float(df2n.loc[(df2n.SUBTYPE == "Meat") &
                      (df2n.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r07c01 = float(df2n.loc[(df2n.SUBTYPE == "Meat") &
                      (df2n.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r08c01 = float(df2n.loc[(df2n.SUBTYPE == "Meat") &
                      (df2n.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r05c02 = float(df2n.loc[(df2n.SUBTYPE == "Milk") &
                      (df2n.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r06c02 = float(df2n.loc[(df2n.SUBTYPE == "Milk") &
                      (df2n.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r07c02 = float(df2n.loc[(df2n.SUBTYPE == "Milk") &
                      (df2n.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r08c02 = float(df2n.loc[(df2n.SUBTYPE == "Milk") &
                      (df2n.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r05c03 = float(df2n.loc[(df2n.TYPE == "Fish (Aquaculture)") &
                      (df2n.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r06c03 = float(df2n.loc[(df2n.TYPE == "Fish (Aquaculture)") &
                      (df2n.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r07c03 = float(df2n.loc[(df2n.TYPE == "Fish (Aquaculture)") &
                      (df2n.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r08c03 = float(df2n.loc[(df2n.TYPE == "Fish (Aquaculture)") &
                      (df2n.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    lp_r05c04 = float(df2n.loc[(df2n.TYPE == "Timber") &
                      (df2n.SUBCLASS == "Yield")].LAND_PRODUCTIVITY)
    lp_r06c04 = float(df2n.loc[(df2n.TYPE == "Timber") &
                      (df2n.SUBCLASS == "Yield rainfall")].LAND_PRODUCTIVITY)
    lp_r07c04 = float(df2n.loc[(df2n.TYPE == "Timber") &
                      (df2n.SUBCLASS == "Incremental yield")].LAND_PRODUCTIVITY)
    lp_r08c04 = float(df2n.loc[(df2n.TYPE == "Timber") &
                      (df2n.SUBCLASS == "Total yield")].LAND_PRODUCTIVITY)

    # Water productivity
    wp_r01c01 = float(df2c.loc[(df2c.TYPE == "Cereals") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c01 = float(df2c.loc[(df2c.TYPE == "Cereals") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c01 = float(df2c.loc[(df2c.TYPE == "Cereals") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c01 = float(df2c.loc[(df2c.TYPE == "Cereals") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r01c02 = float(df2c.loc[(df2c.SUBTYPE == "Root/tuber crops") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c02 = float(df2c.loc[(df2c.SUBTYPE == "Root/tuber crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c02 = float(df2c.loc[(df2c.SUBTYPE == "Root/tuber crops") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c02 = float(df2c.loc[(df2c.SUBTYPE == "Root/tuber crops") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r01c03 = float(df2c.loc[(df2c.SUBTYPE == "Leguminous crops") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c03 = float(df2c.loc[(df2c.SUBTYPE == "Leguminous crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c03 = float(df2c.loc[(df2c.SUBTYPE == "Leguminous crops") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c03 = float(df2c.loc[(df2c.SUBTYPE == "Leguminous crops") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)
    
    wp_r01c04 = float(df2c.loc[(df2c.SUBTYPE == "Sugar crops") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c04 = float(df2c.loc[(df2c.SUBTYPE == "Sugar crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c04 = float(df2c.loc[(df2c.SUBTYPE == "Sugar crops") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c04 = float(df2c.loc[(df2c.SUBTYPE == "Sugar crops") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r01c05 = float(df2c.loc[(df2c.TYPE == "Non-cereals") &
                      (df2c.SUBCLASS == "Yield") &
                      (df2c.SUBTYPE == "Merged")].WATER_PRODUCTIVITY)
    wp_r02c05 = float(df2c.loc[(df2c.TYPE == "Non-cereals") &
                      (df2c.SUBCLASS == "Yield rainfall") &
                      (df2c.SUBTYPE == "Merged")].WATER_PRODUCTIVITY)
    wp_r03c05 = float(df2c.loc[(df2c.TYPE == "Non-cereals") &
                      (df2c.SUBCLASS == "Incremental yield") &
                      (df2c.SUBTYPE == "Merged")].WATER_PRODUCTIVITY)
    wp_r04c05 = float(df2c.loc[(df2c.TYPE == "Non-cereals") &
                      (df2c.SUBCLASS == "Total yield") &
                      (df2c.SUBTYPE == "Merged")].WATER_PRODUCTIVITY)

    wp_r01c06 = float(df2c.loc[(df2c.SUBTYPE == "Vegetables & melons") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c06 = float(df2c.loc[(df2c.SUBTYPE == "Vegetables & melons") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c06 = float(df2c.loc[(df2c.SUBTYPE == "Vegetables & melons") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c06 = float(df2c.loc[(df2c.SUBTYPE == "Vegetables & melons") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r01c07 = float(df2c.loc[(df2c.SUBTYPE == "Fruits & nuts") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c07 = float(df2c.loc[(df2c.SUBTYPE == "Fruits & nuts") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c07 = float(df2c.loc[(df2c.SUBTYPE == "Fruits & nuts") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c07 = float(df2c.loc[(df2c.SUBTYPE == "Fruits & nuts") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r01c08 = float(df2c.loc[(df2c.TYPE == "Fruit & vegetables") &
                      (df2c.SUBCLASS == "Yield") &
                      (df2c.SUBTYPE == "Merged")].WATER_PRODUCTIVITY)
    wp_r02c08 = float(df2c.loc[(df2c.TYPE == "Fruit & vegetables") &
                      (df2c.SUBCLASS == "Yield rainfall") &
                      (df2c.SUBTYPE == "Merged")].WATER_PRODUCTIVITY)
    wp_r03c08 = float(df2c.loc[(df2c.TYPE == "Fruit & vegetables") &
                      (df2c.SUBCLASS == "Incremental yield") &
                      (df2c.SUBTYPE == "Merged")].WATER_PRODUCTIVITY)
    wp_r04c08 = float(df2c.loc[(df2c.TYPE == "Fruit & vegetables") &
                      (df2c.SUBCLASS == "Total yield") &
                      (df2c.SUBTYPE == "Merged")].WATER_PRODUCTIVITY)

    wp_r01c09 = float(df2c.loc[(df2c.TYPE == "Oilseeds") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c09 = float(df2c.loc[(df2c.TYPE == "Oilseeds") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c09 = float(df2c.loc[(df2c.TYPE == "Oilseeds") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c09 = float(df2c.loc[(df2c.TYPE == "Oilseeds") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r01c10 = float(df2c.loc[(df2c.TYPE == "Feed crops") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c10 = float(df2c.loc[(df2c.TYPE == "Feed crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c10 = float(df2c.loc[(df2c.TYPE == "Feed crops") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c10 = float(df2c.loc[(df2c.TYPE == "Feed crops") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r01c11 = float(df2c.loc[(df2c.TYPE == "Beverage crops") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c11 = float(df2c.loc[(df2c.TYPE == "Beverage crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c11 = float(df2c.loc[(df2c.TYPE == "Beverage crops") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c11 = float(df2c.loc[(df2c.TYPE == "Beverage crops") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r01c12 = float(df2c.loc[(df2c.TYPE == "Other crops") &
                      (df2c.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r02c12 = float(df2c.loc[(df2c.TYPE == "Other crops") &
                      (df2c.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r03c12 = float(df2c.loc[(df2c.TYPE == "Other crops") &
                      (df2c.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r04c12 = float(df2c.loc[(df2c.TYPE == "Other crops") &
                      (df2c.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r05c01 = float(df2n.loc[(df2n.SUBTYPE == "Meat") &
                      (df2n.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r06c01 = float(df2n.loc[(df2n.SUBTYPE == "Meat") &
                      (df2n.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r07c01 = float(df2n.loc[(df2n.SUBTYPE == "Meat") &
                      (df2n.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r08c01 = float(df2n.loc[(df2n.SUBTYPE == "Meat") &
                      (df2n.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r05c02 = float(df2n.loc[(df2n.SUBTYPE == "Milk") &
                      (df2n.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r06c02 = float(df2n.loc[(df2n.SUBTYPE == "Milk") &
                      (df2n.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r07c02 = float(df2n.loc[(df2n.SUBTYPE == "Milk") &
                      (df2n.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r08c02 = float(df2n.loc[(df2n.SUBTYPE == "Milk") &
                      (df2n.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r05c03 = float(df2n.loc[(df2n.TYPE == "Fish (Aquaculture)") &
                      (df2n.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r06c03 = float(df2n.loc[(df2n.TYPE == "Fish (Aquaculture)") &
                      (df2n.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r07c03 = float(df2n.loc[(df2n.TYPE == "Fish (Aquaculture)") &
                      (df2n.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r08c03 = float(df2n.loc[(df2n.TYPE == "Fish (Aquaculture)") &
                      (df2n.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    wp_r05c04 = float(df2n.loc[(df2n.TYPE == "Timber") &
                      (df2n.SUBCLASS == "Yield")].WATER_PRODUCTIVITY)
    wp_r06c04 = float(df2n.loc[(df2n.TYPE == "Timber") &
                      (df2n.SUBCLASS == "Yield rainfall")].WATER_PRODUCTIVITY)
    wp_r07c04 = float(df2n.loc[(df2n.TYPE == "Timber") &
                      (df2n.SUBCLASS == "Incremental yield")].WATER_PRODUCTIVITY)
    wp_r08c04 = float(df2n.loc[(df2n.TYPE == "Timber") &
                      (df2n.SUBCLASS == "Total yield")].WATER_PRODUCTIVITY)

    # Calculations & modify svgs
    if not template:
        path = os.path.dirname(os.path.abspath(__file__))
        svg_template_path_1 = os.path.join(path, 'svg', 'sheet_3_part1.svg')
        svg_template_path_2 = os.path.join(path, 'svg', 'sheet_3_part2.svg')
    else:
        svg_template_path_1 = os.path.abspath(template[0])
        svg_template_path_2 = os.path.abspath(template[1])

    tree1 = ET.parse(svg_template_path_1)
    tree2 = ET.parse(svg_template_path_2)
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Titles

    xml_txt_box = tree1.findall('''.//*[@id='basin']''')[0]
    xml_txt_box.getchildren()[0].text = 'Basin: ' + basin

    xml_txt_box = tree1.findall('''.//*[@id='period']''')[0]
    xml_txt_box.getchildren()[0].text = 'Period: ' + period

    xml_txt_box = tree1.findall('''.//*[@id='units']''')[0]
    xml_txt_box.getchildren()[0].text = 'Part 1: Agricultural water consumption (' + units[0] + ')'

    xml_txt_box = tree2.findall('''.//*[@id='basin2']''')[0]
    xml_txt_box.getchildren()[0].text = 'Basin: ' + basin

    xml_txt_box = tree2.findall('''.//*[@id='period2']''')[0]
    xml_txt_box.getchildren()[0].text = 'Period: ' + period

    xml_txt_box = tree2.findall('''.//*[@id='units2']''')[0]
    xml_txt_box.getchildren()[0].text = 'Part 2: Land productivity (' + units[1] + ') and water productivity (' + units[2] + ')'

    # Part 1
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c01']''')[0]
    if not pd.isnull(crop_r01c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c02']''')[0]
    if not pd.isnull(crop_r01c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c03']''')[0]
    if not pd.isnull(crop_r01c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c04']''')[0]
    if not pd.isnull(crop_r01c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c05']''')[0]
    if not pd.isnull(crop_r01c05):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c06']''')[0]
    if not pd.isnull(crop_r01c06):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c07']''')[0]
    if not pd.isnull(crop_r01c07):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c08']''')[0]
    if not pd.isnull(crop_r01c08):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c09']''')[0]
    if not pd.isnull(crop_r01c09):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c10']''')[0]
    if not pd.isnull(crop_r01c10):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c11']''')[0]
    if not pd.isnull(crop_r01c11):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01c12']''')[0]
    if not pd.isnull(crop_r01c12):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r01']''')[0]
    if not pd.isnull(crop_r01):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c01']''')[0]
    if not pd.isnull(crop_r02c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c02']''')[0]
    if not pd.isnull(crop_r02c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c03']''')[0]
    if not pd.isnull(crop_r02c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c04']''')[0]
    if not pd.isnull(crop_r02c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c05']''')[0]
    if not pd.isnull(crop_r02c05):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c06']''')[0]
    if not pd.isnull(crop_r02c06):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c07']''')[0]
    if not pd.isnull(crop_r02c07):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c08']''')[0]
    if not pd.isnull(crop_r02c08):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c09']''')[0]
    if not pd.isnull(crop_r02c09):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c10']''')[0]
    if not pd.isnull(crop_r02c10):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c11']''')[0]
    if not pd.isnull(crop_r02c11):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02c12']''')[0]
    if not pd.isnull(crop_r02c12):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r02']''')[0]
    if not pd.isnull(crop_r02):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c01']''')[0]
    if not pd.isnull(crop_r03c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c02']''')[0]
    if not pd.isnull(crop_r03c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c03']''')[0]
    if not pd.isnull(crop_r03c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c04']''')[0]
    if not pd.isnull(crop_r03c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c05']''')[0]
    if not pd.isnull(crop_r03c05):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c06']''')[0]
    if not pd.isnull(crop_r03c06):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c07']''')[0]
    if not pd.isnull(crop_r03c07):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c08']''')[0]
    if not pd.isnull(crop_r03c08):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c09']''')[0]
    if not pd.isnull(crop_r03c09):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c10']''')[0]
    if not pd.isnull(crop_r03c10):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c11']''')[0]
    if not pd.isnull(crop_r03c11):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03c12']''')[0]
    if not pd.isnull(crop_r03c12):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r03']''')[0]
    if not pd.isnull(crop_r03):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c01']''')[0]
    if not pd.isnull(crop_r04c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c02']''')[0]
    if not pd.isnull(crop_r04c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c03']''')[0]
    if not pd.isnull(crop_r04c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c04']''')[0]
    if not pd.isnull(crop_r04c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c05']''')[0]
    if not pd.isnull(crop_r04c05):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c06']''')[0]
    if not pd.isnull(crop_r04c06):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c07']''')[0]
    if not pd.isnull(crop_r04c07):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c08']''')[0]
    if not pd.isnull(crop_r04c08):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c09']''')[0]
    if not pd.isnull(crop_r04c09):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c10']''')[0]
    if not pd.isnull(crop_r04c10):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c11']''')[0]
    if not pd.isnull(crop_r04c11):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04c12']''')[0]
    if not pd.isnull(crop_r04c12):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='crop_r04']''')[0]
    if not pd.isnull(crop_r04):
        xml_txt_box.getchildren()[0].text = '%.2f' % crop_r04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r01c01']''')[0]
    if not pd.isnull(noncrop_r01c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r01c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r01c02']''')[0]
    if not pd.isnull(noncrop_r01c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r01c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r01']''')[0]
    if not pd.isnull(noncrop_r01) and noncrop_r01 > 0.001:
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r02c01']''')[0]
    if not pd.isnull(noncrop_r02c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r02c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r02c02']''')[0]
    if not pd.isnull(noncrop_r02c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r02c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r02']''')[0]
    if not pd.isnull(noncrop_r02) and noncrop_r02 > 0.001:
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r03c01']''')[0]
    if not pd.isnull(noncrop_r03c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r03c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r03c02']''')[0]
    if not pd.isnull(noncrop_r03c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r03c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r03']''')[0]
    if not pd.isnull(noncrop_r03) and noncrop_r03 > 0.001:
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r04c01']''')[0]
    if not pd.isnull(noncrop_r04c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r04c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r04c02']''')[0]
    if not pd.isnull(noncrop_r04c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r04c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree1.findall('''.//*[@id='noncrop_r04']''')[0]
    if not pd.isnull(noncrop_r04) and noncrop_r04 > 0.001:
        xml_txt_box.getchildren()[0].text = '%.2f' % noncrop_r04
    else:
        xml_txt_box.getchildren()[0].text = '-'

    # Part 2
    xml_txt_box = tree1.findall('''.//*[@id='ag_water_cons']''')[0]
    if not pd.isnull(ag_water_cons):
        xml_txt_box.getchildren()[0].text = '%.2f' % ag_water_cons
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c01']''')[0]
    if not pd.isnull(lp_r01c01):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c02']''')[0]
    if not pd.isnull(lp_r01c02):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c03']''')[0]
    if not pd.isnull(lp_r01c03):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c04']''')[0]
    if not pd.isnull(lp_r01c04):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c05']''')[0]
    if not pd.isnull(lp_r01c05):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c06']''')[0]
    if not pd.isnull(lp_r01c06):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c07']''')[0]
    if not pd.isnull(lp_r01c07):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c08']''')[0]
    if not pd.isnull(lp_r01c08):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c09']''')[0]
    if not pd.isnull(lp_r01c09):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c10']''')[0]
    if not pd.isnull(lp_r01c10):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c11']''')[0]
    if not pd.isnull(lp_r01c11):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r01c12']''')[0]
    if not pd.isnull(lp_r01c12):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r01c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c01']''')[0]
    if not pd.isnull(lp_r02c01):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c02']''')[0]
    if not pd.isnull(lp_r02c02):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c03']''')[0]
    if not pd.isnull(lp_r02c03):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c04']''')[0]
    if not pd.isnull(lp_r02c04):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c05']''')[0]
    if not pd.isnull(lp_r02c05):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c06']''')[0]
    if not pd.isnull(lp_r02c06):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c07']''')[0]
    if not pd.isnull(lp_r02c07):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c08']''')[0]
    if not pd.isnull(lp_r02c08):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c09']''')[0]
    if not pd.isnull(lp_r02c09):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c10']''')[0]
    if not pd.isnull(lp_r02c10):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c11']''')[0]
    if not pd.isnull(lp_r02c11):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r02c12']''')[0]
    if not pd.isnull(lp_r02c12):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r02c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c01']''')[0]
    if not pd.isnull(lp_r03c01):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c02']''')[0]
    if not pd.isnull(lp_r03c02):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c03']''')[0]
    if not pd.isnull(lp_r03c03):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c04']''')[0]
    if not pd.isnull(lp_r03c04):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c05']''')[0]
    if not pd.isnull(lp_r03c05):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c06']''')[0]
    if not pd.isnull(lp_r03c06):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c07']''')[0]
    if not pd.isnull(lp_r03c07):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c08']''')[0]
    if not pd.isnull(lp_r03c08):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c09']''')[0]
    if not pd.isnull(lp_r03c09):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c10']''')[0]
    if not pd.isnull(lp_r03c10):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c11']''')[0]
    if not pd.isnull(lp_r03c11):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r03c12']''')[0]
    if not pd.isnull(lp_r03c12):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r03c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c01']''')[0]
    if not pd.isnull(lp_r04c01):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c02']''')[0]
    if not pd.isnull(lp_r04c02):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c03']''')[0]
    if not pd.isnull(lp_r04c03):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c04']''')[0]
    if not pd.isnull(lp_r04c04):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c05']''')[0]
    if not pd.isnull(lp_r04c05):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c06']''')[0]
    if not pd.isnull(lp_r04c06):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c07']''')[0]
    if not pd.isnull(lp_r04c07):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c08']''')[0]
    if not pd.isnull(lp_r04c08):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c09']''')[0]
    if not pd.isnull(lp_r04c09):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c10']''')[0]
    if not pd.isnull(lp_r04c10):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c11']''')[0]
    if not pd.isnull(lp_r04c11):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r04c12']''')[0]
    if not pd.isnull(lp_r04c12):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r04c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c01']''')[0]
    if not pd.isnull(wp_r01c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c02']''')[0]
    if not pd.isnull(wp_r01c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c03']''')[0]
    if not pd.isnull(wp_r01c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c04']''')[0]
    if not pd.isnull(wp_r01c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c05']''')[0]
    if not pd.isnull(wp_r01c05):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c06']''')[0]
    if not pd.isnull(wp_r01c06):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c07']''')[0]
    if not pd.isnull(wp_r01c07):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c08']''')[0]
    if not pd.isnull(wp_r01c08):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c09']''')[0]
    if not pd.isnull(wp_r01c09):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c10']''')[0]
    if not pd.isnull(wp_r01c10):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c11']''')[0]
    if not pd.isnull(wp_r01c11):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r01c12']''')[0]
    if not pd.isnull(wp_r01c12):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r01c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c01']''')[0]
    if not pd.isnull(wp_r02c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c02']''')[0]
    if not pd.isnull(wp_r02c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c03']''')[0]
    if not pd.isnull(wp_r02c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c04']''')[0]
    if not pd.isnull(wp_r02c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c05']''')[0]
    if not pd.isnull(wp_r02c05):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c06']''')[0]
    if not pd.isnull(wp_r02c06):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c07']''')[0]
    if not pd.isnull(wp_r02c07):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c08']''')[0]
    if not pd.isnull(wp_r02c08):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c09']''')[0]
    if not pd.isnull(wp_r02c09):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c10']''')[0]
    if not pd.isnull(wp_r02c10):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c11']''')[0]
    if not pd.isnull(wp_r02c11):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r02c12']''')[0]
    if not pd.isnull(wp_r02c12):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r02c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c01']''')[0]
    if not pd.isnull(wp_r03c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c02']''')[0]
    if not pd.isnull(wp_r03c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c03']''')[0]
    if not pd.isnull(wp_r03c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c04']''')[0]
    if not pd.isnull(wp_r03c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c05']''')[0]
    if not pd.isnull(wp_r03c05):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c06']''')[0]
    if not pd.isnull(wp_r03c06):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c07']''')[0]
    if not pd.isnull(wp_r03c07):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c08']''')[0]
    if not pd.isnull(wp_r03c08):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c09']''')[0]
    if not pd.isnull(wp_r03c09):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c10']''')[0]
    if not pd.isnull(wp_r03c10):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c11']''')[0]
    if not pd.isnull(wp_r03c11):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r03c12']''')[0]
    if not pd.isnull(wp_r03c12):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r03c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c01']''')[0]
    if not pd.isnull(wp_r04c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c02']''')[0]
    if not pd.isnull(wp_r04c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c03']''')[0]
    if not pd.isnull(wp_r04c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c04']''')[0]
    if not pd.isnull(wp_r04c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c05']''')[0]
    if not pd.isnull(wp_r04c05):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c05
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c06']''')[0]
    if not pd.isnull(wp_r04c06):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c06
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c07']''')[0]
    if not pd.isnull(wp_r04c07):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c07
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c08']''')[0]
    if not pd.isnull(wp_r04c08):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c08
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c09']''')[0]
    if not pd.isnull(wp_r04c09):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c09
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c10']''')[0]
    if not pd.isnull(wp_r04c10):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c10
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c11']''')[0]
    if not pd.isnull(wp_r04c11):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c11
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r04c12']''')[0]
    if not pd.isnull(wp_r04c12):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r04c12
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r05c01']''')[0]
    if not pd.isnull(lp_r05c01):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r05c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r05c02']''')[0]
    if not pd.isnull(lp_r05c02):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r05c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r05c03']''')[0]
    if not pd.isnull(lp_r05c03):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r05c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r05c04']''')[0]
    if not pd.isnull(lp_r05c04):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r05c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r06c01']''')[0]
    if not pd.isnull(lp_r06c01):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r06c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r06c02']''')[0]
    if not pd.isnull(lp_r06c02):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r06c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r06c03']''')[0]
    if not pd.isnull(lp_r06c03):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r06c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r06c04']''')[0]
    if not pd.isnull(lp_r06c04):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r06c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r07c01']''')[0]
    if not pd.isnull(lp_r07c01):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r07c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r07c02']''')[0]
    if not pd.isnull(lp_r07c02):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r07c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r07c03']''')[0]
    if not pd.isnull(lp_r07c03):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r07c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r07c04']''')[0]
    if not pd.isnull(lp_r07c04):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r07c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r08c01']''')[0]
    if not pd.isnull(lp_r08c01):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r08c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r08c02']''')[0]
    if not pd.isnull(lp_r08c02):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r08c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r08c03']''')[0]
    if not pd.isnull(lp_r08c03):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r08c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='lp_r08c04']''')[0]
    if not pd.isnull(lp_r08c04):
        xml_txt_box.getchildren()[0].text = '%.0f' % lp_r08c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r05c01']''')[0]
    if not pd.isnull(wp_r05c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r05c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r05c02']''')[0]
    if not pd.isnull(wp_r05c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r05c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r05c03']''')[0]
    if not pd.isnull(wp_r05c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r05c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r05c04']''')[0]
    if not pd.isnull(wp_r05c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r05c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r06c01']''')[0]
    if not pd.isnull(wp_r06c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r06c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r06c02']''')[0]
    if not pd.isnull(wp_r06c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r06c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r06c03']''')[0]
    if not pd.isnull(wp_r06c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r06c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r06c04']''')[0]
    if not pd.isnull(wp_r06c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r06c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r07c01']''')[0]
    if not pd.isnull(wp_r07c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r07c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r07c02']''')[0]
    if not pd.isnull(wp_r07c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r07c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r07c03']''')[0]
    if not pd.isnull(wp_r07c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r07c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r07c04']''')[0]
    if not pd.isnull(wp_r07c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r07c04
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r08c01']''')[0]
    if not pd.isnull(wp_r08c01):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r08c01
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r08c02']''')[0]
    if not pd.isnull(wp_r08c02):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r08c02
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r08c03']''')[0]
    if not pd.isnull(wp_r08c03):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r08c03
    else:
        xml_txt_box.getchildren()[0].text = '-'
    xml_txt_box = tree2.findall('''.//*[@id='wp_r08c04']''')[0]
    if not pd.isnull(wp_r08c04):
        xml_txt_box.getchildren()[0].text = '%.2f' % wp_r08c04
    else:
        xml_txt_box.getchildren()[0].text = '-'

    # svg to string
    ET.register_namespace("", "http://www.w3.org/2000/svg")
#    root1 = tree1.getroot()
#    root2 = tree2.getroot()
#    svg_string1 = ET.tostring(root1, encoding='UTF-8', method='xml')
#    svg_string2 = ET.tostring(root2, encoding='UTF-8', method='xml')

    # Get the paths based on the environment variable
    if os.name == 'posix':
        Path_Inkscape = 'inkscape'
        
    else:
        WA_env_paths = os.environ["WA_PATHS"].split(';')
        Inkscape_env_path = WA_env_paths[1]
        Path_Inkscape = os.path.join(Inkscape_env_path,'inkscape.exe')

    # Export svg to png
    tempout_path = output[0].replace('.pdf', '_temporary.svg')
    tree1.write(tempout_path)
    subprocess.call([Path_Inkscape,tempout_path,'--export-pdf='+output[0], '-d 300'])
    os.remove(tempout_path)
    
        # Export svg to png
    tempout_path = output[1].replace('.pdf', '_temporary.svg')
    tree2.write(tempout_path)
    subprocess.call([Path_Inkscape,tempout_path,'--export-pdf='+output[1], '-d 300'])
    time.sleep(10)
    os.remove(tempout_path)
    
#    # Export svg to png
#    from wand.image import Image
#    img_out1 = Image(blob=svg_string1, resolution=300)
#    img_out1.format = 'jpg'
#    img_out1.save(filename=output[0])
#
#    img_out2 = Image(blob=svg_string2, resolution=300)
#    img_out2.format = 'jpg'
#    img_out2.save(filename=output[1])

    # Return
    return output
