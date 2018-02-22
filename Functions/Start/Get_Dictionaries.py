# -*- coding: utf-8 -*-
"""
Authors: Bert Coerver
         UNESCO-IHE 2017
Contact: b.coerver@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Two
"""

def get_lulcs(lulc_version = '4.0'):

    lulc_v40 = {
    'legend': ['Code', 'Landuse', 'Description', 'Beneficial T [%]', 'Beneficial E [%]', 'Beneficial I [%]', 'Agriculture [%]', 'Environment [%]', 'Economic [%]', 'Energy [%]', 'Leisure [%]'],
    0: ['X','X','X',0.,0.,0.,0.,0.,0.,0.,0.],
    1: ['PLU1', 'Protected', 'Protected forests', 100.0, 100.0, 0.0, 0.0, 85.0, 0.0, 0.0, 15.0], 
    2: ['PLU2', 'Protected', 'Protected shrubland', 100.0, 100.0, 0.0, 0.0, 85.0, 0.0, 0.0, 15.0], 
    3: ['PLU3', 'Protected', 'Protected natural grasslands', 100.0, 100.0, 0.0, 0.0, 85.0, 0.0, 0.0, 15.0], 
    4: ['PLU4', 'Protected', 'Protected natural waterbodies', 100.0, 100.0, 0.0, 0.0, 85.0, 0.0, 0.0, 15.0], 
    5: ['PLU5', 'Protected', 'Protected wetlands', 100.0, 100.0, 0.0, 0.0, 85.0, 0.0, 0.0, 15.0], 
    6: ['PLU6', 'Protected', 'Glaciers', 0.0, 100.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0], 
    7: ['PLU7', 'Protected', 'Protected other', 100.0, 100.0, 0.0, 0.0, 85.0, 0.0, 0.0, 15.0], 
    8: ['ULU1', 'Utilized', 'Closed deciduous forest', 100.0, 0.0, 0.0, 5.0, 90.0, 0.0, 0.0, 5.0], 
    9: ['ULU2', 'Utilized', 'Open deciduous forest', 100.0, 0.0, 0.0, 5.0, 90.0, 0.0, 0.0, 5.0], 
    10: ['ULU3', 'Utilized', 'Closed evergreen forest', 100.0, 0.0, 0.0, 5.0, 90.0, 0.0, 0.0, 5.0], 
    11: ['ULU4', 'Utilized', 'Open evergreen forest', 100.0, 0.0, 0.0, 5.0, 90.0, 0.0, 0.0, 5.0], 
    12: ['ULU5', 'Utilized', 'Closed savanna', 100.0, 0.0, 0.0, 5.0, 80.0, 0.0, 10.0, 5.0], 
    13: ['ULU6', 'Utilized', 'Open savanna', 100.0, 0.0, 0.0, 10.0, 80.0, 0.0, 5.0, 5.0], 
    14: ['ULU7', 'Utilized', 'Shrub land & mesquite', 100.0, 0.0, 0.0, 5.0, 85.0, 0.0, 10.0, 0.0], 
    15: ['ULU8', 'Utilized', ' Herbaceous cover', 100.0, 0.0, 0.0, 5.0, 95.0, 0.0, 0.0, 0.0], 
    16: ['ULU9', 'Utilized', 'Meadows & open grassland', 100.0, 0.0, 0.0, 60.0, 30.0, 0.0, 0.0, 10.0], 
    17: ['ULU10', 'Utilized', 'Riparian corridor', 100.0, 0.0, 0.0, 10.0, 60.0, 10.0, 0.0, 20.0], 
    18: ['ULU11', 'Utilized', 'Deserts', 100.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0], 
    19: ['ULU12', 'Utilized', 'Wadis', 100.0, 0.0, 0.0, 15.0, 80.0, 0.0, 0.0, 5.0], 
    20: ['ULU13', 'Utilized', 'Natural alpine pastures', 100.0, 0.0, 0.0, 70.0, 20.0, 0.0, 0.0, 10.0], 
    21: ['ULU14', 'Utilized', 'Rocks & gravel & stones & boulders', 100.0, 0.0, 0.0, 0.0, 95.0, 0.0, 0.0, 5.0], 
    22: ['ULU15', 'Utilized', 'Permafrosts', 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0], 
    23: ['ULU16', 'Utilized', 'Brooks & rivers & waterfalls', 0.0, 50.0, 0.0, 25.0, 55.0, 5.0, 0.0, 15.0], 
    24: ['ULU17', 'Utilized', 'Natural lakes\xa0', 0.0, 50.0, 0.0, 25.0, 40.0, 5.0, 0.0, 30.0], 
    25: ['ULU18', 'Utilized', 'Flood plains & mudflats', 100.0, 50.0, 0.0, 40.0, 60.0, 0.0, 0.0, 0.0], 
    26: ['ULU19', 'Utilized', 'Saline sinks & playas & salinized soil', 100.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0], 
    27: ['ULU20', 'Utilized', 'Bare soil', 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0], 
    28: ['ULU21', 'Utilized', 'Waste land', 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0], 
    29: ['ULU22', 'Utilized', 'Moorland', 100.0, 0.0, 0.0, 5.0, 80.0, 0.0, 0.0, 15.0], 
    30: ['ULU23', 'Utilized', 'Wetland', 100.0, 50.0, 0.0, 5.0, 80.0, 0.0, 5.0, 10.0], 
    31: ['ULU24', 'Utilized', 'Mangroves', 100.0, 50.0, 0.0, 5.0, 80.0, 0.0, 5.0, 10.0], 
    32: ['ULU25', 'Utilized', 'Alien invasive species', 0.0, 0.0, 0.0, 0.0, 60.0, 0.0, 10.0, 30.0], 
    33: ['MLU1', 'Modified', 'Forest plantations', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    34: ['MLU2', 'Modified', 'Rainfed production pastures', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    35: ['MLU3', 'Modified', 'Rainfed crops - cereals', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    36: ['MLU4', 'Modified', 'Rainfed crops - root/tuber', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    37: ['MLU5', 'Modified', 'Rainfed crops - legumious', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    38: ['MLU6', 'Modified', 'Rainfed crops - sugar', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    39: ['MLU7', 'Modified', 'Rainfed crops - fruit and nuts', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    40: ['MLU8', 'Modified', 'Rainfed crops - vegetables and melons', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    41: ['MLU9', 'Modified', 'Rainfed crops - oilseed', 100.0, 0.0, 0.0, 45.0, 0.0, 15.0, 40.0, 0.0], 
    42: ['MLU10', 'Modified', 'Rainfed crops - beverage and spice', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    43: ['MLU11', 'Modified', 'Rainfed crops - other ', 100.0, 0.0, 0.0, 80.0, 0.0, 20.0, 0.0, 0.0], 
    44: ['MLU12', 'Modified', 'Mixed species agro-forestry', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    45: ['MLU13', 'Modified', 'Fallow & idle land', 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0], 
    46: ['MLU14', 'Modified', 'Dump sites & deposits', 0.0, 0.0, 0.0, 0.0, 60.0, 40.0, 0.0, 0.0], 
    47: ['MLU15', 'Modified', 'Rainfed homesteads and gardens (urban cities) - outdoor', 100.0, 0.0, 0.0, 0.0, 0.0, 35.0, 0.0, 65.0], 
    48: ['MLU16', 'Modified', 'Rainfed homesteads and gardens (rural villages) - outdoor', 100.0, 0.0, 0.0, 0.0, 0.0, 35.0, 0.0, 65.0], 
    49: ['MLU17', 'Modified', 'Rainfed industry parks - outdoor', 100.0, 0.0, 0.0, 0.0, 0.0, 50.0, 0.0, 50.0], 
    50: ['MLU18', 'Modified', 'Rainfed parks (leisure & sports)', 100.0, 0.0, 0.0, 0.0, 15.0, 0.0, 0.0, 85.0], 
    51: ['MLU19', 'Modified', 'Rural paved surfaces (lots, roads, lanes)', 100.0, 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0], 
    52: ['MWU1', 'Managed', 'Irrigated forest plantations', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    53: ['MWU2', 'Managed', 'Irrigated production pastures', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    54: ['MWU3', 'Managed', 'Irrigated crops - cereals', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    55: ['MWU4', 'Managed', 'Irrigated crops - root/tubers', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    56: ['MWU5', 'Managed', 'Irrigated crops - legumious', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    57: ['MWU6', 'Managed', 'Irrigated crops - sugar', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    58: ['MWU7', 'Managed', 'Irrigated crops - fruit and nuts', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    59: ['MWU8', 'Managed', 'Irrigated crops - vegetables and melons', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    60: ['MWU9', 'Managed', 'Irrigated crops - Oilseed', 100.0, 0.0, 0.0, 65.0, 0.0, 10.0, 25.0, 0.0], 
    61: ['MWU10', 'Managed', 'Irrigated crops - beverage and spice', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    62: ['MWU11', 'Managed', 'Irrigated crops - other', 100.0, 0.0, 0.0, 80.0, 0.0, 20.0, 0.0, 0.0], 
    63: ['MWU12', 'Managed', 'Managed water bodies (reservoirs, canals, harbors, tanks)', 0.0, 100.0, 0.0, 35.0, 5.0, 30.0, 20.0, 10.0], 
    64: ['MWU13', 'Managed', 'Greenhouses - indoor', 100.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0], 
    65: ['MWU14', 'Managed', 'Aquaculture', 0.0, 100.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    66: ['MWU15', 'Managed', 'Domestic households - indoor (sanitation)', 0.0, 100.0, 0.0, 0.0, 0.0, 35.0, 0.0, 65.0], 
    67: ['MWU16', 'Managed', 'Manufacturing & commercial industry - indoor', 0.0, 100.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0], 
    68: ['MWU17', 'Managed', 'Irrigated homesteads and gardens (urban cities) - outdoor', 100.0, 0.0, 0.0, 30.0, 5.0, 15.0, 0.0, 50.0], 
    69: ['MWU18', 'Managed', 'Irrigated homesteads and gardens (rural villages) - outdoor', 100.0, 0.0, 0.0, 30.0, 5.0, 15.0, 0.0, 50.0], 
    70: ['MWU19', 'Managed', 'Irrigated industry parks - outdoor', 100.0, 0.0, 0.0, 0.0, 15.0, 35.0, 0.0, 50.0], 
    71: ['MWU20', 'Managed', 'Irrigated parks (leisure, sports)', 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0], 
    72: ['MWU21', 'Managed', 'Urban paved Surface (lots, roads, lanes)', 100.0, 0.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0], 
    73: ['MWU22', 'Managed', 'Livestock and domestic husbandry', 100.0, 0.0, 0.0, 90.0, 0.0, 10.0, 0.0, 0.0], 
    74: ['MWU23', 'Managed', 'Managed wetlands & swamps', 100.0, 50.0, 0.0, 0.0, 65.0, 10.0, 0.0, 25.0], 
    75: ['MWU24', 'Managed', 'Managed other inundation areas', 100.0, 50.0, 0.0, 0.0, 55.0, 20.0, 0.0, 25.0], 
    76: ['MWU25', 'Managed', 'Mining/ quarry & shale exploiration', 100.0, 50.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0], 
    77: ['MWU26', 'Managed', 'Evaporation ponds', 0.0, 100.0, 0.0, 0.0, 75.0, 25.0, 0.0, 0.0], 
    78: ['MWU27', 'Managed', 'Waste water treatment plants', 0.0, 100.0, 0.0, 0.0, 55.0, 45.0, 0.0, 0.0], 
    79: ['MWU28', 'Managed', 'Hydropower plants', 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 97.5, 2.5], 
    80: ['MWU29', 'Managed', 'Thermal power plants', 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 100.0, 0.0]
    }
    
    lulc = dict()
    lulc['4.0'] = lulc_v40
    
    return lulc[lulc_version]

def get_sheet2_classes(version = '1.0'):
    sheet2_classes_v10 = {
    'PROTECTED':    {'Forest': [1],
                    'Shrubland': [2],
                    'Natural grasslands':[3],
                    'Natural water bodies':[4],
                    'Wetlands':[5],
                    'Glaciers':[6],
                    'Others':[7]
                    },
    'UTILIZED':     {'Forest':[8,9,10,11],
                    'Shrubland':[14],
                    'Natural grasslands':[12,13,15,16,20],
                    'Natural water bodies':[23,24,],
                    'Wetlands':[17,19,25,30,31],
                    'Others':[18,21,22,26,27,28,29,32]
                    },
    'MODIFIED':     {'Rainfed crops': [34,35,36,37,38,39,40,41,42,43,44],
                    'Forest plantations':[33],
                    'Settlements':[47,48,49,50,51],
                    'Others':[45,46]
                    },
    'MANAGED CONVENTIONAL': {'Irrigated crops':[52,53,54,55,56,57,58,59,60,61,62],
                            'Managed water bodies':[63,65,74],
                            'Residential':[68,69,71,72],
                            'Industry':[67,70,76],
                            'Others':[75,78]
                            },
    'MANAGED NON_CONVENTIONAL':     {'Indoor domestic':[66],
                                    'Indoor industry':[0],
                                    'Greenhouses':[64],
                                    'Livestock and husbandry':[73],
                                    'Power and energy':[79,80],
                                    'Others':[77]
                                    }

    }
    
    sheet2_classes =dict()
    sheet2_classes['1.0'] = sheet2_classes_v10
    
    return sheet2_classes[version]
 
def consumed_fractions(version = '1.0'):
    
    fractions = {
         'Forests':              1.00,
         'Shrubland':            1.00,
         'Rainfed Crops':        1.00,
         'Forest Plantations':   1.00,
         'Natural Water Bodies': 0.15,
         'Wetlands':             0.15,
         'Natural Grasslands':   0.70,
         'Other (Non-Manmade)':  0.40,
         'Irrigated crops':      0.80,
         'Managed water bodies': 0.40,
         'Other':                0.40,
         'Residential':          0.05,
         'Greenhouses':          0.95,
         'Aquaculture':          0.20}

    consumed_fractions =dict()
    consumed_fractions['1.0'] = fractions

    return consumed_fractions[version]
 
def sw_return_fractions(version = '1.0'):
    
    fractions = {
         'Forests':              -9999,
         'Shrubland':            -9999,
         'Rainfed Crops':        -9999,
         'Forest Plantations':   -9999,
         'Natural Water Bodies': 0.95,
         'Wetlands':             0.95,
         'Natural Grasslands':   0.10,
         'Other (Non-Manmade)':  0.50,
         'Irrigated crops':      0.90,
         'Managed water bodies': 0.95,
         'Other':                0.50,
         'Residential':          0.60,
         'Greenhouses':          0.50,
         'Aquaculture':          0.95}

    sw_return_fractions =dict()
    sw_return_fractions['1.0'] = fractions

    return sw_return_fractions[version]
	
	
def sw_supply_fractions(version = '1.0'):
    
    fractions = {
         'Forests':              0.05,
         'Shrubland':            0.10,
         'Rainfed Crops':        0.05,
         'Forest Plantations':   0.05,
         'Natural Water Bodies': 0.95,
         'Wetlands':             0.95,
         'Natural Grasslands':   0.30,
         'Other (Non-Manmade)':  0.50,
         'Irrigated crops':      0.90,
         'Managed water bodies': 0.95,
         'Other':                0.50,
         'Residential':          0.90,
         'Greenhouses':          0.50,
         'Aquaculture':          0.95}

    sw_supply_fractions =dict()
    sw_supply_fractions['1.0'] = fractions

    return sw_supply_fractions[version]

def get_sheet5_classes(version = '1.0'):
    lucs2lucstype = {
        'Forests':              [1, 8, 9, 10, 11, 17],
        'Shrubland':            [2, 12, 14, 15],
        'Rainfed Crops':        [34, 35, 36, 37, 38, 39, 40, 41, 42, 43],
        'Forest Plantations':   [33, 44],
        'Natural Water Bodies': [4, 19, 23, 24],
        'Wetlands':             [5, 25, 30, 31],
        'Natural Grasslands':   [3, 13, 16, 20],
        'Other (Non-Manmade)':  [6, 7, 18, 21, 22, 26, 27, 28, 29, 32, 45, 46, 47, 48, 49, 50, 51],
        'Irrigated crops':      [52,53,54,55,56,57,58,59,60,61,62],
        'Managed water bodies': [63,74,75,77],
        'Aquaculture':          [65],
        'Residential':          [66],
        'Greenhouses':          [64],
        'Other':                [68,69,70,71,72,76,78]}
    
    get_sheet5_classes =dict()
    get_sheet5_classes['1.0'] = lucs2lucstype    

    return get_sheet5_classes[version]
 
def get_sheet3_classes(version = '1.0'):
    
    sheet3_classes_v10 =  { 'CROP':         {'Cereals':              {'-':                     {'RAIN': [35], 'IRRI': [54]}},
                     
                                             'Non-cereals':          {'Root/tuber crops':          {'RAIN': [36],'IRRI': [55]},
                                                                      'Leguminous crops':            {'RAIN': [37],'IRRI': [56]},
                                                                      'Sugar crops':                 {'RAIN': [38],'IRRI': [57]},
                                                                      'Merged':                      {'RAIN': [36, 37, 38],'IRRI': [55, 56, 57]}},
                                             'Fruit & vegetables':   {'Vegetables & melons':         {'RAIN': [40],'IRRI': [59]},
                                                                      'Fruits & nuts':               {'RAIN': [39],'IRRI': [58]},
                                                                      'Merged':                      {'RAIN': [39, 40],'IRRI': [58, 59]}},
                                             'Oilseeds':            {'-':                   {'RAIN': [41],'IRRI': [60]}},
                                             'Feed crops':           {'-':                  {'RAIN': [34],'IRRI': [53]}},
                                             'Beverage crops':       {'-':              {'RAIN':[42] ,'IRRI': [61]}},
                                             'Other crops':          {'-':                 {'RAIN': [43],'IRRI': [62]}},
                                             #'Timber':               {'-':                      {'RAIN': [33],'IRRI': [52]}}
                                             },
                            'NON-CROP':     {'Fish (Aquaculture)':                 {'-':                        {'RAIN': [-1234], 'IRRI':[-1234]}},
                                             'Timber':               {'-':                      {'RAIN': [-1234], 'IRRI':[-1234]}},
                                             'Livestock':            {'Meat':                        {'RAIN': [-1234], 'IRRI':[-1234]},
                                                                      'Milk':                        {'RAIN': [-1234], 'IRRI':[-1234]}}
                                            }
                            }
    
    sheet3_classes =dict()
    sheet3_classes['1.0'] = sheet3_classes_v10
    
    return sheet3_classes[version]
    
def get_hi_and_ec():
    HIWC = {
    'Alfalfa': [None, None],
    'Banana': [0.6, 0.76],
    'Barley': [None, None],
    'Beans': [0.16, 0.33],
    'Cassava': [0.6, 0.65],
    'Cashew': [0.03, 0.3],
    'Coconut': [0.244, 0.0],
    'Coffee': [0.012, 0.88],
    'Cotton': [0.13, 0.2],
    'Eucalypt':[0.5, 0.50],
    'Grapes':[0.22, 0.75],
    'Grass':[0.45, 0.60],
    'Lucerne':[0.6, None],
    'Maize - Rainfed': [0.32, 0.26],
    'Maize - Irrigated': [0.39, 0.26],
    'Mango': [0.14, 0.84],
    'Olives': [0.012, 0.20],
    'Onions': [0.55, 0.85],
    'Oranges': [0.22, 0.85],
    'Palm Oil': [0.185, 0.1],
    'Pineapple': [None, None],
    'Potato': [0.8, 0.80],
    'Rice - Rainfed': [0.33, 0.16],
    'Rice - Irrigated': [0.42, 0.16],
    'Rubber': [0.013, 0.63],
    'Sorghum': [0.25, None],
    'Soybean': [None, None],
    'Sugarbeet': [0.6, 0.80],
    'Sugar cane': [0.69, 0.65],
    'Tapioca': [None, None],
    'Tea': [0.12, 0.50],
    'Wheat': [0.37, 0.15],
    'Fodder': [0.45,0.6],
    'Peanut':[0.03, 0.3],
    'Almond':[0.03, 0.3],
    'Pepper':[0.1, 0.5],
    'Mellon':[0.8, 0.6]
        }
    
    return HIWC

def get_sheet1_classes(lulc_version = '4.0'):
    lulc_dict = get_lulcs(lulc_version = lulc_version)
    categories = ['Protected', 'Utilized', 'Modified', 'Managed']
    sheet1_classes = dict()
    for cat in categories:
        sheet1_classes[cat] = [key for key, value in zip(lulc_dict.keys(), lulc_dict.values()) if value[1] == cat]

    return sheet1_classes

def get_sheet3_empties(): 
    wp_y_irrigated_dictionary = {
    'Cereals': {'-': None},
    'Non-cereals': {'Root/tuber crops':None, 'Leguminous crops':None, 'Sugar crops':None, 'Merged':None},
    'Fruit & vegetables': {'Vegetables & melons':None, 'Fruits & nuts':None, 'Merged':None},
    'Oilseeds': {'-': None},
    'Feed crops': {'-': None},
    'Beverage crops': {'-': None},
    'Other crops': {'-': None}}
    
    wp_y_rainfed_dictionary = {
    'Cereals': {'-':None},
    'Non-cereals': {'Root/tuber crops':None, 'Leguminous crops':None, 'Sugar crops':None, 'Merged':None},
    'Fruit & vegetables': {'Vegetables & melons':None, 'Fruits & nuts':None, 'Merged':None},
    'Oilseeds': {'-': None},
    'Feed crops': {'-': None},
    'Beverage crops': {'-': None},
    'Other crops': {'-': None}}
    
    wp_y_non_crop_dictionary = {
    'Livestock': {'Meat':None, 'Milk':None},
    'Fish (Aquaculture)': {'-':None},
    'Timber': {'-':None}}
    
    return wp_y_irrigated_dictionary, wp_y_rainfed_dictionary, wp_y_non_crop_dictionary

def get_bluegreen_classes(version = '1.0'):
    
    gb_cats = dict()
    mvg_avg_len = dict()
    
    gb_cats['1.0'] = {
    'crops':                [53,54,55,56,57,58,59,60,61,62, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 33, 44],
    'perennial crops':      [52],
    'savanna':              [12,13],
    'water':                [63,74,75,77,4, 19, 23, 24],
    'forests':              [1, 8, 9, 10, 11, 17],
    'grass':                [3, 16, 20, 2, 14, 15],
    'other':                [68,69,70,71,72,76,78,73,67,65,66,64,79,80,6, 7, 18, 21, 22, 26, 27, 28, 29, 32, 45, 46, 47, 48, 49, 50, 51, 5, 25, 30, 31],
    }

    mvg_avg_len['1.0'] = {
    'crops':                2,
    'perennial crops':      3,
    'savanna':              4,
    'water':                1,
    'forests':              5,
    'grass':                1,
    'other':                1,
    }
    
    return gb_cats[version], mvg_avg_len[version] 
    
#import csv
#lulc = dict()
#f = open(r"C:\Users\bec\Desktop\dict.csv", 'rt')
#try:
#    reader = csv.reader(f, delimiter=';')
#    for row in reader:
#        lulc[int(row[0])] = [row[1], row[2], row[3], float(row[4]), float(row[5]), float(row[6]), float(row[7]), float(row[8]), float(row[9]), float(row[10]), float(row[11])]
#finally:
#    f.close()
