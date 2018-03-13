# -*- coding: utf-8 -*-
"""
Authors: Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Sheets/sheet1
"""

import os
import time
import pandas as pd
import xml.etree.ElementTree as ET
import subprocess

def create_sheet1(basin, period, units, data, output, template=False):
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

    Example:
    from wa.Sheets import *
    create_sheet1(basin='Incomati', period='2005-2010', units='km3/year',
                  data=r'C:\Sheets\csv\Sample_sheet1.csv',
                  output=r'C:\Sheets\sheet_1.jpg')
    """

    # Read table

    df = pd.read_csv(data, sep=';')

    # Data frames

    df_i = df.loc[df.CLASS == "INFLOW"]
    df_s = df.loc[df.CLASS == "STORAGE"]
    df_o = df.loc[df.CLASS == "OUTFLOW"]

    # Inflow data

    rainfall = float(df_i.loc[(df_i.SUBCLASS == "PRECIPITATION") &
                              (df_i.VARIABLE == "Rainfall")].VALUE)
    snowfall = float(df_i.loc[(df_i.SUBCLASS == "PRECIPITATION") &
                              (df_i.VARIABLE == "Snowfall")].VALUE)
    p_recy = float(df_i.loc[(df_i.SUBCLASS == "PRECIPITATION") &
                   (df_i.VARIABLE == "Precipitation recycling")].VALUE)

    sw_mrs_i = float(df_i.loc[(df_i.SUBCLASS == "SURFACE WATER") &
                              (df_i.VARIABLE == "Main riverstem")].VALUE)
    sw_tri_i = float(df_i.loc[(df_i.SUBCLASS == "SURFACE WATER") &
                              (df_i.VARIABLE == "Tributaries")].VALUE)
    sw_usw_i = float(df_i.loc[(df_i.SUBCLASS == "SURFACE WATER") &
                     (df_i.VARIABLE == "Utilized surface water")].VALUE)
    sw_flo_i = float(df_i.loc[(df_i.SUBCLASS == "SURFACE WATER") &
                              (df_i.VARIABLE == "Flood")].VALUE)

    gw_nat_i = float(df_i.loc[(df_i.SUBCLASS == "GROUNDWATER") &
                              (df_i.VARIABLE == "Natural")].VALUE)
    gw_uti_i = float(df_i.loc[(df_i.SUBCLASS == "GROUNDWATER") &
                              (df_i.VARIABLE == "Utilized")].VALUE)

    q_desal = float(df_i.loc[(df_i.SUBCLASS == "OTHER") &
                             (df_i.VARIABLE == "Desalinized")].VALUE)

    # Storage data

    surf_sto = float(df_s.loc[(df_s.SUBCLASS == "CHANGE") &
                              (df_s.VARIABLE == "Surface storage")].VALUE)
    sto_sink = float(df_s.loc[(df_s.SUBCLASS == "CHANGE") &
                              (df_s.VARIABLE == "Storage in sinks")].VALUE)

    # Outflow data

    et_l_pr = float(df_o.loc[(df_o.SUBCLASS == "ET LANDSCAPE") &
                             (df_o.VARIABLE == "Protected")].VALUE)
    et_l_ut = float(df_o.loc[(df_o.SUBCLASS == "ET LANDSCAPE") &
                             (df_o.VARIABLE == "Utilized")].VALUE)
    et_l_mo = float(df_o.loc[(df_o.SUBCLASS == "ET LANDSCAPE") &
                             (df_o.VARIABLE == "Modified")].VALUE)
    et_l_ma = float(df_o.loc[(df_o.SUBCLASS == "ET LANDSCAPE") &
                             (df_o.VARIABLE == "Managed")].VALUE)

    et_u_pr = float(df_o.loc[(df_o.SUBCLASS == "ET UTILIZED FLOW") &
                             (df_o.VARIABLE == "Protected")].VALUE)
    et_u_ut = float(df_o.loc[(df_o.SUBCLASS == "ET UTILIZED FLOW") &
                             (df_o.VARIABLE == "Utilized")].VALUE)
    et_u_mo = float(df_o.loc[(df_o.SUBCLASS == "ET UTILIZED FLOW") &
                             (df_o.VARIABLE == "Modified")].VALUE)
    et_u_ma = float(df_o.loc[(df_o.SUBCLASS == "ET UTILIZED FLOW") &
                             (df_o.VARIABLE == "Managed")].VALUE)

    et_manmade = float(df_o.loc[(df_o.SUBCLASS == "ET INCREMENTAL") &
                                (df_o.VARIABLE == "Manmade")].VALUE)
    et_natural = float(df_o.loc[(df_o.SUBCLASS == "ET INCREMENTAL") &
                                (df_o.VARIABLE == "Natural")].VALUE)

    sw_mrs_o = float(df_o.loc[(df_o.SUBCLASS == "SURFACE WATER") &
                              (df_o.VARIABLE == "Main riverstem")].VALUE)
    sw_tri_o = float(df_o.loc[(df_o.SUBCLASS == "SURFACE WATER") &
                              (df_o.VARIABLE == "Tributaries")].VALUE)
    sw_usw_o = float(df_o.loc[(df_o.SUBCLASS == "SURFACE WATER") &
                     (df_o.VARIABLE == "Utilized surface water")].VALUE)
    sw_flo_o = float(df_o.loc[(df_o.SUBCLASS == "SURFACE WATER") &
                              (df_o.VARIABLE == "Flood")].VALUE)

    gw_nat_o = float(df_o.loc[(df_o.SUBCLASS == "GROUNDWATER") &
                              (df_o.VARIABLE == "Natural")].VALUE)
    gw_uti_o = float(df_o.loc[(df_o.SUBCLASS == "GROUNDWATER") &
                              (df_o.VARIABLE == "Utilized")].VALUE)

    basin_transfers = float(df_o.loc[(df_o.SUBCLASS == "SURFACE WATER") &
                            (df_o.VARIABLE == "Interbasin transfer")].VALUE)
    non_uti = float(df_o.loc[(df_o.SUBCLASS == "OTHER") &
                             (df_o.VARIABLE == "Non-utilizable")].VALUE)
    other_o = float(df_o.loc[(df_o.SUBCLASS == "OTHER") &
                             (df_o.VARIABLE == "Other")].VALUE)

    com_o = float(df_o.loc[(df_o.SUBCLASS == "RESERVED") &
                           (df_o.VARIABLE == "Commited")].VALUE)
    nav_o = float(df_o.loc[(df_o.SUBCLASS == "RESERVED") &
                           (df_o.VARIABLE == "Navigational")].VALUE)
    env_o = float(df_o.loc[(df_o.SUBCLASS == "RESERVED") &
                           (df_o.VARIABLE == "Environmental")].VALUE)

    # Calculations & modify svg
    if not template:
        path = os.path.dirname(os.path.abspath(__file__))
        svg_template_path = os.path.join(path, 'svg', 'sheet_1.svg')
    else:
        svg_template_path = os.path.abspath(template)

    tree = ET.parse(svg_template_path)

    # Titles

    xml_txt_box = tree.findall('''.//*[@id='basin']''')[0]
    xml_txt_box.getchildren()[0].text = 'Basin: ' + basin

    xml_txt_box = tree.findall('''.//*[@id='period']''')[0]
    xml_txt_box.getchildren()[0].text = 'Period: ' + period

    xml_txt_box = tree.findall('''.//*[@id='units']''')[0]
    xml_txt_box.getchildren()[0].text = 'Sheet 1: Resource Base (' + units + ')'

    # Grey box

    p_advec = rainfall + snowfall
    q_sw_in = sw_mrs_i + sw_tri_i + sw_usw_i + sw_flo_i
    q_gw_in = gw_nat_i + gw_uti_i

    external_in = p_advec + q_desal + q_sw_in + q_gw_in
    gross_inflow = external_in + p_recy

    delta_s = surf_sto + sto_sink

    xml_txt_box = tree.findall('''.//*[@id='external_in']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % external_in

    xml_txt_box = tree.findall('''.//*[@id='p_advec']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % p_advec

    xml_txt_box = tree.findall('''.//*[@id='q_desal']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % q_desal

    xml_txt_box = tree.findall('''.//*[@id='q_sw_in']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % q_sw_in

    xml_txt_box = tree.findall('''.//*[@id='q_gw_in']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % q_gw_in

    xml_txt_box = tree.findall('''.//*[@id='p_recycled']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % p_recy

    xml_txt_box = tree.findall('''.//*[@id='gross_inflow']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % gross_inflow

    if delta_s > 0:
        xml_txt_box = tree.findall('''.//*[@id='pos_delta_s']''')[0]
        xml_txt_box.getchildren()[0].text = '%.1f' % delta_s

        xml_txt_box = tree.findall('''.//*[@id='neg_delta_s']''')[0]
        xml_txt_box.getchildren()[0].text = '0.0'
    else:
        xml_txt_box = tree.findall('''.//*[@id='pos_delta_s']''')[0]
        xml_txt_box.getchildren()[0].text = '0.0'

        xml_txt_box = tree.findall('''.//*[@id='neg_delta_s']''')[0]
        xml_txt_box.getchildren()[0].text = '%.1f' % -delta_s

    # Pink box

    net_inflow = gross_inflow + delta_s

    xml_txt_box = tree.findall('''.//*[@id='net_inflow']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % net_inflow

    # Light-green box

    land_et = et_l_pr + et_l_ut + et_l_mo + et_l_ma

    xml_txt_box = tree.findall('''.//*[@id='landscape_et']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % land_et

    xml_txt_box = tree.findall('''.//*[@id='green_protected']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_l_pr

    xml_txt_box = tree.findall('''.//*[@id='green_utilized']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_l_ut

    xml_txt_box = tree.findall('''.//*[@id='green_modified']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_l_mo

    xml_txt_box = tree.findall('''.//*[@id='green_managed']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_l_ma

    xml_txt_box = tree.findall('''.//*[@id='et_rainfall']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % land_et

    # Blue box (center)

    exploitable_water = net_inflow - land_et
    reserved_outflow = max(com_o, nav_o, env_o)

    available_water = exploitable_water - non_uti - reserved_outflow

    utilized_flow = et_u_pr + et_u_ut + et_u_mo + et_u_ma
    utilizable_outflow = available_water - utilized_flow

    inc_et = et_manmade + et_natural

    non_cons_water = utilizable_outflow + non_uti + reserved_outflow

    non_rec_flow = et_u_pr + et_u_ut + et_u_mo + et_u_ma - inc_et - other_o

    xml_txt_box = tree.findall('''.//*[@id='incremental_et']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % inc_et

    xml_txt_box = tree.findall('''.//*[@id='exploitable_water']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % exploitable_water

    xml_txt_box = tree.findall('''.//*[@id='available_water']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % available_water

    xml_txt_box = tree.findall('''.//*[@id='utilized_flow']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % utilized_flow

    xml_txt_box = tree.findall('''.//*[@id='blue_protected']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_u_pr

    xml_txt_box = tree.findall('''.//*[@id='blue_utilized']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_u_ut

    xml_txt_box = tree.findall('''.//*[@id='blue_modified']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_u_mo

    xml_txt_box = tree.findall('''.//*[@id='blue_managed']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_u_ma

    xml_txt_box = tree.findall('''.//*[@id='utilizable_outflow']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % utilizable_outflow

    xml_txt_box = tree.findall('''.//*[@id='non-utilizable_outflow']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % non_uti

    xml_txt_box = tree.findall('''.//*[@id='reserved_outflow_max']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % reserved_outflow

    xml_txt_box = tree.findall('''.//*[@id='non-consumed_water']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % non_cons_water

    xml_txt_box = tree.findall('''.//*[@id='manmade']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_manmade

    xml_txt_box = tree.findall('''.//*[@id='natural']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % et_natural

    xml_txt_box = tree.findall('''.//*[@id='other']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % other_o

    xml_txt_box = tree.findall('''.//*[@id='non-recoverable_flow']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % non_rec_flow

    # Blue box (right)

    outflow = non_cons_water + non_rec_flow + basin_transfers

    q_sw_out = sw_mrs_o + sw_tri_o + sw_usw_o + sw_flo_o
    q_gw_out = gw_nat_o + gw_uti_o

    xml_txt_box = tree.findall('''.//*[@id='outflow']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % outflow

    xml_txt_box = tree.findall('''.//*[@id='q_sw_outlet']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % q_sw_out

    xml_txt_box = tree.findall('''.//*[@id='q_sw_out']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % basin_transfers

    xml_txt_box = tree.findall('''.//*[@id='q_gw_out']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % q_gw_out

    # Dark-green box

    consumed_water = land_et + utilized_flow
    depleted_water = consumed_water - p_recy - non_rec_flow
    external_out = depleted_water + outflow

    xml_txt_box = tree.findall('''.//*[@id='et_recycled']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % p_recy

    xml_txt_box = tree.findall('''.//*[@id='consumed_water']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % consumed_water

    xml_txt_box = tree.findall('''.//*[@id='depleted_water']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % depleted_water

    xml_txt_box = tree.findall('''.//*[@id='external_out']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % external_out

    xml_txt_box = tree.findall('''.//*[@id='et_out']''')[0]
    xml_txt_box.getchildren()[0].text = '%.1f' % depleted_water

    # svg to string
    ET.register_namespace("", "http://www.w3.org/2000/svg")
#    root = tree.getroot()
#    svg_string = ET.tostring(root, encoding='UTF-8', method='xml')

    # Export svg to png
#    from wand.image import Image
#    img_out = Image(blob=svg_string, resolution=300)
#    img_out.format = 'jpg'
#    img_out.save(filename=output)
    
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
