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
from wand.image import Image
import xml.etree.ElementTree as ET


def create_sheet7(basin, period, units, data, output, template=False):
    """

    Keyword arguments:
    basin -- The name of the basin
    period -- The period of analysis
    units -- The units of the data. For this sheet only Mm3/yr are allowed
             as input
    data -- A csv file that contains the water data. The csv file has to
            follow an specific format. A sample csv is available in the link:
            https://github.com/wateraccounting/wa/tree/master/Sheets/csv
    output -- The output jpg file for the sheet
    template -- A svg file of the sheet. Use False (default) to use the
                standard svg file.
    """

    # Check units

    if units != 'Mm3/yr':
        raise ValueError('The units must be Mm3/yr')

    # Read table

    df = pd.read_csv(data, sep=';')

    # Data frames

    df_Mo = df.loc[df.LAND_USE == "MODIFIED"]
    df_Pr = df.loc[df.LAND_USE == "PROTECTED"]
    df_Ma = df.loc[df.LAND_USE == "MANAGED"]
    df_Ut = df.loc[df.LAND_USE == "UTILIZED"]

    # MODIFIED LAND USE

    mlu_01 = float(df_Mo.loc[
                   (df_Mo.VARIABLE == "Total runoff") &
                   (df_Mo.SERVICE == "-")].VALUE)
    mlu_02 = float(df_Mo.loc[
                   (df_Mo.VARIABLE == "Dry season flow ('baseflow')") &
                   (df_Mo.SERVICE == "-")].VALUE)
    mlu_03 = float(df_Mo.loc[
                   (df_Mo.VARIABLE == "Groundwater recharge") &
                   (df_Mo.SERVICE == "-")].VALUE)
    mlu_04 = float(df_Mo.loc[
                   (df_Mo.VARIABLE == "Reducing erosion and sedimentation") &
                   (df_Mo.SERVICE == "-")].VALUE)
    mlu_05 = float(df_Mo.loc[
                   (df_Mo.VARIABLE == "Reduce greenhouse gas emissions") &
                   (df_Mo.SERVICE == "-")].VALUE)
    mlu_06 = float(df_Mo.loc[
                   (df_Mo.VARIABLE == "Carbon sequestration") &
                   (df_Mo.SERVICE == "-")].VALUE)
    mlu_07 = float(df_Mo.loc[
                   (df_Mo.VARIABLE == "Micro-climate cooling") &
                   (df_Mo.SERVICE == "-")].VALUE)
    mlu_08 = float(df_Mo.loc[
                   (df_Mo.VARIABLE == "Enhanced atmospheric moisture recycling") &
                   (df_Mo.SERVICE == "-")].VALUE)
    mlu_09 = float(df_Mo.loc[
                   (df_Mo.VARIABLE == "Aquatic connectivity (fragmentations)") &
                   (df_Mo.SERVICE == "-")].VALUE)
    mlu_10 = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Leisure") &
                    (df_Mo.SERVICE == "-")].VALUE)

    mlu_01a = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Total runoff") &
                    (df_Mo.SERVICE == "Non-consumptive")].VALUE)
    mlu_02a = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Dry season flow ('baseflow')") &
                    (df_Mo.SERVICE == "Non-consumptive")].VALUE)
    mlu_03a = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Groundwater recharge") &
                    (df_Mo.SERVICE == "Non-consumptive")].VALUE)
    mlu_04b = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Reducing erosion and sedimentation") &
                    (df_Mo.SERVICE == "Incremental ET natural")].VALUE)
    mlu_04c = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Reducing erosion and sedimentation") &
                    (df_Mo.SERVICE == "Landscape ET")].VALUE)
    mlu_05b = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Reduce greenhouse gas emissions") &
                    (df_Mo.SERVICE == "Incremental ET natural")].VALUE)
    mlu_05c = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Reduce greenhouse gas emissions") &
                    (df_Mo.SERVICE == "Landscape ET")].VALUE)
    mlu_060708b = float(df_Mo.loc[
                        (df_Mo.VARIABLE == "C seq, Micro-clim cooling, & e. atm moist recy") &
                        (df_Mo.SERVICE == "Incremental ET natural")].VALUE)
    mlu_060708c = float(df_Mo.loc[
                        (df_Mo.VARIABLE == "C seq, Micro-clim cooling, & e. atm moist recy") &
                        (df_Mo.SERVICE == "Landscape ET")].VALUE)
    mlu_09b = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Aquatic connectivity (fragmentations)") &
                    (df_Mo.SERVICE == "Incremental ET natural")].VALUE)
    mlu_09c = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Aquatic connectivity (fragmentations)") &
                    (df_Mo.SERVICE == "Landscape ET")].VALUE)
    mlu_10a = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Leisure") &
                    (df_Mo.SERVICE == "Non-consumptive")].VALUE)
    mlu_10b = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Leisure") &
                    (df_Mo.SERVICE == "Incremental ET natural")].VALUE)
    mlu_10c = float(df_Mo.loc[
                    (df_Mo.VARIABLE == "Leisure") &
                    (df_Mo.SERVICE == "Landscape ET")].VALUE)

    mlu_incremental = mlu_04b + mlu_05b + mlu_060708b + mlu_09b + mlu_10b
    mlu_landscape = mlu_04c + mlu_05c + mlu_060708c + mlu_09c + mlu_10c

    # PROTECTED LAND USE

    plu_01 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Total runoff") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_02 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Inland capture fishery") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_03 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Natural livestock feed production") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_04 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Dry season flow ('baseflow')") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_05 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Groundwater recharge") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_06 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Natural water storage in lakes") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_07 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Peak flow attenuation") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_08 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Reducing erosion and sedimentation") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_09 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Carbon sequestration") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_10 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Micro-climate cooling") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_11 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Enhanced atmospheric moisture recycling") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_12 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Natural reduction of eutrophication in water") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_13 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Reduce greenhouse gas emissions") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_14 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Aquatic connectivity (fragmentations)") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_15 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Environmental flow requirements") &
                   (df_Pr.SERVICE == "-")].VALUE)
    plu_16 = float(df_Pr.loc[
                   (df_Pr.VARIABLE == "Leisure") &
                   (df_Pr.SERVICE == "-")].VALUE)

    plu_01a = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Total runoff") &
                    (df_Pr.SERVICE == "Non-consumptive")].VALUE)
    plu_02a = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Inland capture fishery") &
                    (df_Pr.SERVICE == "Non-consumptive")].VALUE)
    plu_02b = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Inland capture fishery") &
                    (df_Pr.SERVICE == "Incremental ET natural")].VALUE)
    plu_02c = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Inland capture fishery") &
                    (df_Pr.SERVICE == "Landscape ET")].VALUE)
    plu_03b = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Natural livestock feed production") &
                    (df_Pr.SERVICE == "Incremental ET natural")].VALUE)
    plu_03c = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Natural livestock feed production") &
                    (df_Pr.SERVICE == "Landscape ET")].VALUE)
    plu_04a = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Dry season flow ('baseflow')") &
                    (df_Pr.SERVICE == "Non-consumptive")].VALUE)
    plu_05a = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Groundwater recharge") &
                    (df_Pr.SERVICE == "Non-consumptive")].VALUE)
    plu_06a = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Natural water storage in lakes") &
                    (df_Pr.SERVICE == "Non-consumptive")].VALUE)
    plu_06b = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Natural water storage in lakes") &
                    (df_Pr.SERVICE == "Incremental ET natural")].VALUE)
    plu_06c = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Natural water storage in lakes") &
                    (df_Pr.SERVICE == "Landscape ET")].VALUE)
    plu_07a = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Peak flow attenuation") &
                    (df_Pr.SERVICE == "Non-consumptive")].VALUE)
    plu_08b = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Reducing erosion and sedimentation") &
                    (df_Pr.SERVICE == "Incremental ET natural")].VALUE)
    plu_08c = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Reducing erosion and sedimentation") &
                    (df_Pr.SERVICE == "Landscape ET")].VALUE)
    plu_091011b = float(df_Pr.loc[
                        (df_Pr.VARIABLE == "C seq, Micro-clim cooling, & e. atm moist recy") &
                        (df_Pr.SERVICE == "Incremental ET natural")].VALUE)
    plu_091011c = float(df_Pr.loc[
                        (df_Pr.VARIABLE == "C seq, Micro-clim cooling, & e. atm moist recy") &
                        (df_Pr.SERVICE == "Landscape ET")].VALUE)
    plu_12a = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Natural reduction of eutrophication in water") &
                    (df_Pr.SERVICE == "Non-consumptive")].VALUE)
    plu_13b = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Reduce greenhouse gas emissions") &
                    (df_Pr.SERVICE == "Incremental ET natural")].VALUE)
    plu_13c = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Reduce greenhouse gas emissions") &
                    (df_Pr.SERVICE == "Landscape ET")].VALUE)
    plu_14b = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Aquatic connectivity (fragmentations)") &
                    (df_Pr.SERVICE == "Incremental ET natural")].VALUE)
    plu_14c = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Aquatic connectivity (fragmentations)") &
                    (df_Pr.SERVICE == "Landscape ET")].VALUE)
    plu_15a = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Environmental flow requirements") &
                    (df_Pr.SERVICE == "Non-consumptive")].VALUE)
    plu_16a = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Leisure") &
                    (df_Pr.SERVICE == "Non-consumptive")].VALUE)
    plu_16b = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Leisure") &
                    (df_Pr.SERVICE == "Incremental ET natural")].VALUE)
    plu_16c = float(df_Pr.loc[
                    (df_Pr.VARIABLE == "Leisure") &
                    (df_Pr.SERVICE == "Landscape ET")].VALUE)

    plu_incremental = plu_02b + plu_03b + plu_06b + plu_08b + plu_091011b + \
        plu_13b + plu_14b + plu_16b
    plu_landscape = plu_02c + plu_03c + plu_06c + plu_08c + plu_091011c + \
        plu_13c + plu_14c + plu_16c

    # MANAGED WATER USE

    mwu_01 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Total runoff") &
                   (df_Ma.SERVICE == "-")].VALUE)
    mwu_02 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Dry season flow ('baseflow')") &
                   (df_Ma.SERVICE == "-")].VALUE)
    mwu_03 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Groundwater recharge") &
                   (df_Ma.SERVICE == "-")].VALUE)
    mwu_04 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Reducing erosion and sedimentation") &
                   (df_Ma.SERVICE == "-")].VALUE)
    mwu_05 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Carbon sequestration") &
                   (df_Ma.SERVICE == "-")].VALUE)
    mwu_06 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Micro-climate cooling") &
                   (df_Ma.SERVICE == "-")].VALUE)
    mwu_07 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Enhanced atmospheric moisture recycling") &
                   (df_Ma.SERVICE == "-")].VALUE)
    mwu_08 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Reduce greenhouse gas emissions") &
                   (df_Ma.SERVICE == "-")].VALUE)
    mwu_09 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Aquatic connectivity (fragmentations)") &
                   (df_Ma.SERVICE == "-")].VALUE)
    mwu_10 = float(df_Ma.loc[
                   (df_Ma.VARIABLE == "Leisure") &
                   (df_Ma.SERVICE == "-")].VALUE)

    mwu_01a = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Total runoff") &
                    (df_Ma.SERVICE == "Non-consumptive")].VALUE)
    mwu_02a = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Dry season flow ('baseflow')") &
                    (df_Ma.SERVICE == "Non-consumptive")].VALUE)
    mwu_03a = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Groundwater recharge") &
                    (df_Ma.SERVICE == "Non-consumptive")].VALUE)
    mwu_04b = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Reducing erosion and sedimentation") &
                    (df_Ma.SERVICE == "Incremental ET natural")].VALUE)
    mwu_04c = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Reducing erosion and sedimentation") &
                    (df_Ma.SERVICE == "Landscape ET")].VALUE)
    mwu_050607b = float(df_Ma.loc[
                        (df_Ma.VARIABLE == "C seq, Micro-clim cooling, & e. atm moist recy") &
                        (df_Ma.SERVICE == "Incremental ET natural")].VALUE)
    mwu_050607c = float(df_Ma.loc[
                        (df_Ma.VARIABLE == "C seq, Micro-clim cooling, & e. atm moist recy") &
                        (df_Ma.SERVICE == "Landscape ET")].VALUE)
    mwu_08b = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Reduce greenhouse gas emissions") &
                    (df_Ma.SERVICE == "Incremental ET natural")].VALUE)
    mwu_08c = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Reduce greenhouse gas emissions") &
                    (df_Ma.SERVICE == "Landscape ET")].VALUE)
    mwu_09b = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Aquatic connectivity (fragmentations)") &
                    (df_Ma.SERVICE == "Incremental ET natural")].VALUE)
    mwu_09c = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Aquatic connectivity (fragmentations)") &
                    (df_Ma.SERVICE == "Landscape ET")].VALUE)
    mwu_10a = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Leisure") &
                    (df_Ma.SERVICE == "Non-consumptive")].VALUE)
    mwu_10b = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Leisure") &
                    (df_Ma.SERVICE == "Incremental ET natural")].VALUE)
    mwu_10c = float(df_Ma.loc[
                    (df_Ma.VARIABLE == "Leisure") &
                    (df_Ma.SERVICE == "Landscape ET")].VALUE)

    mwu_incremental = mwu_04b + mwu_050607b + mwu_08b + mwu_09b + mwu_10b
    mwu_landscape = mwu_04c + mwu_050607c + mwu_08c + mwu_09c + mwu_10c

    # UTILIZED LAND USE

    ulu_01 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Total runoff") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_02 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Inland capture fishery") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_03 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Natural livestock feed production") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_04 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Fuelwood from natural forest") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_05 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Dry season flow ('baseflow')") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_06 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Groundwater recharge") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_07 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Natural water storage in lakes") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_08 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Peak flow attenuation") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_09 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Reducing erosion and sedimentation") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_10 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Carbon sequestration") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_11 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Micro-climate cooling") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_12 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Enhanced atmospheric moisture recycling") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_13 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Natural reduction of eutrophication in water") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_14 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Reduce greenhouse gas emissions") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_15 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Aquatic connectivity (fragmentations)") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_16 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Environmental flow requirements") &
                   (df_Ut.SERVICE == "-")].VALUE)
    ulu_17 = float(df_Ut.loc[
                   (df_Ut.VARIABLE == "Leisure") &
                   (df_Ut.SERVICE == "-")].VALUE)

    ulu_01a = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Total runoff") &
                    (df_Ut.SERVICE == "Non-consumptive")].VALUE)
    ulu_02a = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Inland capture fishery") &
                    (df_Ut.SERVICE == "Non-consumptive")].VALUE)
    ulu_02b = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Inland capture fishery") &
                    (df_Ut.SERVICE == "Incremental ET natural")].VALUE)
    ulu_02c = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Inland capture fishery") &
                    (df_Ut.SERVICE == "Landscape ET")].VALUE)
    ulu_03b = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Natural livestock feed production") &
                    (df_Ut.SERVICE == "Incremental ET natural")].VALUE)
    ulu_03c = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Natural livestock feed production") &
                    (df_Ut.SERVICE == "Landscape ET")].VALUE)
    ulu_04b = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Fuelwood from natural forest") &
                    (df_Ut.SERVICE == "Incremental ET natural")].VALUE)
    ulu_04c = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Fuelwood from natural forest") &
                    (df_Ut.SERVICE == "Landscape ET")].VALUE)
    ulu_05a = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Dry season flow ('baseflow')") &
                    (df_Ut.SERVICE == "Non-consumptive")].VALUE)
    ulu_06a = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Groundwater recharge") &
                    (df_Ut.SERVICE == "Non-consumptive")].VALUE)
    ulu_07a = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Natural water storage in lakes") &
                    (df_Ut.SERVICE == "Non-consumptive")].VALUE)
    ulu_07b = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Natural water storage in lakes") &
                    (df_Ut.SERVICE == "Incremental ET natural")].VALUE)
    ulu_07c = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Natural water storage in lakes") &
                    (df_Ut.SERVICE == "Landscape ET")].VALUE)
    ulu_08a = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Peak flow attenuation") &
                    (df_Ut.SERVICE == "Non-consumptive")].VALUE)
    ulu_09b = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Reducing erosion and sedimentation") &
                    (df_Ut.SERVICE == "Incremental ET natural")].VALUE)
    ulu_09c = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Reducing erosion and sedimentation") &
                    (df_Ut.SERVICE == "Landscape ET")].VALUE)
    ulu_101112b = float(df_Ut.loc[
                        (df_Ut.VARIABLE == "C seq, Micro-clim cooling, & e. atm moist recy") &
                        (df_Ut.SERVICE == "Incremental ET natural")].VALUE)
    ulu_101112c = float(df_Ut.loc[
                        (df_Ut.VARIABLE == "C seq, Micro-clim cooling, & e. atm moist recy") &
                        (df_Ut.SERVICE == "Landscape ET")].VALUE)
    ulu_13a = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Natural reduction of eutrophication in water") &
                    (df_Ut.SERVICE == "Non-consumptive")].VALUE)
    ulu_14b = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Reduce greenhouse gas emissions") &
                    (df_Ut.SERVICE == "Incremental ET natural")].VALUE)
    ulu_14c = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Reduce greenhouse gas emissions") &
                    (df_Ut.SERVICE == "Landscape ET")].VALUE)
    ulu_15b = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Aquatic connectivity (fragmentations)") &
                    (df_Ut.SERVICE == "Incremental ET natural")].VALUE)
    ulu_15c = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Aquatic connectivity (fragmentations)") &
                    (df_Ut.SERVICE == "Landscape ET")].VALUE)
    ulu_16a = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Environmental flow requirements") &
                    (df_Ut.SERVICE == "Non-consumptive")].VALUE)
    ulu_17a = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Leisure") &
                    (df_Ut.SERVICE == "Non-consumptive")].VALUE)
    ulu_17b = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Leisure") &
                    (df_Ut.SERVICE == "Incremental ET natural")].VALUE)
    ulu_17c = float(df_Ut.loc[
                    (df_Ut.VARIABLE == "Leisure") &
                    (df_Ut.SERVICE == "Landscape ET")].VALUE)

    ulu_incremental = ulu_02b + ulu_03b + ulu_04b + ulu_07b + ulu_09b + \
        ulu_101112b + ulu_14b + ulu_15b + ulu_17b
    ulu_landscape = ulu_02c + ulu_03c + ulu_04c + ulu_07c + ulu_09c + \
        ulu_101112c + ulu_14c + ulu_15c + ulu_17c

    # Calculations & modify svg
    if not template:
        path = os.path.dirname(os.path.abspath(__file__))
        svg_template_path = os.path.join(path, 'svg', 'sheet_7.svg')
    else:
        svg_template_path = os.path.abspath(template)

    tree = ET.parse(svg_template_path)

    # Titles

    xml_txt_box = tree.findall('''.//*[@id='basin']''')[0]
    xml_txt_box.getchildren()[0].text = 'Basin: ' + basin

    xml_txt_box = tree.findall('''.//*[@id='period']''')[0]
    xml_txt_box.getchildren()[0].text = 'Period: ' + period

    xml_txt_box = tree.findall('''.//*[@id='units']''')[0]
    xml_txt_box.getchildren()[0].text = 'Sheet 7: Hydrologial Ecosystem Services (' + units + ')'

    # MODIFIED LAND USE

    xml_txt_box = tree.findall('''.//*[@id='mlu_01']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_01
    xml_txt_box = tree.findall('''.//*[@id='mlu_02']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_02
    xml_txt_box = tree.findall('''.//*[@id='mlu_03']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_03
    xml_txt_box = tree.findall('''.//*[@id='mlu_04']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_04
    xml_txt_box = tree.findall('''.//*[@id='mlu_05']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_05
    xml_txt_box = tree.findall('''.//*[@id='mlu_06']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_06
    xml_txt_box = tree.findall('''.//*[@id='mlu_07']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_07
    xml_txt_box = tree.findall('''.//*[@id='mlu_08']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_08
    xml_txt_box = tree.findall('''.//*[@id='mlu_09']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_09
    xml_txt_box = tree.findall('''.//*[@id='mlu_10']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_10

    xml_txt_box = tree.findall('''.//*[@id='mlu_01a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_01a
    xml_txt_box = tree.findall('''.//*[@id='mlu_02a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_02a
    xml_txt_box = tree.findall('''.//*[@id='mlu_03a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_03a
    xml_txt_box = tree.findall('''.//*[@id='mlu_04b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_04b
    xml_txt_box = tree.findall('''.//*[@id='mlu_04c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_04c
    xml_txt_box = tree.findall('''.//*[@id='mlu_05b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_05b
    xml_txt_box = tree.findall('''.//*[@id='mlu_05c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_05c
    xml_txt_box = tree.findall('''.//*[@id='mlu_060708b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_060708b
    xml_txt_box = tree.findall('''.//*[@id='mlu_060708c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_060708c
    xml_txt_box = tree.findall('''.//*[@id='mlu_09b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_09b
    xml_txt_box = tree.findall('''.//*[@id='mlu_09c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_09c
    xml_txt_box = tree.findall('''.//*[@id='mlu_10a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_10a
    xml_txt_box = tree.findall('''.//*[@id='mlu_10b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_10b
    xml_txt_box = tree.findall('''.//*[@id='mlu_10c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_10c
    
    # PROTECTED LAND USE

    xml_txt_box = tree.findall('''.//*[@id='plu_01']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_01
    xml_txt_box = tree.findall('''.//*[@id='plu_02']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_02
    xml_txt_box = tree.findall('''.//*[@id='plu_03']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_03
    xml_txt_box = tree.findall('''.//*[@id='plu_04']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_04
    xml_txt_box = tree.findall('''.//*[@id='plu_05']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_05
    xml_txt_box = tree.findall('''.//*[@id='plu_06']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_06
    xml_txt_box = tree.findall('''.//*[@id='plu_07']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_07
    xml_txt_box = tree.findall('''.//*[@id='plu_08']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_08
    xml_txt_box = tree.findall('''.//*[@id='plu_09']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_09
    xml_txt_box = tree.findall('''.//*[@id='plu_10']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_10
    xml_txt_box = tree.findall('''.//*[@id='plu_11']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_11
    xml_txt_box = tree.findall('''.//*[@id='plu_12']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_12
    xml_txt_box = tree.findall('''.//*[@id='plu_13']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_13
    xml_txt_box = tree.findall('''.//*[@id='plu_14']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_14
    xml_txt_box = tree.findall('''.//*[@id='plu_15']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_15
    xml_txt_box = tree.findall('''.//*[@id='plu_16']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_16

    xml_txt_box = tree.findall('''.//*[@id='plu_01a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_01a
    xml_txt_box = tree.findall('''.//*[@id='plu_02a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_02a
    xml_txt_box = tree.findall('''.//*[@id='plu_02b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_02b
    xml_txt_box = tree.findall('''.//*[@id='plu_02c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_02c
    xml_txt_box = tree.findall('''.//*[@id='plu_03b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_03b
    xml_txt_box = tree.findall('''.//*[@id='plu_03c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_03c
    xml_txt_box = tree.findall('''.//*[@id='plu_04a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_04a
    xml_txt_box = tree.findall('''.//*[@id='plu_05a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_05a
    xml_txt_box = tree.findall('''.//*[@id='plu_06a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_06a
    xml_txt_box = tree.findall('''.//*[@id='plu_06b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_06b
    xml_txt_box = tree.findall('''.//*[@id='plu_06c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_06c
    xml_txt_box = tree.findall('''.//*[@id='plu_07a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_07a
    xml_txt_box = tree.findall('''.//*[@id='plu_08b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_08b
    xml_txt_box = tree.findall('''.//*[@id='plu_08c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_08c
    xml_txt_box = tree.findall('''.//*[@id='plu_091011b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_091011b
    xml_txt_box = tree.findall('''.//*[@id='plu_091011c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_091011c
    xml_txt_box = tree.findall('''.//*[@id='plu_12a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_12a
    xml_txt_box = tree.findall('''.//*[@id='plu_13b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_13b
    xml_txt_box = tree.findall('''.//*[@id='plu_13c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_13c
    xml_txt_box = tree.findall('''.//*[@id='plu_14b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_14b
    xml_txt_box = tree.findall('''.//*[@id='plu_14c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_14c
    xml_txt_box = tree.findall('''.//*[@id='plu_15a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_15a
    xml_txt_box = tree.findall('''.//*[@id='plu_16a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_16a
    xml_txt_box = tree.findall('''.//*[@id='plu_16b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_16b
    xml_txt_box = tree.findall('''.//*[@id='plu_16c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_16c

    # MANAGED WATER USE

    xml_txt_box = tree.findall('''.//*[@id='mwu_01']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_01
    xml_txt_box = tree.findall('''.//*[@id='mwu_02']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_02
    xml_txt_box = tree.findall('''.//*[@id='mwu_03']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_03
    xml_txt_box = tree.findall('''.//*[@id='mwu_04']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_04
    xml_txt_box = tree.findall('''.//*[@id='mwu_05']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_05
    xml_txt_box = tree.findall('''.//*[@id='mwu_06']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_06
    xml_txt_box = tree.findall('''.//*[@id='mwu_07']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_07
    xml_txt_box = tree.findall('''.//*[@id='mwu_08']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_08
    xml_txt_box = tree.findall('''.//*[@id='mwu_09']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_09
    xml_txt_box = tree.findall('''.//*[@id='mwu_10']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_10

    xml_txt_box = tree.findall('''.//*[@id='mwu_01a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_01a
    xml_txt_box = tree.findall('''.//*[@id='mwu_02a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_02a
    xml_txt_box = tree.findall('''.//*[@id='mwu_03a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_03a
    xml_txt_box = tree.findall('''.//*[@id='mwu_04b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_04b
    xml_txt_box = tree.findall('''.//*[@id='mwu_04c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_04c
    xml_txt_box = tree.findall('''.//*[@id='mwu_050607b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_050607b
    xml_txt_box = tree.findall('''.//*[@id='mwu_050607c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_050607c
    xml_txt_box = tree.findall('''.//*[@id='mwu_08b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_08b
    xml_txt_box = tree.findall('''.//*[@id='mwu_08c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_08c
    xml_txt_box = tree.findall('''.//*[@id='mwu_09b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_09b
    xml_txt_box = tree.findall('''.//*[@id='mwu_09c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_09c
    xml_txt_box = tree.findall('''.//*[@id='mwu_10a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_10a
    xml_txt_box = tree.findall('''.//*[@id='mwu_10b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_10b
    xml_txt_box = tree.findall('''.//*[@id='mwu_10c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_10c

    # UTILIZED LAND USE

    xml_txt_box = tree.findall('''.//*[@id='ulu_01']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_01
    xml_txt_box = tree.findall('''.//*[@id='ulu_02']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_02
    xml_txt_box = tree.findall('''.//*[@id='ulu_03']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_03
    xml_txt_box = tree.findall('''.//*[@id='ulu_04']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_04
    xml_txt_box = tree.findall('''.//*[@id='ulu_05']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_05
    xml_txt_box = tree.findall('''.//*[@id='ulu_06']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_06
    xml_txt_box = tree.findall('''.//*[@id='ulu_07']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_07
    xml_txt_box = tree.findall('''.//*[@id='ulu_08']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_08
    xml_txt_box = tree.findall('''.//*[@id='ulu_09']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_09
    xml_txt_box = tree.findall('''.//*[@id='ulu_10']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_10
    xml_txt_box = tree.findall('''.//*[@id='ulu_11']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_11
    xml_txt_box = tree.findall('''.//*[@id='ulu_12']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_12
    xml_txt_box = tree.findall('''.//*[@id='ulu_13']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_13
    xml_txt_box = tree.findall('''.//*[@id='ulu_14']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_14
    xml_txt_box = tree.findall('''.//*[@id='ulu_15']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_15
    xml_txt_box = tree.findall('''.//*[@id='ulu_16']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_16
    xml_txt_box = tree.findall('''.//*[@id='ulu_17']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_17

    xml_txt_box = tree.findall('''.//*[@id='ulu_01a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_01a
    xml_txt_box = tree.findall('''.//*[@id='ulu_02a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_02a
    xml_txt_box = tree.findall('''.//*[@id='ulu_02b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_02b
    xml_txt_box = tree.findall('''.//*[@id='ulu_02c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_02c
    xml_txt_box = tree.findall('''.//*[@id='ulu_03b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_03b
    xml_txt_box = tree.findall('''.//*[@id='ulu_03c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_03c
    xml_txt_box = tree.findall('''.//*[@id='ulu_04b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_04b
    xml_txt_box = tree.findall('''.//*[@id='ulu_04c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_04c
    xml_txt_box = tree.findall('''.//*[@id='ulu_05a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_05a
    xml_txt_box = tree.findall('''.//*[@id='ulu_06a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_06a
    xml_txt_box = tree.findall('''.//*[@id='ulu_07a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_07a
    xml_txt_box = tree.findall('''.//*[@id='ulu_07b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_07b
    xml_txt_box = tree.findall('''.//*[@id='ulu_07c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_07c
    xml_txt_box = tree.findall('''.//*[@id='ulu_08a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_08a
    xml_txt_box = tree.findall('''.//*[@id='ulu_09b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_09b
    xml_txt_box = tree.findall('''.//*[@id='ulu_09c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_09c
    xml_txt_box = tree.findall('''.//*[@id='ulu_101112b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_101112b
    xml_txt_box = tree.findall('''.//*[@id='ulu_101112c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_101112c
    xml_txt_box = tree.findall('''.//*[@id='ulu_13a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_13a
    xml_txt_box = tree.findall('''.//*[@id='ulu_14b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_14b
    xml_txt_box = tree.findall('''.//*[@id='ulu_14c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_14c
    xml_txt_box = tree.findall('''.//*[@id='ulu_15b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_15b
    xml_txt_box = tree.findall('''.//*[@id='ulu_15c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_15c
    xml_txt_box = tree.findall('''.//*[@id='ulu_16a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_16a
    xml_txt_box = tree.findall('''.//*[@id='ulu_17a']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_17a
    xml_txt_box = tree.findall('''.//*[@id='ulu_17b']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_17b
    xml_txt_box = tree.findall('''.//*[@id='ulu_17c']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_17c

    # Inner circle

    xml_txt_box = tree.findall('''.//*[@id='mlu_incremental']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_incremental
    xml_txt_box = tree.findall('''.//*[@id='mlu_landscape']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mlu_landscape

    xml_txt_box = tree.findall('''.//*[@id='plu_incremental']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_incremental
    xml_txt_box = tree.findall('''.//*[@id='plu_landscape']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % plu_landscape

    xml_txt_box = tree.findall('''.//*[@id='mwu_incremental']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_incremental
    xml_txt_box = tree.findall('''.//*[@id='mwu_landscape']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % mwu_landscape

    xml_txt_box = tree.findall('''.//*[@id='ulu_incremental']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_incremental
    xml_txt_box = tree.findall('''.//*[@id='ulu_landscape']''')[0]
    xml_txt_box.getchildren()[0].text = '%.0f' % ulu_landscape

    # svg to string
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    root = tree.getroot()
    svg_string = ET.tostring(root, encoding='UTF-8', method='xml')

    # Export svg to png
    img_out = Image(blob=svg_string, resolution=300)
    img_out.format = 'jpg'
    img_out.save(filename=output)

    # Return
    return output
