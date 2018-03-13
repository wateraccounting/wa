# -*- coding: utf-8 -*-
"""
Authors: Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Sheets/sheet2
"""

import os
import pandas as pd
import subprocess
import time
import xml.etree.ElementTree as ET


def create_sheet2(basin, period, units, data, output, template=False,
                  tolerance=0.2):
    """

    Keyword arguments:
    basin -- The name of the basin
    period -- The period of analysis
    units -- The units of the data
    data -- A csv file that contains the water data. The csv file has to
            follow an specific format. A sample csv is available in the link:
            https://github.com/wateraccounting/wa/tree/master/Sheets/csv
    output -- The output path of the jpg file for the sheet.
    template -- A svg file of the sheet. Use False (default) to use the
                standard svg file.
    tolerance -- Tolerance (in km3/year) of the difference in total ET
                 measured from (1) evaporation and transpiration and
                 (2) beneficial and non-beneficial ET.

    Example:
    from wa.Sheets import *
    create_sheet2(basin='Nile Basin', period='2010', units='km3/year',
                  data=r'C:\Sheets\csv\Sample_sheet2.csv',
                  output=r'C:\Sheets\sheet_2.jpg')
    """

    # Read table

    df = pd.read_csv(data, sep=';')

    # Data frames

    df_Pr = df.loc[df.LAND_USE == "PROTECTED"]
    df_Ut = df.loc[df.LAND_USE == "UTILIZED"]
    df_Mo = df.loc[df.LAND_USE == "MODIFIED"]
    df_Mc = df.loc[df.LAND_USE == "MANAGED CONVENTIONAL"]
    df_Mn = df.loc[df.LAND_USE == "MANAGED NON_CONVENTIONAL"]

    # Column 1: Transpiration

    c1r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].TRANSPIRATION)
    c1r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].TRANSPIRATION)
    c1r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].TRANSPIRATION)
    c1r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].TRANSPIRATION)
    c1r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].TRANSPIRATION)
    c1r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].TRANSPIRATION)
    c1r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].TRANSPIRATION)
    c1_t1_total = c1r1_t1 + c1r2_t1 + c1r3_t1 + c1r4_t1 + c1r5_t1 + \
        c1r6_t1 + c1r7_t1

    c1r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].TRANSPIRATION)
    c1r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].TRANSPIRATION)
    c1r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].TRANSPIRATION)
    c1r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].TRANSPIRATION)
    c1r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].TRANSPIRATION)
    c1r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].TRANSPIRATION)
    c1_t2_total = c1r1_t2 + c1r2_t2 + c1r3_t2 + c1r4_t2 + c1r5_t2 + c1r6_t2

    c1r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].TRANSPIRATION)
    c1r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].TRANSPIRATION)
    c1r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].TRANSPIRATION)
    c1r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].TRANSPIRATION)
    c1_t3_total = c1r1_t3 + c1r2_t3 + c1r3_t3 + c1r4_t3

    c1r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].TRANSPIRATION)
    c1r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].TRANSPIRATION)
    c1r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].TRANSPIRATION)
    c1r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].TRANSPIRATION)
    c1r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].TRANSPIRATION)
    c1_t4_total = c1r1_t4 + c1r2_t4 + c1r3_t4 + c1r4_t4 + c1r5_t4

    c1r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].TRANSPIRATION)
    c1r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].TRANSPIRATION)
    c1r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].TRANSPIRATION)
    c1r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].TRANSPIRATION)
    c1r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].TRANSPIRATION)
    c1r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].TRANSPIRATION)
    c1_t5_total = c1r1_t5 + c1r2_t5 + c1r3_t5 + c1r4_t5 + c1r5_t5 + c1r6_t5

    # Column 2: Water

    c2r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].WATER)
    c2r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].WATER)
    c2r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].WATER)
    c2r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].WATER)
    c2r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].WATER)
    c2r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].WATER)
    c2r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].WATER)
    c2_t1_total = c2r1_t1 + c2r2_t1 + c2r3_t1 + c2r4_t1 + c2r5_t1 + \
        c2r6_t1 + c2r7_t1

    c2r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].WATER)
    c2r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].WATER)
    c2r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].WATER)
    c2r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].WATER)
    c2r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].WATER)
    c2r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].WATER)
    c2_t2_total = c2r1_t2 + c2r2_t2 + c2r3_t2 + c2r4_t2 + c2r5_t2 + c2r6_t2

    c2r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].WATER)
    c2r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].WATER)
    c2r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].WATER)
    c2r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].WATER)
    c2_t3_total = c2r1_t3 + c2r2_t3 + c2r3_t3 + c2r4_t3

    c2r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].WATER)
    c2r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].WATER)
    c2r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].WATER)
    c2r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].WATER)
    c2r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].WATER)
    c2_t4_total = c2r1_t4 + c2r2_t4 + c2r3_t4 + c2r4_t4 + c2r5_t4

    c2r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].WATER)
    c2r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].WATER)
    c2r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].WATER)
    c2r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].WATER)
    c2r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].WATER)
    c2r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].WATER)
    c2_t5_total = c2r1_t5 + c2r2_t5 + c2r3_t5 + c2r4_t5 + c2r5_t5 + c2r6_t5

    # Column 3: Soil

    c3r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].SOIL)
    c3r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].SOIL)
    c3r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].SOIL)
    c3r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].SOIL)
    c3r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].SOIL)
    c3r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].SOIL)
    c3r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].SOIL)
    c3_t1_total = c3r1_t1 + c3r2_t1 + c3r3_t1 + c3r4_t1 + c3r5_t1 + \
        c3r6_t1 + c3r7_t1

    c3r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].SOIL)
    c3r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].SOIL)
    c3r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].SOIL)
    c3r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].SOIL)
    c3r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].SOIL)
    c3r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].SOIL)
    c3_t2_total = c3r1_t2 + c3r2_t2 + c3r3_t2 + c3r4_t2 + c3r5_t2 + c3r6_t2

    c3r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].SOIL)
    c3r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].SOIL)
    c3r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].SOIL)
    c3r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].SOIL)
    c3_t3_total = c3r1_t3 + c3r2_t3 + c3r3_t3 + c3r4_t3

    c3r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].SOIL)
    c3r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].SOIL)
    c3r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].SOIL)
    c3r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].SOIL)
    c3r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].SOIL)
    c3_t4_total = c3r1_t4 + c3r2_t4 + c3r3_t4 + c3r4_t4 + c3r5_t4

    c3r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].SOIL)
    c3r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].SOIL)
    c3r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].SOIL)
    c3r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].SOIL)
    c3r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].SOIL)
    c3r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].SOIL)
    c3_t5_total = c3r1_t5 + c3r2_t5 + c3r3_t5 + c3r4_t5 + c3r5_t5 + c3r6_t5

    # Column 4: INTERCEPTION

    c4r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].INTERCEPTION)
    c4r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].INTERCEPTION)
    c4r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].INTERCEPTION)
    c4r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].INTERCEPTION)
    c4r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].INTERCEPTION)
    c4r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].INTERCEPTION)
    c4r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].INTERCEPTION)
    c4_t1_total = c4r1_t1 + c4r2_t1 + c4r3_t1 + c4r4_t1 + c4r5_t1 + \
        c4r6_t1 + c4r7_t1

    c4r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].INTERCEPTION)
    c4r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].INTERCEPTION)
    c4r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].INTERCEPTION)
    c4r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].INTERCEPTION)
    c4r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].INTERCEPTION)
    c4r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].INTERCEPTION)
    c4_t2_total = c4r1_t2 + c4r2_t2 + c4r3_t2 + c4r4_t2 + c4r5_t2 + c4r6_t2

    c4r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].INTERCEPTION)
    c4r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].INTERCEPTION)
    c4r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].INTERCEPTION)
    c4r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].INTERCEPTION)
    c4_t3_total = c4r1_t3 + c4r2_t3 + c4r3_t3 + c4r4_t3

    c4r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].INTERCEPTION)
    c4r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].INTERCEPTION)
    c4r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].INTERCEPTION)
    c4r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].INTERCEPTION)
    c4r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].INTERCEPTION)
    c4_t4_total = c4r1_t4 + c4r2_t4 + c4r3_t4 + c4r4_t4 + c4r5_t4

    c4r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].INTERCEPTION)
    c4r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].INTERCEPTION)
    c4r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].INTERCEPTION)
    c4r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].INTERCEPTION)
    c4r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].INTERCEPTION)
    c4r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].INTERCEPTION)
    c4_t5_total = c4r1_t5 + c4r2_t5 + c4r3_t5 + c4r4_t5 + c4r5_t5 + c4r6_t5

    # Column 6: AGRICULTURE

    c6r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].AGRICULTURE)
    c6r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].AGRICULTURE)
    c6r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].AGRICULTURE)
    c6r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].AGRICULTURE)
    c6r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].AGRICULTURE)
    c6r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].AGRICULTURE)
    c6r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].AGRICULTURE)
    c6_t1_total = c6r1_t1 + c6r2_t1 + c6r3_t1 + c6r4_t1 + c6r5_t1 + \
        c6r6_t1 + c6r7_t1

    c6r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].AGRICULTURE)
    c6r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].AGRICULTURE)
    c6r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].AGRICULTURE)
    c6r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].AGRICULTURE)
    c6r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].AGRICULTURE)
    c6r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].AGRICULTURE)
    c6_t2_total = c6r1_t2 + c6r2_t2 + c6r3_t2 + c6r4_t2 + c6r5_t2 + c6r6_t2

    c6r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].AGRICULTURE)
    c6r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].AGRICULTURE)
    c6r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].AGRICULTURE)
    c6r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].AGRICULTURE)
    c6_t3_total = c6r1_t3 + c6r2_t3 + c6r3_t3 + c6r4_t3

    c6r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].AGRICULTURE)
    c6r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].AGRICULTURE)
    c6r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].AGRICULTURE)
    c6r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].AGRICULTURE)
    c6r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].AGRICULTURE)
    c6_t4_total = c6r1_t4 + c6r2_t4 + c6r3_t4 + c6r4_t4 + c6r5_t4

    c6r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].AGRICULTURE)
    c6r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].AGRICULTURE)
    c6r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].AGRICULTURE)
    c6r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].AGRICULTURE)
    c6r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].AGRICULTURE)
    c6r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].AGRICULTURE)
    c6_t5_total = c6r1_t5 + c6r2_t5 + c6r3_t5 + c6r4_t5 + c6r5_t5 + c6r6_t5

    # Column 7: ENVIRONMENT

    c7r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].ENVIRONMENT)
    c7r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].ENVIRONMENT)
    c7r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].ENVIRONMENT)
    c7r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].ENVIRONMENT)
    c7r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].ENVIRONMENT)
    c7r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].ENVIRONMENT)
    c7r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].ENVIRONMENT)
    c7_t1_total = c7r1_t1 + c7r2_t1 + c7r3_t1 + c7r4_t1 + c7r5_t1 + \
        c7r6_t1 + c7r7_t1

    c7r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].ENVIRONMENT)
    c7r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].ENVIRONMENT)
    c7r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].ENVIRONMENT)
    c7r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].ENVIRONMENT)
    c7r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].ENVIRONMENT)
    c7r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].ENVIRONMENT)
    c7_t2_total = c7r1_t2 + c7r2_t2 + c7r3_t2 + c7r4_t2 + c7r5_t2 + c7r6_t2

    c7r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].ENVIRONMENT)
    c7r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].ENVIRONMENT)
    c7r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].ENVIRONMENT)
    c7r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].ENVIRONMENT)
    c7_t3_total = c7r1_t3 + c7r2_t3 + c7r3_t3 + c7r4_t3

    c7r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].ENVIRONMENT)
    c7r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].ENVIRONMENT)
    c7r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].ENVIRONMENT)
    c7r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].ENVIRONMENT)
    c7r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].ENVIRONMENT)
    c7_t4_total = c7r1_t4 + c7r2_t4 + c7r3_t4 + c7r4_t4 + c7r5_t4

    c7r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].ENVIRONMENT)
    c7r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].ENVIRONMENT)
    c7r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].ENVIRONMENT)
    c7r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].ENVIRONMENT)
    c7r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].ENVIRONMENT)
    c7r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].ENVIRONMENT)
    c7_t5_total = c7r1_t5 + c7r2_t5 + c7r3_t5 + c7r4_t5 + c7r5_t5 + c7r6_t5

    # Column 8: ECONOMY

    c8r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].ECONOMY)
    c8r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].ECONOMY)
    c8r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].ECONOMY)
    c8r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].ECONOMY)
    c8r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].ECONOMY)
    c8r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].ECONOMY)
    c8r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].ECONOMY)
    c8_t1_total = c8r1_t1 + c8r2_t1 + c8r3_t1 + c8r4_t1 + c8r5_t1 + \
        c8r6_t1 + c8r7_t1

    c8r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].ECONOMY)
    c8r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].ECONOMY)
    c8r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].ECONOMY)
    c8r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].ECONOMY)
    c8r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].ECONOMY)
    c8r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].ECONOMY)
    c8_t2_total = c8r1_t2 + c8r2_t2 + c8r3_t2 + c8r4_t2 + c8r5_t2 + c8r6_t2

    c8r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].ECONOMY)
    c8r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].ECONOMY)
    c8r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].ECONOMY)
    c8r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].ECONOMY)
    c8_t3_total = c8r1_t3 + c8r2_t3 + c8r3_t3 + c8r4_t3

    c8r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].ECONOMY)
    c8r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].ECONOMY)
    c8r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].ECONOMY)
    c8r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].ECONOMY)
    c8r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].ECONOMY)
    c8_t4_total = c8r1_t4 + c8r2_t4 + c8r3_t4 + c8r4_t4 + c8r5_t4

    c8r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].ECONOMY)
    c8r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].ECONOMY)
    c8r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].ECONOMY)
    c8r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].ECONOMY)
    c8r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].ECONOMY)
    c8r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].ECONOMY)
    c8_t5_total = c8r1_t5 + c8r2_t5 + c8r3_t5 + c8r4_t5 + c8r5_t5 + c8r6_t5

    # Column 9: ENERGY

    c9r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].ENERGY)
    c9r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].ENERGY)
    c9r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].ENERGY)
    c9r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].ENERGY)
    c9r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].ENERGY)
    c9r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].ENERGY)
    c9r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].ENERGY)
    c9_t1_total = c9r1_t1 + c9r2_t1 + c9r3_t1 + c9r4_t1 + c9r5_t1 + \
        c9r6_t1 + c9r7_t1

    c9r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].ENERGY)
    c9r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].ENERGY)
    c9r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].ENERGY)
    c9r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].ENERGY)
    c9r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].ENERGY)
    c9r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].ENERGY)
    c9_t2_total = c9r1_t2 + c9r2_t2 + c9r3_t2 + c9r4_t2 + c9r5_t2 + c9r6_t2

    c9r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].ENERGY)
    c9r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].ENERGY)
    c9r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].ENERGY)
    c9r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].ENERGY)
    c9_t3_total = c9r1_t3 + c9r2_t3 + c9r3_t3 + c9r4_t3

    c9r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].ENERGY)
    c9r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].ENERGY)
    c9r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].ENERGY)
    c9r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].ENERGY)
    c9r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].ENERGY)
    c9_t4_total = c9r1_t4 + c9r2_t4 + c9r3_t4 + c9r4_t4 + c9r5_t4

    c9r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].ENERGY)
    c9r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].ENERGY)
    c9r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].ENERGY)
    c9r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].ENERGY)
    c9r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].ENERGY)
    c9r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].ENERGY)
    c9_t5_total = c9r1_t5 + c9r2_t5 + c9r3_t5 + c9r4_t5 + c9r5_t5 + c9r6_t5

    # Column 10: LEISURE

    c10r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].LEISURE)
    c10r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].LEISURE)
    c10r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].LEISURE)
    c10r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].LEISURE)
    c10r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].LEISURE)
    c10r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].LEISURE)
    c10r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].LEISURE)
    c10_t1_total = c10r1_t1 + c10r2_t1 + c10r3_t1 + c10r4_t1 + c10r5_t1 + \
        c10r6_t1 + c10r7_t1

    c10r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].LEISURE)
    c10r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].LEISURE)
    c10r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].LEISURE)
    c10r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].LEISURE)
    c10r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].LEISURE)
    c10r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].LEISURE)
    c10_t2_total = c10r1_t2 + c10r2_t2 + c10r3_t2 + c10r4_t2 + \
        c10r5_t2 + c10r6_t2

    c10r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].LEISURE)
    c10r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].LEISURE)
    c10r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].LEISURE)
    c10r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].LEISURE)
    c10_t3_total = c10r1_t3 + c10r2_t3 + c10r3_t3 + c10r4_t3

    c10r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].LEISURE)
    c10r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].LEISURE)
    c10r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].LEISURE)
    c10r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].LEISURE)
    c10r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].LEISURE)
    c10_t4_total = c10r1_t4 + c10r2_t4 + c10r3_t4 + c10r4_t4 + c10r5_t4

    c10r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].LEISURE)
    c10r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].LEISURE)
    c10r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].LEISURE)
    c10r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].LEISURE)
    c10r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].LEISURE)
    c10r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].LEISURE)
    c10_t5_total = c10r1_t5 + c10r2_t5 + c10r3_t5 + c10r4_t5 + \
        c10r5_t5 + c10r6_t5

    # Column 11: NON_BENEFICIAL

    c11r1_t1 = float(df_Pr.loc[df_Pr.CLASS == "Forest"].NON_BENEFICIAL)
    c11r2_t1 = float(df_Pr.loc[df_Pr.CLASS == "Shrubland"].NON_BENEFICIAL)
    c11r3_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural grasslands"].NON_BENEFICIAL)
    c11r4_t1 = float(df_Pr.loc[df_Pr.CLASS == "Natural water bodies"].NON_BENEFICIAL)
    c11r5_t1 = float(df_Pr.loc[df_Pr.CLASS == "Wetlands"].NON_BENEFICIAL)
    c11r6_t1 = float(df_Pr.loc[df_Pr.CLASS == "Glaciers"].NON_BENEFICIAL)
    c11r7_t1 = float(df_Pr.loc[df_Pr.CLASS == "Others"].NON_BENEFICIAL)
    c11_t1_total = c11r1_t1 + c11r2_t1 + c11r3_t1 + c11r4_t1 + c11r5_t1 + \
        c11r6_t1 + c11r7_t1

    c11r1_t2 = float(df_Ut.loc[df_Ut.CLASS == "Forest"].NON_BENEFICIAL)
    c11r2_t2 = float(df_Ut.loc[df_Ut.CLASS == "Shrubland"].NON_BENEFICIAL)
    c11r3_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural grasslands"].NON_BENEFICIAL)
    c11r4_t2 = float(df_Ut.loc[df_Ut.CLASS == "Natural water bodies"].NON_BENEFICIAL)
    c11r5_t2 = float(df_Ut.loc[df_Ut.CLASS == "Wetlands"].NON_BENEFICIAL)
    c11r6_t2 = float(df_Ut.loc[df_Ut.CLASS == "Others"].NON_BENEFICIAL)
    c11_t2_total = c11r1_t2 + c11r2_t2 + c11r3_t2 + c11r4_t2 + \
        c11r5_t2 + c11r6_t2

    c11r1_t3 = float(df_Mo.loc[df_Mo.CLASS == "Rainfed crops"].NON_BENEFICIAL)
    c11r2_t3 = float(df_Mo.loc[df_Mo.CLASS == "Forest plantations"].NON_BENEFICIAL)
    c11r3_t3 = float(df_Mo.loc[df_Mo.CLASS == "Settlements"].NON_BENEFICIAL)
    c11r4_t3 = float(df_Mo.loc[df_Mo.CLASS == "Others"].NON_BENEFICIAL)
    c11_t3_total = c11r1_t3 + c11r2_t3 + c11r3_t3 + c11r4_t3

    c11r1_t4 = float(df_Mc.loc[df_Mc.CLASS == "Irrigated crops"].NON_BENEFICIAL)
    c11r2_t4 = float(df_Mc.loc[df_Mc.CLASS == "Managed water bodies"].NON_BENEFICIAL)
    c11r3_t4 = float(df_Mc.loc[df_Mc.CLASS == "Residential"].NON_BENEFICIAL)
    c11r4_t4 = float(df_Mc.loc[df_Mc.CLASS == "Industry"].NON_BENEFICIAL)
    c11r5_t4 = float(df_Mc.loc[df_Mc.CLASS == "Others"].NON_BENEFICIAL)
    c11_t4_total = c11r1_t4 + c11r2_t4 + c11r3_t4 + c11r4_t4 + c11r5_t4

    c11r1_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor domestic"].NON_BENEFICIAL)
    c11r2_t5 = float(df_Mn.loc[df_Mn.CLASS == "Indoor industry"].NON_BENEFICIAL)
    c11r3_t5 = float(df_Mn.loc[df_Mn.CLASS == "Greenhouses"].NON_BENEFICIAL)
    c11r4_t5 = float(df_Mn.loc[df_Mn.CLASS == "Livestock and husbandry"].NON_BENEFICIAL)
    c11r5_t5 = float(df_Mn.loc[df_Mn.CLASS == "Power and energy"].NON_BENEFICIAL)
    c11r6_t5 = float(df_Mn.loc[df_Mn.CLASS == "Others"].NON_BENEFICIAL)
    c11_t5_total = c11r1_t5 + c11r2_t5 + c11r3_t5 + c11r4_t5 + \
        c11r5_t5 + c11r6_t5

    # Check if left and right side agree

    # Table 1
    r1_t1_bene = c6r1_t1 + c7r1_t1 + c8r1_t1 + c9r1_t1 + c10r1_t1
    r2_t1_bene = c6r2_t1 + c7r2_t1 + c8r2_t1 + c9r2_t1 + c10r2_t1
    r3_t1_bene = c6r3_t1 + c7r3_t1 + c8r3_t1 + c9r3_t1 + c10r3_t1
    r4_t1_bene = c6r4_t1 + c7r4_t1 + c8r4_t1 + c9r4_t1 + c10r4_t1
    r5_t1_bene = c6r5_t1 + c7r5_t1 + c8r5_t1 + c9r5_t1 + c10r5_t1
    r6_t1_bene = c6r6_t1 + c7r6_t1 + c8r6_t1 + c9r6_t1 + c10r6_t1
    r7_t1_bene = c6r7_t1 + c7r7_t1 + c8r7_t1 + c9r7_t1 + c10r7_t1

    c5r1_t1_left = c1r1_t1 + c2r1_t1 + c3r1_t1 + c4r1_t1
    c5r2_t1_left = c1r2_t1 + c2r2_t1 + c3r2_t1 + c4r2_t1
    c5r3_t1_left = c1r3_t1 + c2r3_t1 + c3r3_t1 + c4r3_t1
    c5r4_t1_left = c1r4_t1 + c2r4_t1 + c3r4_t1 + c4r4_t1
    c5r5_t1_left = c1r5_t1 + c2r5_t1 + c3r5_t1 + c4r5_t1
    c5r6_t1_left = c1r6_t1 + c2r6_t1 + c3r6_t1 + c4r6_t1
    c5r7_t1_left = c1r7_t1 + c2r7_t1 + c3r7_t1 + c4r7_t1

    c5r1_t1_right = r1_t1_bene + c11r1_t1
    c5r2_t1_right = r2_t1_bene + c11r2_t1
    c5r3_t1_right = r3_t1_bene + c11r3_t1
    c5r4_t1_right = r4_t1_bene + c11r4_t1
    c5r5_t1_right = r5_t1_bene + c11r5_t1
    c5r6_t1_right = r6_t1_bene + c11r6_t1
    c5r7_t1_right = r7_t1_bene + c11r7_t1

    # Table 2
    r1_t2_bene = c6r1_t2 + c7r1_t2 + c8r1_t2 + c9r1_t2 + c10r1_t2
    r2_t2_bene = c6r2_t2 + c7r2_t2 + c8r2_t2 + c9r2_t2 + c10r2_t2
    r3_t2_bene = c6r3_t2 + c7r3_t2 + c8r3_t2 + c9r3_t2 + c10r3_t2
    r4_t2_bene = c6r4_t2 + c7r4_t2 + c8r4_t2 + c9r4_t2 + c10r4_t2
    r5_t2_bene = c6r5_t2 + c7r5_t2 + c8r5_t2 + c9r5_t2 + c10r5_t2
    r6_t2_bene = c6r6_t2 + c7r6_t2 + c8r6_t2 + c9r6_t2 + c10r6_t2

    c5r1_t2_left = c1r1_t2 + c2r1_t2 + c3r1_t2 + c4r1_t2
    c5r2_t2_left = c1r2_t2 + c2r2_t2 + c3r2_t2 + c4r2_t2
    c5r3_t2_left = c1r3_t2 + c2r3_t2 + c3r3_t2 + c4r3_t2
    c5r4_t2_left = c1r4_t2 + c2r4_t2 + c3r4_t2 + c4r4_t2
    c5r5_t2_left = c1r5_t2 + c2r5_t2 + c3r5_t2 + c4r5_t2
    c5r6_t2_left = c1r6_t2 + c2r6_t2 + c3r6_t2 + c4r6_t2

    c5r1_t2_right = r1_t2_bene + c11r1_t2
    c5r2_t2_right = r2_t2_bene + c11r2_t2
    c5r3_t2_right = r3_t2_bene + c11r3_t2
    c5r4_t2_right = r4_t2_bene + c11r4_t2
    c5r5_t2_right = r5_t2_bene + c11r5_t2
    c5r6_t2_right = r6_t2_bene + c11r6_t2

    # Table 3
    r1_t3_bene = c6r1_t3 + c7r1_t3 + c8r1_t3 + c9r1_t3 + c10r1_t3
    r2_t3_bene = c6r2_t3 + c7r2_t3 + c8r2_t3 + c9r2_t3 + c10r2_t3
    r3_t3_bene = c6r3_t3 + c7r3_t3 + c8r3_t3 + c9r3_t3 + c10r3_t3
    r4_t3_bene = c6r4_t3 + c7r4_t3 + c8r4_t3 + c9r4_t3 + c10r4_t3

    c5r1_t3_left = c1r1_t3 + c2r1_t3 + c3r1_t3 + c4r1_t3
    c5r2_t3_left = c1r2_t3 + c2r2_t3 + c3r2_t3 + c4r2_t3
    c5r3_t3_left = c1r3_t3 + c2r3_t3 + c3r3_t3 + c4r3_t3
    c5r4_t3_left = c1r4_t3 + c2r4_t3 + c3r4_t3 + c4r4_t3

    c5r1_t3_right = r1_t3_bene + c11r1_t3
    c5r2_t3_right = r2_t3_bene + c11r2_t3
    c5r3_t3_right = r3_t3_bene + c11r3_t3
    c5r4_t3_right = r4_t3_bene + c11r4_t3

    # Table 4
    r1_t4_bene = c6r1_t4 + c7r1_t4 + c8r1_t4 + c9r1_t4 + c10r1_t4
    r2_t4_bene = c6r2_t4 + c7r2_t4 + c8r2_t4 + c9r2_t4 + c10r2_t4
    r3_t4_bene = c6r3_t4 + c7r3_t4 + c8r3_t4 + c9r3_t4 + c10r3_t4
    r4_t4_bene = c6r4_t4 + c7r4_t4 + c8r4_t4 + c9r4_t4 + c10r4_t4
    r5_t4_bene = c6r5_t4 + c7r5_t4 + c8r5_t4 + c9r5_t4 + c10r5_t4

    c5r1_t4_left = c1r1_t4 + c2r1_t4 + c3r1_t4 + c4r1_t4
    c5r2_t4_left = c1r2_t4 + c2r2_t4 + c3r2_t4 + c4r2_t4
    c5r3_t4_left = c1r3_t4 + c2r3_t4 + c3r3_t4 + c4r3_t4
    c5r4_t4_left = c1r4_t4 + c2r4_t4 + c3r4_t4 + c4r4_t4
    c5r5_t4_left = c1r5_t4 + c2r5_t4 + c3r5_t4 + c4r5_t4

    c5r1_t4_right = r1_t4_bene + c11r1_t4
    c5r2_t4_right = r2_t4_bene + c11r2_t4
    c5r3_t4_right = r3_t4_bene + c11r3_t4
    c5r4_t4_right = r4_t4_bene + c11r4_t4
    c5r5_t4_right = r5_t4_bene + c11r5_t4

    # Table 5
    r1_t5_bene = c6r1_t5 + c7r1_t5 + c8r1_t5 + c9r1_t5 + c10r1_t5
    r2_t5_bene = c6r2_t5 + c7r2_t5 + c8r2_t5 + c9r2_t5 + c10r2_t5
    r3_t5_bene = c6r3_t5 + c7r3_t5 + c8r3_t5 + c9r3_t5 + c10r3_t5
    r4_t5_bene = c6r4_t5 + c7r4_t5 + c8r4_t5 + c9r4_t5 + c10r4_t5
    r5_t5_bene = c6r5_t5 + c7r5_t5 + c8r5_t5 + c9r5_t5 + c10r5_t5
    r6_t5_bene = c6r6_t5 + c7r6_t5 + c8r6_t5 + c9r6_t5 + c10r6_t5

    c5r1_t5_left = c1r1_t5 + c2r1_t5 + c3r1_t5 + c4r1_t5
    c5r2_t5_left = c1r2_t5 + c2r2_t5 + c3r2_t5 + c4r2_t5
    c5r3_t5_left = c1r3_t5 + c2r3_t5 + c3r3_t5 + c4r3_t5
    c5r4_t5_left = c1r4_t5 + c2r4_t5 + c3r4_t5 + c4r4_t5
    c5r5_t5_left = c1r5_t5 + c2r5_t5 + c3r5_t5 + c4r5_t5
    c5r6_t5_left = c1r6_t5 + c2r6_t5 + c3r6_t5 + c4r6_t5

    c5r1_t5_right = r1_t5_bene + c11r1_t5
    c5r2_t5_right = r2_t5_bene + c11r2_t5
    c5r3_t5_right = r3_t5_bene + c11r3_t5
    c5r4_t5_right = r4_t5_bene + c11r4_t5
    c5r5_t5_right = r5_t5_bene + c11r5_t5
    c5r6_t5_right = r6_t5_bene + c11r6_t5

    # t1
    if abs(c5r1_t1_left - c5r1_t1_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('PROTECTED', 'Forest'))
    elif abs(c5r2_t1_left - c5r2_t1_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('PROTECTED', 'Shrubland'))
    elif abs(c5r3_t1_left - c5r3_t1_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('PROTECTED',
                                               'Natural grasslands'))
    elif abs(c5r4_t1_left - c5r4_t1_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('PROTECTED',
                                               'Natural water bodies'))
    elif abs(c5r5_t1_left - c5r5_t1_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('PROTECTED', 'Wetlands'))
    elif abs(c5r6_t1_left - c5r6_t1_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('PROTECTED', 'Glaciers'))
    elif abs(c5r7_t1_left - c5r7_t1_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('PROTECTED', 'Others'))

    # t2
    elif abs(c5r1_t2_left - c5r1_t2_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('UTILIZED', 'Forest'))
    elif abs(c5r2_t2_left - c5r2_t2_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('UTILIZED', 'Shrubland'))
    elif abs(c5r3_t2_left - c5r3_t2_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('UTILIZED',
                                               'Natural grasslands'))
    elif abs(c5r4_t2_left - c5r4_t2_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('UTILIZED',
                                               'Natural water bodies'))
    elif abs(c5r5_t2_left - c5r5_t2_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('UTILIZED', 'Wetlands'))
    elif abs(c5r6_t2_left - c5r6_t2_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('UTILIZED', 'Others'))

    # t3
    elif abs(c5r1_t3_left - c5r1_t3_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MODIFIED', 'Rainfed crops'))
    elif abs(c5r2_t3_left - c5r2_t3_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MODIFIED',
                                               'Forest plantations'))
    elif abs(c5r3_t3_left - c5r3_t3_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MODIFIED', 'Settlements'))
    elif abs(c5r4_t3_left - c5r4_t3_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MODIFIED', 'Others'))

    # t4
    elif abs(c5r1_t4_left - c5r1_t4_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED CONVENTIONAL',
                                               'Irrigated crops'))
    elif abs(c5r2_t4_left - c5r2_t4_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED CONVENTIONAL',
                                               'Managed water bodies'))
    elif abs(c5r3_t4_left - c5r3_t4_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED CONVENTIONAL',
                                               'Residential'))
    elif abs(c5r4_t4_left - c5r4_t4_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED CONVENTIONAL',
                                               'Industry'))
    elif abs(c5r5_t4_left - c5r5_t4_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED CONVENTIONAL',
                                               'Others'))

    # t5
    elif abs(c5r1_t5_left - c5r1_t5_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED NON_CONVENTIONAL',
                                               'Indoor domestic'))
    elif abs(c5r2_t5_left - c5r2_t5_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED NON_CONVENTIONAL',
                                               'Indoor industrial'))
    elif abs(c5r3_t5_left - c5r3_t5_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED NON_CONVENTIONAL',
                                               'Greenhouses'))
    elif abs(c5r4_t5_left - c5r4_t5_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED NON_CONVENTIONAL',
                                               'Livestock and husbandry'))
    elif abs(c5r5_t5_left - c5r5_t5_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED NON_CONVENTIONAL',
                                               'Power and energy'))
    elif abs(c5r6_t5_left - c5r6_t5_right) > tolerance:
        raise ValueError('The left and rigth sides \
                          do not add up ({0} table \
                          and {1} row)'.format('MANAGED NON_CONVENTIONAL',
                                               'Others'))

    # Calculations & modify svg
    if not template:
        path = os.path.dirname(os.path.abspath(__file__))
        svg_template_path = os.path.join(path, 'svg', 'sheet_2.svg')
    else:
        svg_template_path = os.path.abspath(template)

    tree = ET.parse(svg_template_path)

    # Titles

    xml_txt_box = tree.findall('''.//*[@id='basin']''')[0]
    xml_txt_box.getchildren()[0].text = 'Basin: ' + basin

    xml_txt_box = tree.findall('''.//*[@id='period']''')[0]
    xml_txt_box.getchildren()[0].text = 'Period: ' + period

    xml_txt_box = tree.findall('''.//*[@id='units']''')[0]
    xml_txt_box.getchildren()[0].text = 'Sheet 2: Evapotranspiration (' + units + ')'

    # Total ET
    total_et_t1 = c5r1_t1_left + c5r2_t1_left + c5r3_t1_left + c5r4_t1_left + \
        c5r5_t1_left + c5r6_t1_left + c5r7_t1_left
    total_et_t2 = c5r1_t2_left + c5r2_t2_left + c5r3_t2_left + c5r4_t2_left + \
        c5r5_t2_left + c5r6_t2_left
    total_et_t3 = c5r1_t3_left + c5r2_t3_left + c5r3_t3_left + c5r4_t3_left
    total_et_t4 = c5r1_t4_left + c5r2_t4_left + c5r3_t4_left + c5r4_t4_left + \
        c5r5_t4_left
    total_et_t5 = c5r1_t5_left + c5r2_t5_left + c5r3_t5_left + c5r4_t5_left + \
        c5r5_t5_left + c5r6_t5_left

    total_et = total_et_t1 + total_et_t2 + total_et_t3 + \
        total_et_t4 + total_et_t5

    et_total_managed_lu = total_et_t4 + total_et_t5
    et_total_managed = total_et_t3 + et_total_managed_lu

    t_total_managed_lu = c1_t4_total + c1_t5_total

    xml_txt_box = tree.findall('''.//*[@id='total_et']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_et

    xml_txt_box = tree.findall('''.//*[@id='non-manageble']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_et_t1

    xml_txt_box = tree.findall('''.//*[@id='manageble']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_et_t2

    xml_txt_box = tree.findall('''.//*[@id='managed']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_total_managed

    # Totals land use

    xml_txt_box = tree.findall('''.//*[@id='protected_lu_et']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_et_t1

    xml_txt_box = tree.findall('''.//*[@id='protected_lu_t']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1_t1_total

    xml_txt_box = tree.findall('''.//*[@id='utilized_lu_et']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_et_t2

    xml_txt_box = tree.findall('''.//*[@id='utilized_lu_t']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1_t2_total

    xml_txt_box = tree.findall('''.//*[@id='modified_lu_et']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_et_t3

    xml_txt_box = tree.findall('''.//*[@id='modified_lu_t']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1_t3_total

    xml_txt_box = tree.findall('''.//*[@id='managed_lu_et']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_total_managed_lu

    xml_txt_box = tree.findall('''.//*[@id='managed_lu_t']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % t_total_managed_lu

    # Table 1
    xml_txt_box = tree.findall('''.//*[@id='plu_et_forest']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r1_t1_left

    xml_txt_box = tree.findall('''.//*[@id='plu_t_forest']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r1_t1

    xml_txt_box = tree.findall('''.//*[@id='plu_et_shrubland']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r2_t1_left

    xml_txt_box = tree.findall('''.//*[@id='plu_t_shrubland']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r2_t1

    xml_txt_box = tree.findall('''.//*[@id='plu_et_grasslands']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r3_t1_left

    xml_txt_box = tree.findall('''.//*[@id='plu_t_grasslands']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r3_t1

    xml_txt_box = tree.findall('''.//*[@id='plu_et_waterbodies']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r4_t1_left

    xml_txt_box = tree.findall('''.//*[@id='plu_t_waterbodies']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r4_t1

    xml_txt_box = tree.findall('''.//*[@id='plu_et_wetlands']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r5_t1_left

    xml_txt_box = tree.findall('''.//*[@id='plu_t_wetlands']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r5_t1

    xml_txt_box = tree.findall('''.//*[@id='plu_et_glaciers']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r6_t1_left

    xml_txt_box = tree.findall('''.//*[@id='plu_t_glaciers']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r6_t1

    xml_txt_box = tree.findall('''.//*[@id='plu_et_others']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r7_t1_left

    xml_txt_box = tree.findall('''.//*[@id='plu_t_others']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r7_t1

    # Table 2
    xml_txt_box = tree.findall('''.//*[@id='ulu_et_forest']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r1_t2_left

    xml_txt_box = tree.findall('''.//*[@id='ulu_t_forest']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r1_t2

    xml_txt_box = tree.findall('''.//*[@id='ulu_et_shrubland']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r2_t2_left

    xml_txt_box = tree.findall('''.//*[@id='ulu_t_shrubland']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r2_t2

    xml_txt_box = tree.findall('''.//*[@id='ulu_et_grasslands']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r3_t2_left

    xml_txt_box = tree.findall('''.//*[@id='ulu_t_grasslands']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r3_t2

    xml_txt_box = tree.findall('''.//*[@id='ulu_et_waterbodies']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r4_t2_left

    xml_txt_box = tree.findall('''.//*[@id='ulu_t_waterbodies']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r4_t2

    xml_txt_box = tree.findall('''.//*[@id='ulu_et_wetlands']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r5_t2_left

    xml_txt_box = tree.findall('''.//*[@id='ulu_t_wetlands']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r5_t2

    xml_txt_box = tree.findall('''.//*[@id='ulu_et_others']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r6_t2_left

    xml_txt_box = tree.findall('''.//*[@id='ulu_t_others']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r6_t2

    # Table 3
    xml_txt_box = tree.findall('''.//*[@id='molu_et_rainfed']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r1_t3_left

    xml_txt_box = tree.findall('''.//*[@id='molu_t_rainfed']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r1_t3

    xml_txt_box = tree.findall('''.//*[@id='molu_et_forest']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r2_t3_left

    xml_txt_box = tree.findall('''.//*[@id='molu_t_forest']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r2_t3

    xml_txt_box = tree.findall('''.//*[@id='molu_et_settlements']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r3_t3_left

    xml_txt_box = tree.findall('''.//*[@id='molu_t_settlements']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r3_t3

    xml_txt_box = tree.findall('''.//*[@id='molu_et_others']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r4_t3_left

    xml_txt_box = tree.findall('''.//*[@id='molu_t_others']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r4_t3

    # Table 4
    xml_txt_box = tree.findall('''.//*[@id='malu_et_crops']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r1_t4_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_crops']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r1_t4

    xml_txt_box = tree.findall('''.//*[@id='malu_et_waterbodies']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r2_t4_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_waterbodies']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r2_t4

    xml_txt_box = tree.findall('''.//*[@id='malu_et_residential']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r3_t4_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_residential']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r3_t4

    xml_txt_box = tree.findall('''.//*[@id='malu_et_industry']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r4_t4_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_industry']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r4_t4

    xml_txt_box = tree.findall('''.//*[@id='malu_et_others1']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r5_t4_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_others1']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r5_t4

    # Table 5
    xml_txt_box = tree.findall('''.//*[@id='malu_et_idomestic']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r1_t5_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_idomestic']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r1_t5

    xml_txt_box = tree.findall('''.//*[@id='malu_et_iindustry']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r2_t5_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_iindustry']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r2_t5

    xml_txt_box = tree.findall('''.//*[@id='malu_et_greenhouses']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r3_t5_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_greenhouses']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r3_t5

    xml_txt_box = tree.findall('''.//*[@id='malu_et_livestock']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r4_t5_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_livestock']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r4_t5

    xml_txt_box = tree.findall('''.//*[@id='malu_et_powerandenergy']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r5_t5_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_powerandenergy']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r5_t5

    xml_txt_box = tree.findall('''.//*[@id='malu_et_others2']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c5r6_t5_left

    xml_txt_box = tree.findall('''.//*[@id='malu_t_others2']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % c1r6_t5

    # Right box
    total_t = c1_t1_total + c1_t2_total + c1_t3_total + \
        c1_t4_total + c1_t5_total
    total_e = total_et - total_t

    total_water = c2_t1_total + c2_t2_total + c2_t3_total + \
        c2_t4_total + c2_t5_total
    total_soil = c3_t1_total + c3_t2_total + c3_t3_total + \
        c3_t4_total + c3_t5_total
    total_interception = c4_t1_total + c4_t2_total + c4_t3_total + \
        c4_t4_total + c4_t5_total

    xml_txt_box = tree.findall('''.//*[@id='evaporation']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_e

    xml_txt_box = tree.findall('''.//*[@id='transpiration']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_t

    xml_txt_box = tree.findall('''.//*[@id='water']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_water

    xml_txt_box = tree.findall('''.//*[@id='soil']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_soil

    xml_txt_box = tree.findall('''.//*[@id='interception']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_interception

    total_agr = c6_t1_total + c6_t2_total + c6_t3_total + \
        c6_t4_total + c6_t5_total
    total_env = c7_t1_total + c7_t2_total + c7_t3_total + \
        c7_t4_total + c7_t5_total
    total_eco = c8_t1_total + c8_t2_total + c8_t3_total + \
        c8_t4_total + c8_t5_total
    total_ene = c9_t1_total + c9_t2_total + c9_t3_total + \
        c9_t4_total + c9_t5_total
    total_lei = c10_t1_total + c10_t2_total + c10_t3_total + \
        c10_t4_total + c10_t5_total

    total_bene = total_agr + total_env + total_eco + total_ene + total_lei
    total_non_bene = c11_t1_total + c11_t2_total + c11_t3_total + \
        c11_t4_total + c11_t5_total

    xml_txt_box = tree.findall('''.//*[@id='non-beneficial']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_non_bene

    xml_txt_box = tree.findall('''.//*[@id='beneficial']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_bene

    xml_txt_box = tree.findall('''.//*[@id='agriculture']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_agr

    xml_txt_box = tree.findall('''.//*[@id='environment']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_env

    xml_txt_box = tree.findall('''.//*[@id='economy']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_eco

    xml_txt_box = tree.findall('''.//*[@id='energy']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_ene

    xml_txt_box = tree.findall('''.//*[@id='leisure']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % total_lei

    # svg to string
    ET.register_namespace("", "http://www.w3.org/2000/svg")

    # Get the paths based on the environment variable
    if os.name == 'posix':
        Path_Inkscape = 'inkscape'
        
    else:
        WA_env_paths = os.environ["WA_PATHS"].split(';')
        Inkscape_env_path = WA_env_paths[1]
        Path_Inkscape = os.path.join(Inkscape_env_path,'inkscape.exe')

    # Export svg to png
    tempout_path = output.replace('.pdf', '_temporary.svg')
    tree.write(tempout_path)
    subprocess.call([Path_Inkscape,tempout_path,'--export-pdf='+output, '-d 300'])
    time.sleep(10)
    os.remove(tempout_path)


    # Return
    return output
