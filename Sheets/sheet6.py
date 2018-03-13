# -*- coding: utf-8 -*-
"""
Authors: Bert Coerver
         UNESCO-IHE 2017
Contact: b.coerver@un-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Sheets/sheet6
"""
import os
import pandas as pd
import xml.etree.ElementTree as ET
import subprocess
import time

def create_sheet6(basin, period, unit, data, output, template=False):
    """
    Create sheet 6 of the Water Accounting Plus framework.
    
    Parameters
    ----------
    basin : str
        The name of the basin.
    period : str
        The period of analysis.
    units : str
        the unit of the data on sheet 6.
    data : str
        csv file that contains the water data. The csv file has to
        follow an specific format. A sample csv is available here:
        https://github.com/wateraccounting/wa/tree/master/Sheets/csv
    output : list
        Filehandles pointing to the jpg files to be created.
    template : str or boolean, optional
        the svg file of the sheet. False
        uses the standard svg files. Default is False.

    Examples
    --------
    >>> from wa.Sheets import *
    >>> create_sheet6(basin='Helmand', period='2007-2011',
                  units = 'km3/yr',
                  data = r'C:\Sheets\csv\Sample_sheet6.csv',
                  output = r'C:\Sheets\sheet_6.png')
    """
    df1 = pd.read_csv(data, sep=';')
    
    p1 = dict()
    
    p1['VR_forest'] = float(df1.loc[(df1.TYPE == 'Forests') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_shrubland'] = float(df1.loc[(df1.TYPE == 'Shrubland') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_naturalgrassland'] = float(df1.loc[(df1.TYPE == 'Natural Grasslands') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_naturalwaterbodies'] = float(df1.loc[(df1.TYPE == 'Natural Water Bodies') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_wetlands'] = float(df1.loc[(df1.TYPE == 'Wetlands') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_rainfedcrops'] = float(df1.loc[(df1.TYPE == 'Rainfed Crops') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_forestplantations'] = float(df1.loc[(df1.TYPE == 'Forest Plantations') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_irrigatedcrops'] = float(df1.loc[(df1.TYPE == 'Irrigated crops') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_managedwaterbodies'] = float(df1.loc[(df1.TYPE == 'Managed water bodies') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_residential'] = float(df1.loc[(df1.TYPE == 'Residential') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_industry'] = float(df1.loc[(df1.TYPE == 'Industry') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_other'] = float(df1.loc[(df1.TYPE == 'Other (Non-Manmade)') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VR_managedaquiferrecharge'] = float(df1.loc[(df1.TYPE == 'NON_LU_SPECIFIC') & (df1.SUBTYPE == 'ManagedAquiferRecharge')].VALUE)
    p1['VR_glaciers'] = float(df1.loc[(df1.TYPE == 'Glaciers') & (df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    
    p1['VGW_forest'] = float(df1.loc[(df1.TYPE == 'Forests') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_shrubland'] = float(df1.loc[(df1.TYPE == 'Shrubland') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_rainfedcrops'] = float(df1.loc[(df1.TYPE == 'Rainfed Crops') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_forestplantations'] = float(df1.loc[(df1.TYPE == 'Forest Plantations') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_wetlands'] = float(df1.loc[(df1.TYPE == 'Wetlands') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_naturalgrassland'] = float(df1.loc[(df1.TYPE == 'Natural Grasslands') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_othernatural'] = float(df1.loc[(df1.TYPE == 'Other (Non-Manmade)') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_irrigatedcrops'] = float(df1.loc[(df1.TYPE == 'Irrigated crops') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_industry'] = float(df1.loc[(df1.TYPE == 'Industry') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_aquaculture'] = float(df1.loc[(df1.TYPE == 'Aquaculture') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_residential'] = float(df1.loc[(df1.TYPE == 'Residential') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_greenhouses'] = float(df1.loc[(df1.TYPE == 'Greenhouses') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    p1['VGW_othermanmade'] = float(df1.loc[(df1.TYPE == 'Other') & (df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    
    p1['RFG_irrigatedcrops'] = float(df1.loc[(df1.TYPE == 'Irrigated crops') & (df1.SUBTYPE == 'RETURN_FLOW_GROUNDWATER')].VALUE)
    p1['RFG_industry'] = float(df1.loc[(df1.TYPE == 'Industry') & (df1.SUBTYPE == 'RETURN_FLOW_GROUNDWATER')].VALUE)
    p1['RFG_aquaculture'] = float(df1.loc[(df1.TYPE == 'Aquaculture') & (df1.SUBTYPE == 'RETURN_FLOW_GROUNDWATER')].VALUE)
    p1['RFG_residential'] = float(df1.loc[(df1.TYPE == 'Residential') & (df1.SUBTYPE == 'RETURN_FLOW_GROUNDWATER')].VALUE)
    p1['RFG_greenhouses'] = float(df1.loc[(df1.TYPE == 'Greenhouses') & (df1.SUBTYPE == 'RETURN_FLOW_GROUNDWATER')].VALUE)
    p1['RFG_other'] = float(df1.loc[(df1.TYPE == 'Other') & (df1.SUBTYPE == 'RETURN_FLOW_GROUNDWATER')].VALUE)
    
    p1['RFS_forest'] = float(df1.loc[(df1.TYPE == 'Forests') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_shrubland'] = float(df1.loc[(df1.TYPE == 'Shrubland') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_rainfedcrops'] = float(df1.loc[(df1.TYPE == 'Rainfed Crops') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_forestplantations'] = float(df1.loc[(df1.TYPE == 'Forest Plantations') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_wetlands'] = float(df1.loc[(df1.TYPE == 'Wetlands') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_naturalgrassland'] = float(df1.loc[(df1.TYPE == 'Natural Grasslands') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_othernatural'] = float(df1.loc[(df1.TYPE == 'Other (Non-Manmade)') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_irrigatedcrops'] = float(df1.loc[(df1.TYPE == 'Irrigated crops') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_industry'] = float(df1.loc[(df1.TYPE == 'Industry') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_aquaculture'] = float(df1.loc[(df1.TYPE == 'Aquaculture') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_residential'] = float(df1.loc[(df1.TYPE == 'Residential') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_greenhouses'] = float(df1.loc[(df1.TYPE == 'Greenhouses') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    p1['RFS_othermanmade'] = float(df1.loc[(df1.TYPE == 'Other') & (df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    
    p1['VRtotal_natural'] = pd.np.nansum(df1.loc[(df1.SUBTYPE == 'VERTICAL_RECHARGE')].VALUE)
    p1['VRtotal_manmade'] = float(df1.loc[(df1.SUBTYPE == 'ManagedAquiferRecharge')].VALUE)
    p1['VRtotal'] = pd.np.nansum([p1['VRtotal_natural'], p1['VRtotal_manmade']])
    
    p1['CRtotal'] = float(df1.loc[(df1.SUBTYPE == 'CapillaryRise')].VALUE)
    #p1['delta_S'] = float(df1.loc[(df1.SUBTYPE == 'DeltaS')].VALUE)
    
    p1['VGWtotal_natural'] = pd.np.nansum([p1['VGW_forest'], p1['VGW_shrubland'], p1['VGW_rainfedcrops'], p1['VGW_forestplantations'], p1['VGW_wetlands'], p1['VGW_naturalgrassland'], p1['VGW_othernatural']])
    p1['VGWtotal_manmade'] = pd.np.nansum([p1['VGW_irrigatedcrops'],p1['VGW_industry'],p1['VGW_aquaculture'],p1['VGW_residential'],p1['VGW_greenhouses'],p1['VGW_othermanmade']])
    p1['VGWtotal'] = pd.np.nansum(df1.loc[(df1.SUBTYPE == 'VERTICAL_GROUNDWATER_WITHDRAWALS')].VALUE)
    
    p1['RFGtotal_manmade'] = p1['RFGtotal'] = pd.np.nansum(df1.loc[(df1.SUBTYPE == 'RETURN_FLOW_GROUNDWATER')].VALUE)
    
    p1['RFStotal_natural'] = pd.np.nansum([p1['RFS_forest'], p1['RFS_shrubland'], p1['RFS_rainfedcrops'], p1['RFS_forestplantations'], p1['RFS_wetlands'], p1['RFS_naturalgrassland'], p1['RFS_othernatural']])
    
    p1['RFStotal_manmade'] = pd.np.nansum([p1['RFS_irrigatedcrops'],p1['RFS_industry'],p1['RFS_aquaculture'],p1['RFS_residential'],p1['RFS_greenhouses'],p1['RFS_othermanmade']])
    
    p1['RFStotal'] = pd.np.nansum(df1.loc[(df1.SUBTYPE == 'RETURN_FLOW_SURFACEWATER')].VALUE)
    
    p1['HGI'] = float(df1.loc[(df1.TYPE == 'NON_LU_SPECIFIC') & (df1.SUBTYPE == 'GWInflow')].VALUE)
    p1['HGO'] = float(df1.loc[(df1.TYPE == 'NON_LU_SPECIFIC') & (df1.SUBTYPE == 'GWOutflow')].VALUE)
    p1['baseflow'] = float(df1.loc[(df1.TYPE == 'NON_LU_SPECIFIC') & (df1.SUBTYPE == 'Baseflow')].VALUE)
    
    p1['delta_S'] = p1['VRtotal'] - p1['CRtotal'] - p1['VGWtotal'] + p1['RFGtotal_manmade'] + p1['RFStotal'] - p1['baseflow']
    #p1['CRtotal'] = p1['VRtotal'] - p1['VGWtotal'] + p1['RFGtotal_manmade'] + p1['RFStotal'] - p1['baseflow'] - p1['delta_S']

    if not template:
        path = os.path.dirname(os.path.abspath(__file__))
        svg_template_path_1 = os.path.join(path, 'svg', 'sheet_6.svg')
    else:
        svg_template_path_1 = os.path.abspath(template)
    
    tree1 = ET.parse(svg_template_path_1)
    xml_txt_box = tree1.findall('''.//*[@id='basin']''')[0]
    xml_txt_box.getchildren()[0].text = 'Basin: ' + basin
    
    xml_txt_box = tree1.findall('''.//*[@id='period']''')[0]
    xml_txt_box.getchildren()[0].text = 'Period: ' + period
    
    xml_txt_box = tree1.findall('''.//*[@id='unit']''')[0]
    xml_txt_box.getchildren()[0].text = 'Sheet 6: Groundwater ({0})'.format(unit)
    
    for key in p1.keys():
        xml_txt_box = tree1.findall(".//*[@id='{0}']".format(key))[0]
        if not pd.isnull(p1[key]):
            xml_txt_box.getchildren()[0].text = '%.1f' % p1[key]
        else:
            xml_txt_box.getchildren()[0].text = '-'
    
    ET.register_namespace("", "http://www.w3.org/2000/svg")

    tempout_path = output.replace('.png', '_temporary.svg')
    tree1.write(tempout_path)
    
    subprocess.call(['C:\Program Files\Inkscape\inkscape.exe',tempout_path,'--export-png='+output, '-d 300'])
    time.sleep(10)
    os.remove(tempout_path)