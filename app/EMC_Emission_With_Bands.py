import dash
from dash import dcc, ctx, html, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import dash_daq as daq
import plotly.graph_objects as go
import pandas as pd
import os
import time
import base64
import io
import zipfile
import tempfile
import math
import numpy as np

def add_rowSpan(data, group):
    for i ,row in enumerate(data):
        if i == 0 or row[group] != data[i-1][group]:
            span = 1
            while i + span < len(data) and data[i + span][group] == row[group]:
                span += 1
            row["rowSpan"] = span
        else:
            row["rowSpan"] = 0
    return data

def find_min_max(figure):
    x_max = 0.00000000001
    y_max = float('-inf')
    x_min = float('inf')
    y_min = float('inf')
    for fig in figure['data']:
        if fig['visible'] == True and fig['meta']['Type'] == 'Line' or  fig['meta']['Type'] == 'Limit':
            if max(fig['x'])>x_max:
                x_max = float(max(fig['x']))
            if float(max(fig['y']))>y_max:
                y_max = float(max(fig['y']))
            if min(fig['x'])<x_min:
                x_min = float(min(fig['x']))
            if float(min(fig['y']))<y_min:
                y_min = float(min(fig['y']))
    return x_max, y_max, x_min, y_min


CISPR_25_5_RE_class_5 = {
  "GroupName": ["Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Analogue broadcast services", "Digital broadcast services", "Digital broadcast services", "Digital broadcast services", "Digital broadcast services", "Digital broadcast services", "Digital broadcast services", "Digital broadcast services", "Digital broadcast services", "Digital broadcast services", "Digital broadcast services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Digital mobile phone services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services", "Mobile services"],
  "BandName": ["LW", "LW", "LW", "MW", "MW", "MW", "SW", "SW", "SW", "TV Band I", "TV Band I", "FM", "FM", "FM", "TV Band III (analogue)", "TV Band III (analogue)", "TV Band IV", "TV Band IV", "DAB III", "DAB III", "TV Band III (digital)", "TV Band III (digital)", "DTTV", "DTTV", "DAB L Band", "DAB L Band", "SDARS", "SDARS", "4G I", "4G I", "5G n71, 4G", "5G n71, 4G", "5G n12/n14/n28/n29, 4G", "3G I", "5G n12/n14/n28/n29, 4G", "3G I", "5G n20", "3G II", "3G II", "5G n20", "2G I", "3G III", "5G n5/n18/n26, 4G", "2G I", "3G III", "5G n5/n18/n26, 4G", "2G II", "2G II", "3G IV", "5G n8, 4G", "5G n8, 4G", "3G IV", "5G n50/n51/n74/n75/n76/n91/n92/n93, 4G", "3G V", "3G V", "5G n50/n51/n74/n75/n76/n91/n92/n93, 4G", "4G II", "4G II", "2G III", "3G VI", "5G n3, 4G", "5G n3, 4G", "3G VI", "2G III", "2G IV", "3G VII", "5G n39/n2/n25/n70/n34, 4G", "3G VII", "2G IV", "5G n39/n2/n25/n70/n34, 4G", "5G n1/n65/n66, 4G", "5G n1/n65/n66, 4G", "3G VIII", "3G VIII", "3G IX", "5G n30/n40, 4G", "5G n30/n40, 4G", "3G IX", "5G n53", "5G n53", "3G X", "5G n7/n38/n41/n90, 4G", "5G n7/n38/n41/n90, 4G", "3G X", "3G XI", "5G n48/n77/n78, 4G", "5G n48/n77/n78, 4G", "3G XI", "5G n79", "5G n79", "4G III", "4G III", "5G n47, V2X", "5G n47, V2X", "CB", "CB", "CB", "VHF I", "VHF I", "VHF I", "VHF II", "VHF II", "VHF II", "VHF III", "VHF III", "VHF III", "RKE & TPMS 1", "RKE & TPMS 1", "Analogue UHF I", "Analogue UHF I", "Analogue UHF I", "RKE & TPMS 2", "RKE & TPMS 2", "Analogue UHF II", "Analogue UHF II", "Analogue UHF II", "GPS L5", "BDS, B1I", "GPS L1", "GLONASS L1", "WiFi / Bluetooth", "WiFi / Bluetooth", "WiFi I", "WiFi I", "WiFi II", "WiFi II", "B2X (WiFi)", "B2X (WiFi)"],
  "F Start(MHz)": ["0.15", "0.15", "0.15", "0.53", "0.53", "0.53", "5.9", "5.9", "5.9", "41", "41", "76", "76", "76", "174", "174", "470", "470", "171", "171", "174", "174", "470", "470", "1447", "1447", "2320", "2320", "460", "460", "617", "617", "703", "703", "703", "703", "791", "791", "791", "791", "852", "852", "852", "852", "852", "852", "925", "925", "925", "925", "925", "925", "1427", "1427", "1427", "1427", "1525", "1525", "1805", "1805", "1805", "1805", "1805", "1805", "1850", "1850", "1850", "1850", "1850", "1850", "2110", "2110", "2110", "2110", "2300", "2300", "2300", "2300", "2483.5", "2483.5", "2496", "2496", "2496", "2496", "3300", "3300", "3300", "3300", "4400", "4400", "5150", "5150", "5855", "5855", "26", "26", "26", "30", "30", "30", "68", "68", "68", "142", "142", "142", "300", "300", "380", "380", "380", "420", "420", "820", "820", "820", "1156.45", "1553.098", "1567.42", "1590.781", "2402", "2402", "5150", "5150", "5470", "5470", "5850", "5850"],
  "F Stop(MHz)": ["0.3", "0.3", "0.3", "1.8", "1.8", "1.8", "6.2", "6.2", "6.2", "88", "88", "108", "108", "108", "230", "230", "944", "944", "245", "245", "230", "230", "770", "770", "1494", "1494", "2345", "2345", "467.5", "467.5", "652", "652", "803", "803", "803", "803", "821", "821", "821", "821", "894", "894", "894", "894", "894", "894", "960", "960", "960", "960", "960", "960", "1518", "1518", "1518", "1518", "1559", "1559", "1880", "1880", "1880", "1880", "1880", "1880", "2025", "2025", "2025", "2025", "2025", "2025", "2200", "2200", "2200", "2200", "2400", "2400", "2400", "2400", "2495", "2495", "2690", "2690", "2690", "2690", "4200", "4200", "4200", "4200", "5000", "5000", "5925", "5925", "5925", "5925", "28", "28", "28", "54", "54", "54", "87", "87", "87", "175", "175", "175", "330", "330", "512", "512", "512", "450", "450", "960", "960", "960", "1196.45", "1569.098", "1583.42", "1616.594", "2494", "2494", "5350", "5350", "5725", "5725", "5925", "5925"],
  "Level Start(dBµV/m)": ["33", "46", "26", "20", "27", "40", "20", "27", "40", "28", "18", "38", "18", "25", "10", "20", "31", "41", "20", "30", "20", "30", "36", "46", "54", "44", "48", "58", "44", "24", "26", "46", "47", "21", "27", "41", "48", "42", "22", "28", "23", "23", "29", "43", "43", "49", "24", "44", "44", "50", "30", "24", "53", "27", "47", "33", "34", "54", "49", "49", "35", "55", "29", "29", "30", "30", "56", "50", "50", "36", "57", "37", "51", "31", "52", "38", "58", "32", "38", "58", "52", "58", "38", "32", "35", "41", "61", "55", "43", "63", "45", "65", "66", "46", "27", "20", "40", "27", "20", "40", "35", "15", "22", "22", "35", "15", "18", "32", "18", "25", "38", "18", "32", "31", "44", "24", "20", "5.5", "10", "10", "32", "52", "59", "39", "39", "59", "64", "84"],
  "Level Stop(dBµV/m)": ["33", "46", "26", "20", "27", "40", "20", "27", "40", "28", "18", "38", "18", "25", "10", "20", "31", "41", "20", "30", "20", "30", "36", "46", "54", "44", "48", "58", "44", "24", "26", "46", "47", "21", "27", "41", "48", "42", "22", "28", "23", "23", "29", "43", "43", "49", "24", "44", "44", "50", "30", "24", "53", "27", "47", "33", "34", "54", "49", "49", "35", "55", "29", "29", "30", "30", "56", "50", "50", "36", "57", "37", "51", "31", "52", "38", "58", "32", "38", "58", "52", "58", "38", "32", "35", "41", "61", "55", "43", "63", "45", "65", "66", "46", "27", "20", "40", "27", "20", "40", "35", "15", "22", "22", "35", "15", "18", "32", "18", "25", "38", "18", "32", "31", "44", "24", "20", "5.5", "10", "10", "32", "52", "59", "39", "39", "59", "64", "84"],
  "Detector": ["QPeak", "Peak", "CISPR_Avg", "CISPR_Avg", "QPeak", "Peak", "CISPR_Avg", "QPeak", "Peak", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "QPeak", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak", "Peak", "CISPR_Avg", "CISPR_Avg", "Peak", "Peak", "CISPR_Avg", "CISPR_Avg", "Peak", "Peak", "CISPR_Avg", "CISPR_Avg", "Peak", "Peak", "Peak", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "Peak", "Peak", "Peak", "CISPR_Avg", "Peak", "Peak", "Peak", "CISPR_Avg", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "CISPR_Avg", "Peak", "Peak", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "Peak", "Peak", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "CISPR_Avg", "Peak", "Peak", "Peak", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "Peak", "Peak", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak", "Peak", "CISPR_Avg", "QPeak", "CISPR_Avg", "Peak", "QPeak", "CISPR_Avg", "Peak", "Peak", "CISPR_Avg", "QPeak", "QPeak", "Peak", "CISPR_Avg", "CISPR_Avg", "Peak", "CISPR_Avg", "QPeak", "Peak", "CISPR_Avg", "Peak", "QPeak", "Peak", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "CISPR_Avg", "Peak", "Peak", "CISPR_Avg", "CISPR_Avg", "Peak", "CISPR_Avg", "Peak"],
  "RBW(kHz)": ["9", "9", "9", "9", "9", "9", "9", "9", "9", "120", "120", "120", "120", "120", "120", "120", "120", "120", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "120", "1000", "1000", "120", "1000", "1000", "120", "120", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "120", "1000", "1000", "1000", "1000", "120", "120", "1000", "1000", "1000", "120", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "9", "9", "9", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "120", "9", "9", "9", "9", "1000", "1000", "1000", "1000", "1000", "1000", "1000", "1000"],
  "Interpolation": ["LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN", "LOGLIN"],
  "MeasurementTime(ms)": ["1000", "50", "50", "50", "1000", "50", "50", "1000", "50", "5", "5", "5", "5", "1000", "5", "5", "5", "5", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "5", "50", "50", "5", "50", "50", "5", "5", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "5", "50", "50", "50", "50", "5", "5", "50", "50", "50", "5", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "1000", "50", "50", "1000", "5", "5", "5", "5", "1000", "1000", "5", "5", "5", "5", "5", "1000", "5", "5", "5", "1000", "5", "5", "5", "5", "5", "5", "50", "50", "50", "50", "50", "50", "50", "50"],
  "FrequencyStep(kHz)": ["5", "5", "5", "5", "5", "5", "5", "5", "5", "50", "50", "50", "50", "50", "50", "50", "50", "50", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "50", "500", "500", "50", "500", "500", "50", "50", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "50", "500", "500", "500", "500", "50", "50", "500", "500", "500", "50", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "500", "5", "5", "5", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "50", "5", "5", "5", "5", "500", "500", "500", "500", "500", "500", "500", "500"]
}

CISPR_25_5_AN_class_5 = {
    'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
    'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
    'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
    'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
    'Level Start(dBµV)': [57, 70, 50, 34, 41, 54, 33, 40, 53, 34, 24, 25, 18, 38, 44, 24, 31, 31, 44, 24, 18, 25, 38],
    'Level Stop(dBµV)': [57, 70, 50, 34, 41, 54, 33, 40, 53, 34, 24, 25, 18, 38, 44, 24, 31, 31, 44, 24, 18, 25, 38],
    'Detector': ['QPeak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'QPeak', 'Peak', 'CISPR_Avg', 'QPeak', 'Peak', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'QPeak', 'QPeak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'QPeak', 'Peak'],
    'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
    'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
    'MeasurementTime(ms)': [1000, 50, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 1000, 5, 5, 50, 50, 1000, 1000, 5, 5, 5, 1000, 5], 'FrequencyStep(kHz)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 5, 5, 5, 50, 50, 50, 50, 50, 50]}

TL_81000_RE_class_5 = {
    'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
    'BandName': ['B4', 'B5', 'B6', 'B7', 'B8', 'B8', 'B8', 'B9', 'B9', 'B9', 'B10', 'B10', 'B10', 'B11', 'B11', 'B12', 'B12', '8 - 125kHz', '9 - CB radio', '9 - CB radio', '10 - 4m/BOS', '10 - 4m/BOS', '11 - 2m/Taxi', '11 - 2m/Taxi', '12 - 2m/BOS', '12 - 2m/BOS', '13 - 2m/BOS', '13 - 2m/BOS', '14 - SRD', '14 - SRD', '15 - Trunked Radio', '15 - Trunked Radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - SRD', '19 - SRD', '20 - Trunked Radio', '20 - Trunked Radio', '21 - 2G, 3G, 4G, 5G', '21 - 2G, 3G, 4G, 5G', '22 - SRD', '22 - SRD', '23 - GPS, Galileo I', '23 - GPS, Galileo I', '23 - GPS, Galileo I', '23 - Glonass I', '23 - GPS, Galileo II', '23 - Glonass I', '23 - Beidou I', '23 - Glonass I', '23 - Beidou I', '23 - GPS, Galileo II', '23 - GPS, Galileo II', '23 - Beidou I', '23 - GPS I', '23 - GPS I', '23 - GPS I', '24 - 3G, 4G, 5G', '24 - 3G, 4G, 5G', '25 - Beidou II', '25 - Galileo', '25 - Beidou II', '25 - GPS II', '25 - Beidou II', '25 - GPS II', '25 - Galileo', '25 - Galileo', '25 - GPS II', '25 - Beidou III', '25 - Beidou III', '25 - Beidou III', '25 - Glonass II', '25 - Glonass II', '25 - Glonass II', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 5G', '27 - 5G', '28 - WLAN, DSRC', '28 - WLAN, DSRC', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '5 - TV II', '5 - TV II', '6 - TV III', '6 - TV III', '3 - DAB', '3 - DAB', '7 - TV IV/V', '7 - TV IV/V', '4 - SDARS', '4 - SDARS'],
    'F Start(MHz)': [0.009, 0.15, 5.35, 20.0, 30.0, 30.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 1164.0, 1175.45, 1177.45, 1188.0, 1195.0, 1197.0, 1198.14, 1205.0, 1205.14, 1206.14, 1208.14, 1209.14, 1217.0, 1226.6, 1228.6, 1350.0, 1350.0, 1552.098, 1559.0, 1559.098, 1563.0, 1563.098, 1574.42, 1574.42, 1576.42, 1576.42, 1580.742, 1587.742, 1591.742, 1593.0, 1597.625, 1606.375, 1695.0, 1695.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0, 2320.0, 2320.0],
    'F Stop(MHz)': [0.15, 5.35, 20.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 1000.0, 3000.0, 3000.0, 6000.0, 6000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1175.45, 1177.45, 1188.0, 1197.0, 1206.14, 1205.0, 1205.14, 1214.0, 1209.14, 1208.14, 1219.0, 1216.14, 1226.6, 1228.6, 1237.0, 1518.0, 1518.0, 1559.098, 1574.42, 1563.098, 1574.42, 1570.098, 1576.42, 1576.42, 1591.0, 1587.0, 1587.742, 1591.742, 1598.742, 1597.625, 1606.375, 1610.0, 2900.0, 2900.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0, 2345.0, 2345.0],
    'Level Start(dBµV/m)': [86, 62, 62, 39, 62, 49, 42, 32, 39, 52, 50, 43, 63, 60, 80, 84, 104, 41, 27, 7, 2, 25, 2, 25, 25, 2, 2, 25, 34, 14, 39, 19, 39, 19, 19, 39, 19, 39, 34, 14, 19, 39, 35, 55, 20, 40, 60, 20, 20, 60, 60, 20, 60, 20, 20, 20, 20, 20, 60, 20, 20, 34, 54, 60, 60, 20, 60, 20, 20, 20, 20, 20, 60, 20, 20, 60, 20, 20, 57, 37, 65, 45, 48, 68, 25, 18, 12, 19, 22, 37, 22, 37, 22, 32, 40, 20, 46, 56],
    'Level Stop(dBµV/m)': [62, 62, 39, 39, 52, 39, 32, 43, 50, 63, 50, 43, 63, 60, 80, 84, 104, 41, 27, 7, 2, 25, 2, 25, 25, 2, 2, 25, 34, 14, 39, 19, 39, 19, 19, 39, 19, 39, 34, 14, 19, 39, 35, 55, 20, 40, 20, 20, 60, 20, 20, 20, 20, 60, 20, 20, 60, 60, 20, 20, 60, 34, 54, 20, 20, 20, 20, 60, 20, 20, 60, 60, 20, 20, 60, 20, 20, 60, 62, 42, 65, 45, 48, 68, 25, 18, 12, 19, 22, 37, 22, 37, 22, 32, 45, 25, 46, 56],
    'Detector': ['Peak', 'Peak', 'Peak', 'Peak', 'Peak', 'QPeak', 'Average', 'Average', 'QPeak', 'Peak', 'QPeak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'QPeak', 'Average', 'Average', 'QPeak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak'],
    'RBW(kHz)': [0.2, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0],
    'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN'],
    'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 10000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
    'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_AN_class_5 = {
    'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio broadcasting - digital', 'Radio broadcasting - digital'],
    'BandName': ['B1', 'B1', 'B2', 'B2', 'B3', 'B3', '4 - 125kHz', '5 - CB radio', '5 - CB radio', '6 - 4m/BOS', '6 - 4m/BOS', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '3 - TV II', '3 - TV II'],
    'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0],
    'F Stop(MHz)': [0.52, 0.52, 30.0, 30.0, 108.0, 108.0, 0.15, 29.7, 29.7, 87.255, 87.255, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0],
    'Level Start(dBµV)': [97, 107, 65, 75, 55, 65, 73, 63, 43, 8, 31, 41, 34, 12, 19, 43, 28],
    'Level Stop(dBµV)': [65, 75, 65, 75, 55, 65, 73, 63, 43, 8, 31, 41, 34, 12, 19, 43, 28],
    'Detector': ['Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'QPeak', 'Average', 'Average', 'QPeak', 'Peak', 'Average'],
    'RBW(kHz)': [9, 9, 9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000],
    'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
    'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 3000, 10000, 3000, 3000],
    'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_RE_class_3 = {
    'GroupName': ['Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
    'BandName': ['RE_B1', 'RE_B1', 'RE_B2', 'RE_B2', 'RE_B3', 'RE_B3', 'RE_B4', 'RE_B4', 'RE_B5', 'RE_B5', 'RE_B6', 'RE_B6', '1 - MW', '1 - MW', '2 - FM', '2 - FM', '4 - TV III', '3 - DAB', '5 - TV IV/V', '6 - SDARS', '6 - SDARS', '20 - SRD', '20 - SRD', '7 - NFC', '7 - NFC', '8 - 4m/BOS', '8 - 4m/BOS', '9 - 2m/Taxi', '9 - 2m/Taxi', '10 - 2m/BOS', '10 - 2m/BOS', '11 - 2m/BOS', '11 - 2m/BOS', '12 - SRD', '12 - SRD', '13 - Trunked Radio', '13 - Trunked Radio', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - SRD', '16 - SRD', '17 - Trunked Radio', '17 - Trunked Radio', '18 - 2G, 3G, 4G', '18 - 2G, 3G, 4G', '19 - PDC, D-AMPS', '19 - PDC, D-AMPS', '21 - 4G', '21 - 4G', '22 - GNSS', '23 - 2G, 3G, 4G', '23 - 2G, 3G, 4G', '24 - 4G', '24 - 4G', '25 - Bluetooth, WLAN', '25 - Bluetooth, WLAN', '26 - 4G', '26 - 4G', '27 - 5G', '27 - 5G', '28 - WLAN, C2X', '28 - WLAN, C2X'],
    'F Start(MHz)': [0.15, 0.15, 5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 0.52, 0.52, 70.0, 70.0, 170.0, 174.0, 470.0, 2320.0, 2320.0, 0.000868, 0.000868, 13.5, 13.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 717.0, 717.0, 851.0, 851.0, 1427.0, 1427.0, 1553.0, 1805.0, 1805.0, 2300.0, 2300.0, 2402.0, 2402.0, 2496.0, 2496.0, 3400.0, 3400.0, 5150.0, 5150.0],
    'F Stop(MHz)': [5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 1.73, 1.73, 120.0, 120.0, 230.0, 241.0, 806.0, 2345.0, 2345.0, 0.000876, 0.000876, 13.9, 13.9, 87.255, 87.255, 164.0, 164.0, 169.83, 169.83, 173.98, 173.98, 317.0, 317.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 894.0, 894.0, 1518.0, 1518.0, 1610.0, 2200.0, 2200.0, 2400.0, 2400.0, 2497.0, 2497.0, 2690.0, 2690.0, 3800.0, 3800.0, 5925.0, 5925.0],
    'Level Start(dBµV/m)': [52, 62, 62, 52, 29, 39, 42, 52, 52, 42, 63, 53, 41, 34, 31, 24, 34, 34, 41, 58, 68, 52, 32, 50, 30, 47, 14, 47, 14, 47, 14, 14, 47, 46, 26, 51, 31, 31, 51, 51, 31, 26, 46, 51, 31, 63, 43, 63, 43, 47, 67, 32, 43, 63, 70, 50, 78, 58, 70, 50, 78, 58, 78, 58], 'Level Stop(dBµV/m)': [52, 62, 39, 29, 29, 39, 42, 52, 63, 53, 63, 53, 41, 34, 31, 24, 34, 34, 41, 58, 68, 52, 32, 50, 30, 47, 14, 47, 14, 47, 14, 14, 47, 46, 26, 51, 31, 31, 51, 51, 31, 26, 46, 51, 31, 63, 43, 63, 43, 47, 67, 32, 43, 63, 70, 50, 78, 58, 70, 50, 78, 58, 78, 58],
    'Detector': ['Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average'],
    'RBW(kHz)': [9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 9, 9, 9, 9, 120, 9, 120, 9, 120, 9, 9, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 120, 120, 1000, 1000, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
    'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
    'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
    'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

CE_AN_Non_Spark_Requirements_reduced = {'GroupName': ['AN', 'AN'],
                                        'BandName': ['G1', 'G1'],
                                        'F Start(MHz)': [0.53, 0.53],
                                        'F Stop(MHz)': [1.71, 1.71],
                                        'Level Start(dBµV)': [26, 32],
                                        'Level Stop(dBµV)': [26, 32],
                                        'Detector': ['Average', 'Peak'],
                                        'RBW(kHz)': [9, 9],
                                        'Interpolation': ['LOGLIN', 'LOGLIN'],
                                        'MeasurementTime(ms)': [1000, 1000],
                                        'FrequencyStep(kHz)': [' ', ' ']}

CE_AN_Non_Spark_Requirements = {'GroupName': ['AN', 'AN'],
                                'BandName': ['G1', 'G1'],
                                'F Start(MHz)': [0.53, 0.53],
                                'F Stop(MHz)': [1.71, 1.71],
                                'Level Start(dBµV)': [36, 42],
                                'Level Stop(dBµV)': [36, 42],
                                'Detector': ['Average', 'Peak'],
                                'RBW(kHz)': [9, 9],
                                'Interpolation': ['LOGLIN', 'LOGLIN'],
                                'MeasurementTime(ms)': [1000, 1000],
                                'FrequencyStep(kHz)': [' ', ' ']}

CE_AN_Spark_Requirements = {'GroupName': ['AN'],
                            'BandName': ['G1'],
                            'F Start(MHz)': [0.53],
                            'F Stop(MHz)': [1.71],
                            'Level Start(dBµV)': [82],
                            'Level Stop(dBµV)': [82],
                            'Detector': ['QPeak'],
                            'RBW(kHz)': [9],
                            'Interpolation': ['LOGLIN'],
                            'MeasurementTime(ms)': [5000],
                            'FrequencyStep(kHz)': [' ']}

CISPR_25_4_AN_class_1 = {'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
                         'Level Start(dBµV)': [97, 90, 110, 86, 73, 66, 77, 64, 57, 48, 58, 49, 42, 62, 68, 55, 48, 68, 55, 48, 42, 62, 49],
                         'Level Stop(dBµV)': [97, 90, 110, 86, 73, 66, 77, 64, 57, 48, 58, 49, 42, 62, 68, 55, 48, 68, 55, 48, 42, 62, 49],
                         'Detector': ['QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'QPeak'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [1000, 50, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 1000, 5, 5, 50, 1000, 50, 5, 1000, 5, 5, 5, 1000],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

CISPR_25_4_AN_class_2 = {'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
                        'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
                        'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
                        'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
                        'Level Start(dBµV)': [87, 80, 100, 78, 65, 58, 71, 58, 51, 42, 52, 43, 36, 56, 62, 49, 42, 62, 49, 42, 36, 56, 43],
                        'Level Stop(dBµV)': [87, 80, 100, 78, 65, 58, 71, 58, 51, 42, 52, 43, 36, 56, 62, 49, 42, 62, 49, 42, 36, 56, 43],
                        'Detector': ['QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'QPeak'],
                        'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                        'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                        'MeasurementTime(ms)': [1000, 50, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 1000, 5, 5, 50, 1000, 50, 5, 1000, 5, 5, 5, 1000],
                        'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

CISPR_25_4_AN_class_3 = {'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
                         'Level Start(dBµV)': [90, 77, 70, 70, 57, 50, 65, 52, 45, 46, 36, 50, 37, 30, 56, 43, 36, 56, 43, 36, 50, 37, 30],
                         'Level Stop(dBµV)': [90, 77, 70, 70, 57, 50, 65, 52, 45, 46, 36, 50, 37, 30, 56, 43, 36, 56, 43, 36, 50, 37, 30],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 5, 1000, 5, 50, 1000, 50, 5, 1000, 5, 5, 1000, 5],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

CISPR_25_4_AN_class_4 = {'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
                         'Level Start(dBµV)': [80, 67, 60, 62, 49, 42, 59, 46, 39, 40, 30, 44, 31, 24, 50, 37, 30, 50, 37, 30, 44, 31, 24],
                         'Level Stop(dBµV)': [80, 67, 60, 62, 49, 42, 59, 46, 39, 40, 30, 44, 31, 24, 50, 37, 30, 50, 37, 30, 44, 31, 24],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 5, 1000, 5, 50, 1000, 50, 5, 1000, 5, 5, 1000, 5],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

CISPR_25_4_AN_class_5 = {'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
                         'Level Start(dBµV)': [70, 57, 50, 54, 41, 34, 53, 40, 33, 34, 24, 38, 25, 18, 44, 31, 24, 44, 31, 24, 38, 25, 18],
                         'Level Stop(dBµV)': [70, 57, 50, 54, 41, 34, 53, 40, 33, 34, 24, 38, 25, 18, 44, 31, 24, 44, 31, 24, 38, 25, 18],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 5, 1000, 5, 50, 1000, 50, 5, 1000, 5, 5, 1000, 5],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

CISPR_25_4_RE_class_5 = {'GroupName': ['Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Broadcast', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'DAB L Band', 'DAB L Band', 'SW', 'SW', 'SW', 'TV Band I', 'TV Band I', 'FM', 'FM', 'FM', 'DAB III', 'DAB III', 'TV Band III', 'TV Band III', 'TV Band IV', 'TV Band IV', 'DTTV', 'DTTV', 'SDARS', 'SDARS', 'CB', 'CB', 'CB', 'VHF I', 'VHF I', 'VHF I', 'VHF II', 'VHF II', 'VHF II', 'VHF III', 'VHF III', 'VHF III', 'RKE I', 'RKE I', 'Analogue UHF I', 'Analogue UHF I', 'Analogue UHF I', 'RKE II', 'RKE II', 'Analogue UHF II', 'Analogue UHF II', 'Analogue UHF II', 'GSM 800', 'GSM 800', 'EGSM/GSM 900', 'EGSM/GSM 900', 'GPS L1 civil', 'Glonass L1', 'GSM 1800 (PCN)', 'GSM 1800 (PCN)', 'GSM 1900', 'GSM 1900', '3G / IMT 2000 I', '3G / IMT 2000 I', '3G / IMT 2000 II', '3G / IMT 2000 II', '3G / IMT 2000 III', '3G / IMT 2000 III', 'Bluetooth/802.11', 'Bluetooth/802.11'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 1.447, 1.447, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 171.0, 171.0, 174.0, 174.0, 468.0, 468.0, 470.0, 470.0, 2320.0, 2320.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0, 142.0, 142.0, 142.0, 300.0, 300.0, 380.0, 380.0, 380.0, 420.0, 420.0, 820.0, 820.0, 820.0, 860.0, 860.0, 925.0, 925.0, 1567.0, 1591.0, 1803.0, 1803.0, 1850.0, 1850.0, 1900.0, 1900.0, 2010.0, 2010.0, 2172.0, 2172.0, 2400.0, 2400.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 1.494, 1.494, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 245.0, 245.0, 230.0, 230.0, 944.0, 944.0, 770.0, 770.0, 2345.0, 2345.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0, 175.0, 175.0, 175.0, 330.0, 330.0, 512.0, 512.0, 512.0, 450.0, 450.0, 960.0, 960.0, 960.0, 895.0, 895.0, 960.0, 960.0, 1583.0, 1616.0, 1882.0, 1882.0, 1990.0, 1990.0, 1992.0, 1992.0, 2025.0, 2025.0, 2180.0, 2180.0, 2500.0, 2500.0],
                         'Level Start(dBµV/m)': [46, 33, 26, 40, 27, 20, 28, 18, 40, 27, 20, 28, 18, 38, 25, 18, 26, 16, 32, 22, 41, 31, 45, 35, 34, 24, 40, 27, 20, 40, 27, 20, 35, 22, 15, 35, 22, 15, 32, 18, 38, 25, 18, 32, 18, 44, 31, 24, 44, 24, 44, 24, 10, 10, 44, 24, 44, 24, 44, 24, 44, 24, 44, 24, 44, 24],
                         'Level Stop(dBµV/m)': [46, 33, 26, 40, 27, 20, 28, 18, 40, 27, 20, 28, 18, 38, 25, 18, 26, 16, 32, 22, 41, 31, 45, 35, 34, 24, 40, 27, 20, 40, 27, 20, 35, 22, 15, 35, 22, 15, 32, 18, 38, 25, 18, 32, 18, 44, 31, 24, 44, 24, 44, 24, 10, 10, 44, 24, 44, 24, 44, 24, 44, 24, 44, 24, 44, 24],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 50, 50, 1000, 50, 50, 50, 50, 1000, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 50, 50, 50, 1000, 50, 50, 50, 50, 1000, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

CISPR_25_5_AN_class_1 = {'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
                         'Level Start(dBµV)': [110, 97, 90, 86, 73, 66, 77, 64, 57, 58, 48, 62, 49, 42, 68, 55, 48, 68, 55, 48, 62, 49, 42],
                         'Level Stop(dBµV)': [110, 97, 90, 86, 73, 66, 77, 64, 57, 58, 48, 62, 49, 42, 68, 55, 48, 68, 55, 48, 62, 49, 42],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 5, 1000, 5, 50, 1000, 50, 5, 1000, 5, 5, 1000, 5],
                         'FrequencyStep(kHz)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 5, 5, 5, 50, 50, 50, 50, 50, 50]}

CISPR_25_5_AN_class_2 = {'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
                         'Level Start(dBµV)': [100, 87, 80, 78, 65, 58, 71, 58, 51, 52, 42, 56, 43, 36, 62, 49, 42, 62, 49, 42, 56, 43, 36],
                         'Level Stop(dBµV)': [100, 87, 80, 78, 65, 58, 71, 58, 51, 52, 42, 56, 43, 36, 62, 49, 42, 62, 49, 42, 56, 43, 36],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 5, 1000, 5, 50, 1000, 50, 5, 1000, 5, 5, 1000, 5],
                         'FrequencyStep(kHz)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 5, 5, 5, 50, 50, 50, 50, 50, 50]}

CISPR_25_5_AN_class_3 = {'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
                         'Level Start(dBµV)': [90, 77, 70, 50, 57, 70, 45, 52, 65, 46, 36, 37, 30, 50, 56, 43, 36, 36, 43, 56, 37, 30, 50],
                         'Level Stop(dBµV)': [90, 77, 70, 50, 57, 70, 45, 52, 65, 46, 36, 37, 30, 50, 56, 43, 36, 36, 43, 56, 37, 30, 50],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'QPeak', 'Peak', 'CISPR_Avg', 'QPeak', 'Peak', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'QPeak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 1000, 5, 5, 50, 1000, 50, 5, 1000, 5, 1000, 5, 5],
                         'FrequencyStep(kHz)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 5, 5, 5, 50, 50, 50, 50, 50, 50]}

CISPR_25_5_AN_class_4 = {'GroupName': ['BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'BROADCAST', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES', 'MOBILE SERVICES'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV I', 'TV I', 'FM', 'FM', 'FM', 'CB', 'CB', 'CB', 'VHF 1', 'VHF 1', 'VHF 1', 'VHF 2', 'VHF 2', 'VHF 2'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0],
                         'Level Start(dBµV)': [80, 67, 60, 62, 49, 42, 59, 46, 39, 40, 30, 44, 31, 24, 50, 37, 30, 50, 37, 30, 44, 31, 24],
                         'Level Stop(dBµV)': [80, 67, 60, 62, 49, 42, 59, 46, 39, 40, 30, 44, 31, 24, 50, 37, 30, 50, 37, 30, 44, 31, 24],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 5, 1000, 5, 50, 1000, 50, 5, 1000, 5, 5, 1000, 5],
                         'FrequencyStep(kHz)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 60, 50, 5, 5, 5, 50, 50, 50, 50, 50, 50]}

CISPR_25_5_RE_class_1 = {'GroupName': ['Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV Band I', 'TV Band I', 'FM', 'FM', 'FM', 'TV Band III (analogue)', 'TV Band III (analogue)', 'TV Band IV', 'TV Band IV', 'DAB III', 'DAB III', 'TV Band III (digital)', 'TV Band III (digital)', 'DTTV', 'DTTV', 'DAB L Band', 'DAB L Band', 'SDARS', 'SDARS', '4G I', '4G I', '5G n71, 4G', '5G n71, 4G', '3G I', '5G n12/n14/n28/n29, 4G', '5G n12/n14/n28/n29, 4G', '3G I', '3G II', '3G II', '5G n20', '5G n20', '5G n5/n18/n26, 4G', '3G III', '5G n5/n18/n26, 4G', '3G III', '2G I', '2G I', '5G n8, 4G', '5G n8, 4G', '3G IV', '2G II', '2G II', '3G IV', '3G V', '5G n50/n51/n74/n75/n76/n91/n92/n93, 4G', '5G n50/n51/n74/n75/n76/n91/n92/n93, 4G', '3G V', '4G II', '4G II', '3G VI', '2G III', '5G n3, 4G', '5G n3, 4G', '2G III', '3G VI', '5G n39/n2/n25/n70/n34, 4G', '5G n39/n2/n25/n70/n34, 4G', '2G IV', '2G IV', '3G VII', '3G VII', '3G VIII', '3G VIII', '5G n1/n65/n66, 4G', '5G n1/n65/n66, 4G', '3G IX', '5G n30/n40, 4G', '5G n30/n40, 4G', '3G IX', '5G n53', '5G n53', '5G n7/n38/n41/n90, 4G', '3G X', '3G X', '5G n7/n38/n41/n90, 4G', '3G XI', '3G XI', '5G n48/n77/n78, 4G', '5G n48/n77/n78, 4G', '5G n79', '5G n79', '4G III', '4G III', '5G n47, V2X', '5G n47, V2X', 'CB', 'CB', 'CB', 'VHF I', 'VHF I', 'VHF I', 'VHF II', 'VHF II', 'VHF II', 'VHF III', 'VHF III', 'VHF III', 'RKE & TPMS 1', 'RKE & TPMS 1', 'Analogue UHF I', 'Analogue UHF I', 'Analogue UHF I', 'RKE & TPMS 2', 'RKE & TPMS 2', 'Analogue UHF II', 'Analogue UHF II', 'Analogue UHF II', 'GPS L5', 'BDS, B1I', 'GPS L1', 'GLONASS L1', 'WiFi / Bluetooth', 'WiFi / Bluetooth', 'WiFi I', 'WiFi I', 'WiFi II', 'WiFi II', 'B2X (WiFi)', 'B2X (WiFi)'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 174.0, 174.0, 470.0, 470.0, 171.0, 171.0, 174.0, 174.0, 470.0, 470.0, 1447.0, 1447.0, 2320.0, 2320.0, 460.0, 460.0, 617.0, 617.0, 703.0, 703.0, 703.0, 703.0, 791.0, 791.0, 791.0, 791.0, 852.0, 852.0, 852.0, 852.0, 852.0, 852.0, 925.0, 925.0, 925.0, 925.0, 925.0, 925.0, 1427.0, 1427.0, 1427.0, 1427.0, 1525.0, 1525.0, 1805.0, 1805.0, 1805.0, 1805.0, 1805.0, 1805.0, 1850.0, 1850.0, 1850.0, 1850.0, 1850.0, 1850.0, 2110.0, 2110.0, 2110.0, 2110.0, 2300.0, 2300.0, 2300.0, 2300.0, 2483.5, 2483.5, 2496.0, 2496.0, 2496.0, 2496.0, 3300.0, 3300.0, 3300.0, 3300.0, 4400.0, 4400.0, 5150.0, 5150.0, 5855.0, 5855.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0, 142.0, 142.0, 142.0, 300.0, 300.0, 380.0, 380.0, 380.0, 420.0, 420.0, 820.0, 820.0, 820.0, 1156.45, 1553.098, 1567.42, 1590.781, 2402.0, 2402.0, 5150.0, 5150.0, 5470.0, 5470.0, 5850.0, 5850.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 230.0, 230.0, 944.0, 944.0, 245.0, 245.0, 230.0, 230.0, 770.0, 770.0, 1494.0, 1494.0, 2345.0, 2345.0, 467.5, 467.5, 652.0, 652.0, 803.0, 803.0, 803.0, 803.0, 821.0, 821.0, 821.0, 821.0, 894.0, 894.0, 894.0, 894.0, 894.0, 894.0, 960.0, 960.0, 960.0, 960.0, 960.0, 960.0, 1518.0, 1518.0, 1518.0, 1518.0, 1559.0, 1559.0, 1880.0, 1880.0, 1880.0, 1880.0, 1880.0, 1880.0, 2025.0, 2025.0, 2025.0, 2025.0, 2025.0, 2025.0, 2200.0, 2200.0, 2200.0, 2200.0, 2400.0, 2400.0, 2400.0, 2400.0, 2495.0, 2495.0, 2690.0, 2690.0, 2690.0, 2690.0, 4200.0, 4200.0, 4200.0, 4200.0, 5000.0, 5000.0, 5925.0, 5925.0, 5925.0, 5925.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0, 175.0, 175.0, 175.0, 330.0, 330.0, 512.0, 512.0, 512.0, 450.0, 450.0, 960.0, 960.0, 960.0, 1196.45, 1569.098, 1583.42, 1616.594, 2494.0, 2494.0, 5350.0, 5350.0, 5725.0, 5725.0, 5925.0, 5925.0],
                         'Level Start(dBµV/m)': [66.0, 86.0, 73.0, 52.0, 72.0, 59.0, 51.0, 64.0, 44.0, 42.0, 52.0, 49.0, 42.0, 62.0, 44.0, 34.0, 55.0, 65.0, 44.0, 54.0, 54.0, 44.0, 70.0, 60.0, 78.0, 68.0, 82.0, 72.0, 68.0, 48.0, 50.0, 70.0, 45.0, 51.0, 71.0, 65.0, 46.0, 66.0, 72.0, 52.0, 73.0, 67.0, 53.0, 47.0, 67.0, 47.0, 54.0, 74.0, 68.0, 68.0, 48.0, 48.0, 71.0, 57.0, 77.0, 51.0, 58.0, 78.0, 53.0, 53.0, 79.0, 59.0, 73.0, 73.0, 80.0, 60.0, 74.0, 54.0, 74.0, 54.0, 55.0, 75.0, 81.0, 61.0, 76.0, 82.0, 62.0, 56.0, 82.0, 62.0, 82.0, 76.0, 56.0, 62.0, 79.0, 59.0, 65.0, 85.0, 87.0, 67.0, 69.0, 89.0, 70.0, 90.0, 44.0, 51.0, 64.0, 51.0, 44.0, 64.0, 46.0, 39.0, 59.0, 39.0, 46.0, 59.0, 56.0, 42.0, 62.0, 42.0, 49.0, 42.0, 56.0, 68.0, 55.0, 48.0, 44.0, 29.5, 34.0, 34.0, 56.0, 76.0, 63.0, 83.0, 83.0, 63.0, 108.0, 88.0],
                         'Level Stop(dBµV/m)': [66.0, 86.0, 73.0, 52.0, 72.0, 59.0, 51.0, 64.0, 44.0, 42.0, 52.0, 49.0, 42.0, 62.0, 44.0, 34.0, 55.0, 65.0, 44.0, 54.0, 54.0, 44.0, 70.0, 60.0, 78.0, 68.0, 82.0, 72.0, 68.0, 48.0, 50.0, 70.0, 45.0, 51.0, 71.0, 65.0, 46.0, 66.0, 72.0, 52.0, 73.0, 67.0, 53.0, 47.0, 67.0, 47.0, 54.0, 74.0, 68.0, 68.0, 48.0, 48.0, 71.0, 57.0, 77.0, 51.0, 58.0, 78.0, 53.0, 53.0, 79.0, 59.0, 73.0, 73.0, 80.0, 60.0, 74.0, 54.0, 74.0, 54.0, 55.0, 75.0, 81.0, 61.0, 76.0, 82.0, 62.0, 56.0, 82.0, 62.0, 82.0, 76.0, 56.0, 62.0, 79.0, 59.0, 65.0, 85.0, 87.0, 67.0, 69.0, 89.0, 70.0, 90.0, 44.0, 51.0, 64.0, 51.0, 44.0, 64.0, 46.0, 39.0, 59.0, 39.0, 46.0, 59.0, 56.0, 42.0, 62.0, 42.0, 49.0, 42.0, 56.0, 68.0, 55.0, 48.0, 44.0, 29.5, 34.0, 34.0, 56.0, 76.0, 63.0, 83.0, 83.0, 63.0, 108.0, 88.0],
                         'Detector': ['CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'QPeak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 1000, 1000, 120, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 50, 1000, 50, 50, 1000, 1000, 50, 50, 5, 5, 1000, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 50, 50, 50, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 5, 50, 50, 5, 50, 50, 50, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 1000, 50, 1000, 5, 5, 1000, 5, 5, 5, 1000, 5, 5, 5, 5, 5, 1000, 5, 5, 5, 1000, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50], 'FrequencyStep(kHz)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 50, 50, 500, 500, 500, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 50, 500, 500, 50, 500, 500, 500, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 5, 5, 500, 500, 500, 500, 500, 500, 500, 500]}

CISPR_25_5_RE_class_2 = {'GroupName': ['Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV Band I', 'TV Band I', 'FM', 'FM', 'FM', 'TV Band III (analogue)', 'TV Band III (analogue)', 'TV Band IV', 'TV Band IV', 'DAB III', 'DAB III', 'TV Band III (digital)', 'TV Band III (digital)', 'DTTV', 'DTTV', 'DAB L Band', 'DAB L Band', 'SDARS', 'SDARS', '4G I', '4G I', '5G n71, 4G', '5G n71, 4G', '3G I', '3G I', '5G n12/n14/n28/n29, 4G', '5G n12/n14/n28/n29, 4G', '5G n20', '3G II', '3G II', '5G n20', '5G n5/n18/n26, 4G', '2G I', '2G I', '5G n5/n18/n26, 4G', '3G III', '3G III', '3G IV', '2G II', '5G n8, 4G', '5G n8, 4G', '2G II', '3G IV', '5G n50/n51/n74/n75/n76/n91/n92/n93, 4G', '3G V', '3G V', '5G n50/n51/n74/n75/n76/n91/n92/n93, 4G', '4G II', '4G II', '3G VI', '3G VI', '5G n3, 4G', '2G III', '2G III', '5G n3, 4G', '3G VII', '3G VII', '2G IV', '2G IV', '5G n39/n2/n25/n70/n34, 4G', '5G n39/n2/n25/n70/n34, 4G', '5G n1/n65/n66, 4G', '3G VIII', '5G n1/n65/n66, 4G', '3G VIII', '3G IX', '5G n30/n40, 4G', '3G IX', '5G n30/n40, 4G', '5G n53', '5G n53', '3G X', '3G X', '5G n7/n38/n41/n90, 4G', '5G n7/n38/n41/n90, 4G', '3G XI', '3G XI', '5G n48/n77/n78, 4G', '5G n48/n77/n78, 4G', '5G n79', '5G n79', '4G III', '4G III', '5G n47, V2X', '5G n47, V2X', 'CB', 'CB', 'CB', 'VHF I', 'VHF I', 'VHF I', 'VHF II', 'VHF II', 'VHF II', 'VHF III', 'VHF III', 'VHF III', 'RKE & TPMS 1', 'RKE & TPMS 1', 'Analogue UHF I', 'Analogue UHF I', 'Analogue UHF I', 'RKE & TPMS 2', 'RKE & TPMS 2', 'Analogue UHF II', 'Analogue UHF II', 'Analogue UHF II', 'GPS L5', 'BDS, B1I', 'GPS L1', 'GLONASS L1', 'WiFi / Bluetooth', 'WiFi / Bluetooth', 'WiFi I', 'WiFi I', 'WiFi II', 'WiFi II', 'B2X (WiFi)', 'B2X (WiFi)'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 174.0, 174.0, 470.0, 470.0, 171.0, 171.0, 174.0, 174.0, 470.0, 470.0, 1447.0, 1447.0, 2320.0, 2320.0, 460.0, 460.0, 617.0, 617.0, 703.0, 703.0, 703.0, 703.0, 791.0, 791.0, 791.0, 791.0, 852.0, 852.0, 852.0, 852.0, 852.0, 852.0, 925.0, 925.0, 925.0, 925.0, 925.0, 925.0, 1427.0, 1427.0, 1427.0, 1427.0, 1525.0, 1525.0, 1805.0, 1805.0, 1805.0, 1805.0, 1805.0, 1805.0, 1850.0, 1850.0, 1850.0, 1850.0, 1850.0, 1850.0, 2110.0, 2110.0, 2110.0, 2110.0, 2300.0, 2300.0, 2300.0, 2300.0, 2483.5, 2483.5, 2496.0, 2496.0, 2496.0, 2496.0, 3300.0, 3300.0, 3300.0, 3300.0, 4400.0, 4400.0, 5150.0, 5150.0, 5855.0, 5855.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0, 142.0, 142.0, 142.0, 300.0, 300.0, 380.0, 380.0, 380.0, 420.0, 420.0, 820.0, 820.0, 820.0, 1156.45, 1553.098, 1567.42, 1590.781, 2402.0, 2402.0, 5150.0, 5150.0, 5470.0, 5470.0, 5850.0, 5850.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 230.0, 230.0, 944.0, 944.0, 245.0, 245.0, 230.0, 230.0, 770.0, 770.0, 1494.0, 1494.0, 2345.0, 2345.0, 467.5, 467.5, 652.0, 652.0, 803.0, 803.0, 803.0, 803.0, 821.0, 821.0, 821.0, 821.0, 894.0, 894.0, 894.0, 894.0, 894.0, 894.0, 960.0, 960.0, 960.0, 960.0, 960.0, 960.0, 1518.0, 1518.0, 1518.0, 1518.0, 1559.0, 1559.0, 1880.0, 1880.0, 1880.0, 1880.0, 1880.0, 1880.0, 2025.0, 2025.0, 2025.0, 2025.0, 2025.0, 2025.0, 2200.0, 2200.0, 2200.0, 2200.0, 2400.0, 2400.0, 2400.0, 2400.0, 2495.0, 2495.0, 2690.0, 2690.0, 2690.0, 2690.0, 4200.0, 4200.0, 4200.0, 4200.0, 5000.0, 5000.0, 5925.0, 5925.0, 5925.0, 5925.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0, 175.0, 175.0, 175.0, 330.0, 330.0, 512.0, 512.0, 512.0, 450.0, 450.0, 960.0, 960.0, 960.0, 1196.45, 1569.098, 1583.42, 1616.594, 2494.0, 2494.0, 5350.0, 5350.0, 5725.0, 5725.0, 5925.0, 5925.0],
                         'Level Start(dBµV/m)': [76.0, 63.0, 56.0, 44.0, 51.0, 64.0, 58.0, 45.0, 38.0, 46.0, 36.0, 36.0, 56.0, 43.0, 28.0, 38.0, 59.0, 49.0, 48.0, 38.0, 48.0, 38.0, 64.0, 54.0, 72.0, 62.0, 66.0, 76.0, 62.0, 42.0, 64.0, 44.0, 39.0, 59.0, 65.0, 45.0, 46.0, 40.0, 60.0, 66.0, 67.0, 41.0, 61.0, 47.0, 41.0, 61.0, 62.0, 42.0, 48.0, 68.0, 62.0, 42.0, 51.0, 65.0, 45.0, 71.0, 52.0, 72.0, 47.0, 67.0, 53.0, 47.0, 67.0, 73.0, 68.0, 48.0, 48.0, 68.0, 54.0, 74.0, 55.0, 69.0, 75.0, 49.0, 50.0, 56.0, 70.0, 76.0, 56.0, 76.0, 70.0, 50.0, 76.0, 56.0, 53.0, 73.0, 79.0, 59.0, 81.0, 61.0, 63.0, 83.0, 84.0, 64.0, 45.0, 38.0, 58.0, 38.0, 45.0, 58.0, 40.0, 33.0, 53.0, 33.0, 53.0, 40.0, 36.0, 50.0, 36.0, 43.0, 56.0, 50.0, 36.0, 42.0, 49.0, 62.0, 38.0, 23.5, 28.0, 28.0, 50.0, 70.0, 77.0, 57.0, 77.0, 57.0, 102.0, 82.0],
                         'Level Stop(dBµV/m)': [76.0, 63.0, 56.0, 44.0, 51.0, 64.0, 58.0, 45.0, 38.0, 46.0, 36.0, 36.0, 56.0, 43.0, 28.0, 38.0, 59.0, 49.0, 48.0, 38.0, 48.0, 38.0, 64.0, 54.0, 72.0, 62.0, 66.0, 76.0, 62.0, 42.0, 64.0, 44.0, 39.0, 59.0, 65.0, 45.0, 46.0, 40.0, 60.0, 66.0, 67.0, 41.0, 61.0, 47.0, 41.0, 61.0, 62.0, 42.0, 48.0, 68.0, 62.0, 42.0, 51.0, 65.0, 45.0, 71.0, 52.0, 72.0, 47.0, 67.0, 53.0, 47.0, 67.0, 73.0, 68.0, 48.0, 48.0, 68.0, 54.0, 74.0, 55.0, 69.0, 75.0, 49.0, 50.0, 56.0, 70.0, 76.0, 56.0, 76.0, 70.0, 50.0, 76.0, 56.0, 53.0, 73.0, 79.0, 59.0, 81.0, 61.0, 63.0, 83.0, 84.0, 64.0, 45.0, 38.0, 58.0, 38.0, 45.0, 58.0, 40.0, 33.0, 53.0, 33.0, 53.0, 40.0, 36.0, 50.0, 36.0, 43.0, 56.0, 50.0, 36.0, 42.0, 49.0, 62.0, 38.0, 23.5, 28.0, 28.0, 50.0, 70.0, 77.0, 57.0, 77.0, 57.0, 102.0, 82.0],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'QPeak', 'Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'QPeak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 120, 1000, 1000, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 5, 5, 1000, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 50, 50, 50, 50, 5, 50, 50, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 50, 50, 50, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 1000, 50, 50, 5, 1000, 5, 1000, 5, 5, 5, 5, 1000, 5, 5, 5, 1000, 5, 5, 5, 5, 1000, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50], 'FrequencyStep(kHz)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 50, 50, 500, 500, 500, 500, 50, 500, 500, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 50, 50, 500, 500, 500, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 5, 5, 500, 500, 500, 500, 500, 500, 500, 500]}

CISPR_25_5_RE_class_3 = {'GroupName': ['Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV Band I', 'TV Band I', 'FM', 'FM', 'FM', 'TV Band III (analogue)', 'TV Band III (analogue)', 'TV Band IV', 'TV Band IV', 'DAB III', 'DAB III', 'TV Band III (digital)', 'TV Band III (digital)', 'DTTV', 'DTTV', 'DAB L Band', 'DAB L Band', 'SDARS', 'SDARS', '4G I', '4G I', '5G n71, 4G', '5G n71, 4G', '5G n12/n14/n28/n29, 4G', '5G n12/n14/n28/n29, 4G', '3G I', '3G I', '5G n20', '5G n20', '3G II', '3G II', '2G I', '2G I', '5G n5/n18/n26, 4G', '5G n5/n18/n26, 4G', '3G III', '3G III', '2G II', '2G II', '3G IV', '3G IV', '5G n8, 4G', '5G n8, 4G', '5G n50/n51/n74/n75/n76/n91/n92/n93, 4G', '5G n50/n51/n74/n75/n76/n91/n92/n93, 4G', '3G V', '3G V', '4G II', '4G II', '2G III', '2G III', '3G VI', '3G VI', '5G n3, 4G', '5G n3, 4G', '3G VII', '3G VII', '5G n39/n2/n25/n70/n34, 4G', '5G n39/n2/n25/n70/n34, 4G', '2G IV', '2G IV', '3G VIII', '3G VIII', '5G n1/n65/n66, 4G', '5G n1/n65/n66, 4G', '5G n30/n40, 4G', '5G n30/n40, 4G', '3G IX', '3G IX', '5G n53', '5G n53', '3G X', '3G X', '5G n7/n38/n41/n90, 4G', '5G n7/n38/n41/n90, 4G', '3G XI', '3G XI', '5G n48/n77/n78, 4G', '5G n48/n77/n78, 4G', '5G n79', '5G n79', '4G III', '4G III', '5G n47, V2X', '5G n47, V2X', 'CB', 'CB', 'CB', 'VHF I', 'VHF I', 'VHF I', 'VHF II', 'VHF II', 'VHF II', 'VHF III', 'VHF III', 'VHF III', 'RKE & TPMS 1', 'RKE & TPMS 1', 'Analogue UHF I', 'Analogue UHF I', 'Analogue UHF I', 'RKE & TPMS 2', 'RKE & TPMS 2', 'Analogue UHF II', 'Analogue UHF II', 'Analogue UHF II', 'GPS L5', 'BDS, B1I', 'GPS L1', 'GLONASS L1', 'WiFi / Bluetooth', 'WiFi / Bluetooth', 'WiFi I', 'WiFi I', 'WiFi II', 'WiFi II', 'B2X (WiFi)', 'B2X (WiFi)'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 174.0, 174.0, 470.0, 470.0, 171.0, 171.0, 174.0, 174.0, 470.0, 470.0, 1447.0, 1447.0, 2320.0, 2320.0, 460.0, 460.0, 617.0, 617.0, 703.0, 703.0, 703.0, 703.0, 791.0, 791.0, 791.0, 791.0, 852.0, 852.0, 852.0, 852.0, 852.0, 852.0, 925.0, 925.0, 925.0, 925.0, 925.0, 925.0, 1427.0, 1427.0, 1427.0, 1427.0, 1525.0, 1525.0, 1805.0, 1805.0, 1805.0, 1805.0, 1805.0, 1805.0, 1850.0, 1850.0, 1850.0, 1850.0, 1850.0, 1850.0, 2110.0, 2110.0, 2110.0, 2110.0, 2300.0, 2300.0, 2300.0, 2300.0, 2483.5, 2483.5, 2496.0, 2496.0, 2496.0, 2496.0, 3300.0, 3300.0, 3300.0, 3300.0, 4400.0, 4400.0, 5150.0, 5150.0, 5855.0, 5855.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0, 142.0, 142.0, 142.0, 300.0, 300.0, 380.0, 380.0, 380.0, 420.0, 420.0, 820.0, 820.0, 820.0, 1156.45, 1553.098, 1567.42, 1590.781, 2402.0, 2402.0, 5150.0, 5150.0, 5470.0, 5470.0, 5850.0, 5850.0], 'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 230.0, 230.0, 944.0, 944.0, 245.0, 245.0, 230.0, 230.0, 770.0, 770.0, 1494.0, 1494.0, 2345.0, 2345.0, 467.5, 467.5, 652.0, 652.0, 803.0, 803.0, 803.0, 803.0, 821.0, 821.0, 821.0, 821.0, 894.0, 894.0, 894.0, 894.0, 894.0, 894.0, 960.0, 960.0, 960.0, 960.0, 960.0, 960.0, 1518.0, 1518.0, 1518.0, 1518.0, 1559.0, 1559.0, 1880.0, 1880.0, 1880.0, 1880.0, 1880.0, 1880.0, 2025.0, 2025.0, 2025.0, 2025.0, 2025.0, 2025.0, 2200.0, 2200.0, 2200.0, 2200.0, 2400.0, 2400.0, 2400.0, 2400.0, 2495.0, 2495.0, 2690.0, 2690.0, 2690.0, 2690.0, 4200.0, 4200.0, 4200.0, 4200.0, 5000.0, 5000.0, 5925.0, 5925.0, 5925.0, 5925.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0, 175.0, 175.0, 175.0, 330.0, 330.0, 512.0, 512.0, 512.0, 450.0, 450.0, 960.0, 960.0, 960.0, 1196.45, 1569.098, 1583.42, 1616.594, 2494.0, 2494.0, 5350.0, 5350.0, 5725.0, 5725.0, 5925.0, 5925.0],
                         'Level Start(dBµV/m)': [66.0, 53.0, 46.0, 56.0, 43.0, 36.0, 52.0, 39.0, 32.0, 40.0, 30.0, 50.0, 37.0, 30.0, 32.0, 22.0, 53.0, 43.0, 42.0, 32.0, 42.0, 32.0, 58.0, 48.0, 66.0, 56.0, 70.0, 60.0, 56.0, 36.0, 58.0, 38.0, 59.0, 39.0, 53.0, 33.0, 60.0, 40.0, 54.0, 34.0, 55.0, 35.0, 61.0, 41.0, 55.0, 35.0, 56.0, 36.0, 56.0, 36.0, 62.0, 42.0, 65.0, 45.0, 59.0, 39.0, 66.0, 46.0, 61.0, 41.0, 61.0, 41.0, 67.0, 47.0, 62.0, 42.0, 68.0, 48.0, 62.0, 42.0, 63.0, 43.0, 69.0, 49.0, 70.0, 50.0, 64.0, 44.0, 70.0, 50.0, 64.0, 44.0, 70.0, 50.0, 67.0, 47.0, 73.0, 53.0, 75.0, 55.0, 77.0, 57.0, 78.0, 58.0, 52.0, 39.0, 32.0, 52.0, 39.0, 32.0, 47.0, 34.0, 27.0, 47.0, 34.0, 27.0, 44.0, 30.0, 50.0, 37.0, 30.0, 44.0, 30.0, 56.0, 43.0, 36.0, 32.0, 17.5, 22.0, 22.0, 64.0, 44.0, 71.0, 51.0, 71.0, 51.0, 96.0, 76.0],
                         'Level Stop(dBµV/m)': [66.0, 53.0, 46.0, 56.0, 43.0, 36.0, 52.0, 39.0, 32.0, 40.0, 30.0, 50.0, 37.0, 30.0, 32.0, 22.0, 53.0, 43.0, 42.0, 32.0, 42.0, 32.0, 58.0, 48.0, 66.0, 56.0, 70.0, 60.0, 56.0, 36.0, 58.0, 38.0, 59.0, 39.0, 53.0, 33.0, 60.0, 40.0, 54.0, 34.0, 55.0, 35.0, 61.0, 41.0, 55.0, 35.0, 56.0, 36.0, 56.0, 36.0, 62.0, 42.0, 65.0, 45.0, 59.0, 39.0, 66.0, 46.0, 61.0, 41.0, 61.0, 41.0, 67.0, 47.0, 62.0, 42.0, 68.0, 48.0, 62.0, 42.0, 63.0, 43.0, 69.0, 49.0, 70.0, 50.0, 64.0, 44.0, 70.0, 50.0, 64.0, 44.0, 70.0, 50.0, 67.0, 47.0, 73.0, 53.0, 75.0, 55.0, 77.0, 57.0, 78.0, 58.0, 52.0, 39.0, 32.0, 52.0, 39.0, 32.0, 47.0, 34.0, 27.0, 47.0, 34.0, 27.0, 44.0, 30.0, 50.0, 37.0, 30.0, 44.0, 30.0, 56.0, 43.0, 36.0, 32.0, 17.5, 22.0, 22.0, 64.0, 44.0, 71.0, 51.0, 71.0, 51.0, 96.0, 76.0],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 5, 1000, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 50, 50, 50, 50, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 1000, 50, 5, 1000, 5, 5, 1000, 5, 5, 1000, 5, 5, 5, 5, 1000, 5, 5, 5, 5, 1000, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50], 'FrequencyStep(kHz)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 50, 50, 500, 500, 500, 500, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 5, 5, 500, 500, 500, 500, 500, 500, 500, 500]}

CISPR_25_5_RE_class_4 = {'GroupName': ['Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Analogue broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital broadcast services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Digital mobile phone services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services', 'Mobile services'],
                         'BandName': ['LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'SW', 'TV Band I', 'TV Band I', 'FM', 'FM', 'FM', 'TV Band III (analogue)', 'TV Band III (analogue)', 'TV Band IV', 'TV Band IV', 'DAB III', 'DAB III', 'TV Band III (digital)', 'TV Band III (digital)', 'DTTV', 'DTTV', 'DAB L Band', 'DAB L Band', 'SDARS', 'SDARS', '4G I', '4G I', '5G n71, 4G', '5G n71, 4G', '5G n12/n14/n28/n29, 4G', '5G n12/n14/n28/n29, 4G', '3G I', '3G I', '3G II', '3G II', '5G n20', '5G n20', '3G III', '3G III', '2G I', '2G I', '5G n5/n18/n26, 4G', '5G n5/n18/n26, 4G', '2G II', '2G II', '5G n8, 4G', '5G n8, 4G', '3G IV', '3G IV', '3G V', '3G V', '5G n50/n51/n74/n75/n76/n91/n92/n93, 4G', '5G n50/n51/n74/n75/n76/n91/n92/n93, 4G', '4G II', '4G II', '2G III', '2G III', '5G n3, 4G', '5G n3, 4G', '3G VI', '3G VI', '5G n39/n2/n25/n70/n34, 4G', '5G n39/n2/n25/n70/n34, 4G', '3G VII', '3G VII', '2G IV', '2G IV', '3G VIII', '3G VIII', '5G n1/n65/n66, 4G', '5G n1/n65/n66, 4G', '3G IX', '3G IX', '5G n30/n40, 4G', '5G n30/n40, 4G', '5G n53', '5G n53', '5G n7/n38/n41/n90, 4G', '5G n7/n38/n41/n90, 4G', '3G X', '3G X', '5G n48/n77/n78, 4G', '5G n48/n77/n78, 4G', '3G XI', '3G XI', '5G n79', '5G n79', '4G III', '4G III', '5G n47, V2X', '5G n47, V2X', 'CB', 'CB', 'CB', 'VHF I', 'VHF I', 'VHF I', 'VHF II', 'VHF II', 'VHF II', 'VHF III', 'VHF III', 'VHF III', 'RKE & TPMS 1', 'RKE & TPMS 1', 'Analogue UHF I', 'Analogue UHF I', 'Analogue UHF I', 'RKE & TPMS 2', 'RKE & TPMS 2', 'Analogue UHF II', 'Analogue UHF II', 'Analogue UHF II', 'GPS L5', 'BDS, B1I', 'GPS L1', 'GLONASS L1', 'WiFi / Bluetooth', 'WiFi / Bluetooth', 'WiFi I', 'WiFi I', 'WiFi II', 'WiFi II', 'B2X (WiFi)', 'B2X (WiFi)'],
                         'F Start(MHz)': [0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 5.9, 41.0, 41.0, 76.0, 76.0, 76.0, 174.0, 174.0, 470.0, 470.0, 171.0, 171.0, 174.0, 174.0, 470.0, 470.0, 1447.0, 1447.0, 2320.0, 2320.0, 460.0, 460.0, 617.0, 617.0, 703.0, 703.0, 703.0, 703.0, 791.0, 791.0, 791.0, 791.0, 852.0, 852.0, 852.0, 852.0, 852.0, 852.0, 925.0, 925.0, 925.0, 925.0, 925.0, 925.0, 1427.0, 1427.0, 1427.0, 1427.0, 1525.0, 1525.0, 1805.0, 1805.0, 1805.0, 1805.0, 1805.0, 1805.0, 1850.0, 1850.0, 1850.0, 1850.0, 1850.0, 1850.0, 2110.0, 2110.0, 2110.0, 2110.0, 2300.0, 2300.0, 2300.0, 2300.0, 2483.5, 2483.5, 2496.0, 2496.0, 2496.0, 2496.0, 3300.0, 3300.0, 3300.0, 3300.0, 4400.0, 4400.0, 5150.0, 5150.0, 5855.0, 5855.0, 26.0, 26.0, 26.0, 30.0, 30.0, 30.0, 68.0, 68.0, 68.0, 142.0, 142.0, 142.0, 300.0, 300.0, 380.0, 380.0, 380.0, 420.0, 420.0, 820.0, 820.0, 820.0, 1156.45, 1553.098, 1567.42, 1590.781, 2402.0, 2402.0, 5150.0, 5150.0, 5470.0, 5470.0, 5850.0, 5850.0],
                         'F Stop(MHz)': [0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 6.2, 88.0, 88.0, 108.0, 108.0, 108.0, 230.0, 230.0, 944.0, 944.0, 245.0, 245.0, 230.0, 230.0, 770.0, 770.0, 1494.0, 1494.0, 2345.0, 2345.0, 467.5, 467.5, 652.0, 652.0, 803.0, 803.0, 803.0, 803.0, 821.0, 821.0, 821.0, 821.0, 894.0, 894.0, 894.0, 894.0, 894.0, 894.0, 960.0, 960.0, 960.0, 960.0, 960.0, 960.0, 1518.0, 1518.0, 1518.0, 1518.0, 1559.0, 1559.0, 1880.0, 1880.0, 1880.0, 1880.0, 1880.0, 1880.0, 2025.0, 2025.0, 2025.0, 2025.0, 2025.0, 2025.0, 2200.0, 2200.0, 2200.0, 2200.0, 2400.0, 2400.0, 2400.0, 2400.0, 2495.0, 2495.0, 2690.0, 2690.0, 2690.0, 2690.0, 4200.0, 4200.0, 4200.0, 4200.0, 5000.0, 5000.0, 5925.0, 5925.0, 5925.0, 5925.0, 28.0, 28.0, 28.0, 54.0, 54.0, 54.0, 87.0, 87.0, 87.0, 175.0, 175.0, 175.0, 330.0, 330.0, 512.0, 512.0, 512.0, 450.0, 450.0, 960.0, 960.0, 960.0, 1196.45, 1569.098, 1583.42, 1616.594, 2494.0, 2494.0, 5350.0, 5350.0, 5725.0, 5725.0, 5925.0, 5925.0],
                         'Level Start(dBµV/m)': [56.0, 43.0, 36.0, 48.0, 35.0, 28.0, 46.0, 33.0, 26.0, 34.0, 24.0, 44.0, 31.0, 24.0, 26.0, 16.0, 47.0, 37.0, 36.0, 26.0, 36.0, 26.0, 52.0, 42.0, 60.0, 50.0, 64.0, 54.0, 50.0, 30.0, 52.0, 32.0, 53.0, 33.0, 47.0, 27.0, 48.0, 28.0, 54.0, 34.0, 49.0, 29.0, 49.0, 29.0, 55.0, 35.0, 50.0, 30.0, 56.0, 36.0, 50.0, 30.0, 53.0, 33.0, 59.0, 39.0, 60.0, 40.0, 55.0, 35.0, 61.0, 41.0, 55.0, 35.0, 62.0, 42.0, 56.0, 36.0, 56.0, 36.0, 57.0, 37.0, 63.0, 43.0, 58.0, 38.0, 64.0, 44.0, 64.0, 44.0, 64.0, 44.0, 58.0, 38.0, 67.0, 47.0, 61.0, 41.0, 69.0, 49.0, 71.0, 51.0, 72.0, 52.0, 46.0, 33.0, 26.0, 46.0, 33.0, 26.0, 41.0, 28.0, 21.0, 41.0, 28.0, 21.0, 38.0, 24.0, 44.0, 31.0, 24.0, 38.0, 24.0, 50.0, 37.0, 30.0, 26.0, 11.5, 16.0, 16.0, 58.0, 38.0, 65.0, 45.0, 65.0, 45.0, 90.0, 70.0],
                         'Level Stop(dBµV/m)': [56.0, 43.0, 36.0, 48.0, 35.0, 28.0, 46.0, 33.0, 26.0, 34.0, 24.0, 44.0, 31.0, 24.0, 26.0, 16.0, 47.0, 37.0, 36.0, 26.0, 36.0, 26.0, 52.0, 42.0, 60.0, 50.0, 64.0, 54.0, 50.0, 30.0, 52.0, 32.0, 53.0, 33.0, 47.0, 27.0, 48.0, 28.0, 54.0, 34.0, 49.0, 29.0, 49.0, 29.0, 55.0, 35.0, 50.0, 30.0, 56.0, 36.0, 50.0, 30.0, 53.0, 33.0, 59.0, 39.0, 60.0, 40.0, 55.0, 35.0, 61.0, 41.0, 55.0, 35.0, 62.0, 42.0, 56.0, 36.0, 56.0, 36.0, 57.0, 37.0, 63.0, 43.0, 58.0, 38.0, 64.0, 44.0, 64.0, 44.0, 64.0, 44.0, 58.0, 38.0, 67.0, 47.0, 61.0, 41.0, 69.0, 49.0, 71.0, 51.0, 72.0, 52.0, 46.0, 33.0, 26.0, 46.0, 33.0, 26.0, 41.0, 28.0, 21.0, 41.0, 28.0, 21.0, 38.0, 24.0, 44.0, 31.0, 24.0, 38.0, 24.0, 50.0, 37.0, 30.0, 26.0, 11.5, 16.0, 16.0, 58.0, 38.0, 65.0, 45.0, 65.0, 45.0, 90.0, 70.0],
                         'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [50, 1000, 50, 50, 1000, 50, 50, 1000, 50, 5, 5, 5, 1000, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 50, 50, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 1000, 50, 5, 1000, 5, 5, 1000, 5, 5, 1000, 5, 5, 5, 5, 1000, 5, 5, 5, 5, 1000, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50], 'FrequencyStep(kHz)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 50, 50, 500, 500, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 50, 50, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 5, 5, 500, 500, 500, 500, 500, 500, 500, 500]}

FMC1278_CE420_HV = {'GroupName': ['CE420 Requirements - HV', 'CE420 Requirements - HV', 'CE420 Requirements - HV', 'CE420 Requirements - HV', 'CE420 Requirements - HV', 'CE420 Requirements - HV', 'CE420 Requirements - HV', 'CE420 Requirements - HV', 'CE420 Requirements - HV', 'CE420 Requirements - HV'],
                    'BandName': ['G1 - Medium Wave (AM)', 'G1 - Medium Wave (AM)', 'M0', 'M0', 'M1', 'M1', 'SA1 - FM1', 'SA1 - FM1', 'G3 - FM2', 'G3 - FM2'],
                    'F Start(MHz)': [0.53, 0.53, 20.0, 20.0, 30.0, 30.0, 75.0, 75.0, 87.5, 87.5],
                    'F Stop(MHz)': [1.7, 1.7, 30.0, 30.0, 75.0, 75.0, 90.0, 90.0, 108.0, 108.0],
                    'Level Start(dBµV)': [73, 66, 73, 60, 73, 60, 73, 60, 73, 60],
                    'Level Stop(dBµV)': [73, 66, 73, 60, 73, 60, 73, 60, 73, 60],
                    'Detector': ['QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg'],
                    'RBW(kHz)': [9, 9, 9, 9, 120, 120, 120, 120, 120, 120],
                    'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                    'MeasurementTime(ms)': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                    'FrequencyStep(kHz)': [4.5, 4.5, 4.5, 4.5, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0]}

FMC1278_CE420_LV = {'GroupName': ['CE420 Requirements - LV', 'CE420 Requirements - LV', 'CE420 Requirements - LV', 'CE420 Requirements - LV', 'CE420 Requirements - LV', 'CE420 Requirements - LV', 'CE420 Requirements - LV', 'CE420 Requirements - LV'],
                    'BandName': ['G1 - Medium Wave (AM)', 'G1 - Medium Wave (AM)', 'G1 - Medium Wave (AM) relaxed', 'G1 - Medium Wave (AM) relaxed', 'M0', 'M1', 'SA1 - FM1', 'G3 - FM2'],
                    'F Start(MHz)': [0.53, 0.53, 0.53, 0.53, 20.0, 30.0, 75.0, 87.5],
                    'F Stop(MHz)': [1.7, 1.7, 1.7, 1.7, 30.0, 75.0, 90.0, 108.0],
                    'Level Start(dBµV)': [66, 48, 76, 48, 36, 36, 36, 36],
                    'Level Stop(dBµV)': [66, 48, 76, 48, 36, 36, 36, 36],
                    'Detector': ['QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'QPeak', 'QPeak', 'QPeak'],
                    'RBW(kHz)': [9, 9, 9, 9, 9, 120, 120, 120],
                    'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                    'MeasurementTime(ms)': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                    'FrequencyStep(kHz)': [4.5, 4.5, 4.5, 4.5, 4.5, 60.0, 60.0, 60.0]}

FMC1278_RE310 = {'GroupName': ['Table 8-1 RE 310 Level 1 Requirement', 'Table 8-1 RE 310 Level 1 Requirement', 'Table 8-1 RE 310 Level 1 Requirement', 'Table 8-1 RE 310 Level 1 Requirement', 'Table 8-1 RE 310 Level 1 Requirement', 'Table 8-1 RE 310 Level 1 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement', 'Table 8-2 RE310 Level 2 Requirement'],
                 'BandName': ['M1', 'M1', 'M2', 'M2', 'M3', 'M3', 'G1 Medium Wave (AM) relaxed', 'G1 Medium Wave (AM) relaxed', 'G1 Medium Wave (AM)', 'G1 Medium Wave (AM)', 'NA1 DOT 1/Police (39-47.34)', 'NA1 DOT 1/Police (39-47.34)', 'NA1 DOT 1/Police (39-47.34)', 'SA1 FM1 (76-90)', 'SA1 FM1 (76-90)', 'SA1 FM1 (76-90)', 'G3 FM2 (87.5-108)', 'G3 FM2 (87.5-108)', 'G3 FM2 (87.5-108)', 'G4 2 Meter (142-175)', 'G4 2 Meter (142-175)', 'G4 2 Meter (142-175)', 'G5 DAB (174.1-240)', 'G5 DAB (174.1-240)', 'G5 DAB (174.1-240)', 'G6a RKE, TPMS 1', 'G6a RKE, TPMS 1', 'G6a RKE, TPMS 1', 'G7 Tetra', 'G7 Tetra', 'G7 Tetra', 'G6b RKE, TPMS 2', 'G6b RKE, TPMS 2', 'G6b RKE, TPMS 2', 'G6c RKE', 'G6c RKE', 'G6d RKE', 'G6d RKE', 'G8a GPS L5', 'G8b BEIDOU BDS B1I', 'G8b BEIDOU BDS B1I', 'G8b BEIDOU BDS B1I', 'G8c GPS L1 BEIDOU BDS B1C', 'G8c GPS L1 BEIDOU BDS B1C', 'G8c GPS L1 BEIDOU BDS B1C', 'G8d GNSS'],
                 'F Start(MHz)': [30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 0.53, 0.53, 0.53, 0.53, 39.0, 39.0, 39.0, 75.0, 75.0, 75.0, 86.0, 86.0, 86.0, 140.0, 140.0, 140.0, 172.0, 172.0, 172.0, 310.0, 310.0, 310.0, 380.0, 380.0, 380.0, 429.0, 429.0, 429.0, 868.0, 868.0, 902.0, 902.0, 1151.45, 1531.0, 1559.0, 1563.0, 1567.0, 1574.0, 1576.0, 1598.0],
                 'F Stop(MHz)': [75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 1.7, 1.7, 1.7, 1.7, 48.0, 48.0, 48.0, 91.0, 91.0, 91.0, 109.0, 109.0, 109.0, 176.0, 176.0, 176.0, 242.0, 242.0, 242.0, 320.0, 320.0, 320.0, 430.0, 430.0, 430.0, 439.0, 439.0, 439.0, 870.0, 870.0, 904.0, 904.0, 1201.45, 1559.0, 1563.0, 1591.0, 1574.0, 1576.0, 1583.0, 1605.0],
                 'Level Start(dBµV/m)': [52, 62, 42, 52, 53, 63, 58, 40, 42, 24, 24, 20, 12, 20, 24, 12, 20, 12, 24, 24, 12, 20, 16, 26, 20, 14, 30, 20, 14, 30, 20, 19, 30, 25, 30, 24, 24, 30, 14, 19, 4, 4, 44, 4, 4, 20],
                 'Level Stop(dBµV/m)': [42, 52, 53, 63, 53, 63, 58, 40, 42, 24, 24, 20, 12, 20, 24, 12, 20, 12, 24, 24, 12, 20, 16, 26, 20, 14, 30, 20, 14, 30, 20, 19, 30, 25, 30, 24, 24, 30, 14, 4, 4, 19, 4, 4, 44, 20],
                 'Detector': ['CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'QPeak', 'Peak', 'CISPR_Avg', 'QPeak', 'Peak', 'CISPR_Avg', 'QPeak', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg'], 'RBW(kHz)': [120, 120, 120, 120, 120, 120, 9, 9, 9, 9, 120, 9, 9, 9, 120, 9, 9, 9, 120, 120, 9, 9, 120, 120, 120, 9, 120, 9, 9, 120, 9, 9, 120, 9, 9, 9, 9, 9, 9, 1, 1, 1, 1, 1, 1, 9],
                 'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN'],
                 'MeasurementTime(ms)': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                 'FrequencyStep(kHz)': [60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 4.5, 4.5, 4.5, 4.5, 60.0, 4.5, 4.5, 4.5, 60.0, 4.5, 4.5, 4.5, 60.0, 60.0, 4.5, 4.5, 60.0, 60.0, 60.0, 4.5, 60.0, 4.5, 4.5, 60.0, 4.5, 4.5, 60.0, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 4.5]}

GMW3097_Table3_NonSpark = {'GroupName': ['30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Below 30M', 'Below 30M'], 'BandName': ['M1', 'NA1', 'NA1', 'NZ1', 'NZ1', 'M2', 'JA1', 'JA1', 'G3', 'G3', 'G4', 'G4', 'G5', 'G5', 'G6a', 'G6a', 'G6a', 'G7', 'M3', 'G6b', 'G6b', 'G6b', 'G8a', 'G8a', 'G8a', 'G8b', 'G8b', 'G8b', 'G8c', 'G1', 'G1'],
                           'F Start(MHz)': [30.0, 45.2, 45.2, 74.2, 74.2, 75.0, 75.2, 75.2, 86.6, 86.6, 140.6, 140.6, 172.4, 172.4, 310.0, 313.0, 317.0, 380.0, 400.0, 429.0, 432.0, 436.0, 1552.052, 1559.052, 1563.144, 1567.0, 1574.0, 1576.0, 1598.0, 0.53, 0.53],
                           'F Stop(MHz)': [75.0, 47.8, 47.8, 78.2, 78.2, 400.0, 90.9, 90.9, 109.1, 109.1, 176.3, 176.3, 242.4, 242.4, 313.0, 317.0, 320.0, 430.0, 1000.0, 432.0, 436.0, 439.0, 1559.052, 1563.144, 1570.144, 1574.0, 1576.0, 1583.0, 1606.0, 1.71, 1.71],
                           'Level Start(dBµV/m)': [52, 12, 20, 12, 20, 42, 20, 12, 20, 12, 12, 20, 20, 12, 20, 10, 20, 26, 53, 24, 14, 24, 44, 4, 4, 44, 4, 4, 20, 30, 24],
                           'Level Stop(dBµV/m)': [42, 12, 20, 12, 20, 53, 20, 12, 20, 12, 12, 20, 20, 12, 20, 10, 20, 26, 53, 24, 14, 24, 4, 4, 44, 4, 4, 44, 20, 30, 24],
                           'Detector': ['Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average'],
                           'RBW(kHz)': [120, 9, 9, 9, 9, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 9, 9, 9, 1, 1, 1, 1, 1, 1, 1, 9, 9],
                           'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                           'MeasurementTime(ms)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50], 'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_CV = {'GroupName': ['Basic limit values', 'Basic limit values', 'Basic limit values'],
               'BandName': ['CV_B1', 'CV_B2', 'CV_B3'],
               'F Start(MHz)': [0.15, 0.3, 0.5],
               'F Stop(MHz)': [0.3, 0.5, 30.0],
               'Level Start(dBµV)': [50, 50, 30],
               'Level Stop(dBµV)': [50, 30, 30],
               'Detector': ['Peak', 'Peak', 'Peak'],
               'RBW(kHz)': [9, 9, 9],
               'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN'],
               'MeasurementTime(ms)': [3000, 3000, 3000],
               'FrequencyStep(kHz)': [' ', ' ', ' ']}

GS_95002_2_AN_class_3 = {'GroupName': ['Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
                         'BandName': ['AN_B1', 'AN_B1', 'AN_B2', 'AN_B2', 'AN_B3', 'AN_B3', 'AN_B4', 'AN_B4', 'AN_B5', 'AN_B5', '1 - MW', '1 - MW', '2 - FM', '2 - FM', '7 - FM', '7 - FM', '8 - 4m/BOS', '8 - 4m/BOS'],
                         'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 0.52, 0.52, 70.0, 70.0, 13.5, 13.5, 84.015, 84.015],
                         'F Stop(MHz)': [0.52, 0.52, 5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 108.0, 108.0, 1.73, 1.73, 120.0, 120.0, 13.9, 13.9, 87.255, 87.255],
                         'Level Start(dBµV)': [97, 107, 65, 75, 65, 75, 52, 42, 55, 65, 57, 50, 31, 24, 45, 65, 53, 20],
                         'Level Stop(dBµV)': [65, 75, 65, 75, 42, 52, 52, 42, 55, 65, 57, 50, 31, 24, 45, 65, 53, 20],
                         'Detector': ['Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'Peak', 'Peak', 'Average'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 9, 9, 120, 120, 9, 9, 120, 9],
                         'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_AN_class_4 = {'GroupName': ['Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
                         'BandName': ['AN_B1', 'AN_B1', 'AN_B2', 'AN_B2', 'AN_B3', 'AN_B3', 'AN_B4', 'AN_B4', 'AN_B5', 'AN_B5', '1 - MW', '1 - MW', '2 - FM', '2 - FM', '7 - FM', '7 - FM', '8 - 4m/BOS', '8 - 4m/BOS'],
                         'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 0.52, 0.52, 70.0, 70.0, 13.5, 13.5, 84.015, 84.015],
                         'F Stop(MHz)': [0.52, 0.52, 5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 108.0, 108.0, 1.73, 1.73, 120.0, 120.0, 13.9, 13.9, 87.255, 87.255],
                         'Level Start(dBµV)': [97, 107, 65, 75, 75, 65, 42, 52, 65, 55, 49, 42, 25, 18, 39, 59, 47, 14],
                         'Level Stop(dBµV)': [65, 75, 65, 75, 52, 42, 42, 52, 65, 55, 49, 42, 25, 18, 39, 59, 47, 14],
                         'Detector': ['Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'Peak', 'Peak', 'Average'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 9, 9, 120, 120, 9, 9, 120, 9],
                         'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_AN_class_5 = {'GroupName': ['Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
                         'BandName': ['AN_B1', 'AN_B1', 'AN_B2', 'AN_B2', 'AN_B3', 'AN_B3', 'AN_B4', 'AN_B4', 'AN_B5', 'AN_B5', '1 - MW', '1 - MW', '2 - FM', '2 - FM', '7 - FM', '7 - FM', '8 - 4m/BOS', '8 - 4m/BOS'],
                         'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 0.52, 0.52, 70.0, 70.0, 13.5, 13.5, 84.015, 84.015],
                         'F Stop(MHz)': [0.52, 0.52, 5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 108.0, 108.0, 1.73, 1.73, 120.0, 120.0, 13.9, 13.9, 87.255, 87.255],
                         'Level Start(dBµV)': [97, 107, 75, 65, 75, 65, 42, 52, 55, 65, 41, 34, 12, 19, 33, 53, 8, 41],
                         'Level Stop(dBµV)': [65, 75, 75, 65, 52, 42, 42, 52, 55, 65, 41, 34, 12, 19, 33, 53, 8, 41],
                         'Detector': ['Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'QPeak', 'Average', 'Average', 'QPeak', 'Average', 'Peak', 'Average', 'Peak'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 9, 9, 120, 120, 9, 9, 9, 120],
                         'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 3000, 10000, 3000, 3000, 3000, 3000],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_RE_class_4 = {'GroupName': ['Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
                         'BandName': ['RE_B1', 'RE_B1', 'RE_B2', 'RE_B2', 'RE_B3', 'RE_B3', 'RE_B4', 'RE_B4', 'RE_B5', 'RE_B5', 'RE_B6', 'RE_B6', '1 - MW', '1 - MW', '2 - FM', '2 - FM', '4 - TV III', '3 - DAB', '5 - TV IV/V', '6 - SDARS', '6 - SDARS', '20 - SRD', '20 - SRD', '7 - NFC', '7 - NFC', '8 - 4m/BOS', '8 - 4m/BOS', '9 - 2m/Taxi', '9 - 2m/Taxi', '10 - 2m/BOS', '10 - 2m/BOS', '11 - 2m/BOS', '11 - 2m/BOS', '12 - SRD', '12 - SRD', '13 - Trunked Radio', '13 - Trunked Radio', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - SRD', '16 - SRD', '17 - Trunked Radio', '17 - Trunked Radio', '18 - 2G, 3G, 4G', '18 - 2G, 3G, 4G', '19 - PDC, D-AMPS', '19 - PDC, D-AMPS', '21 - 4G', '21 - 4G', '22 - GNSS', '23 - 2G, 3G, 4G', '23 - 2G, 3G, 4G', '24 - 4G', '24 - 4G', '25 - Bluetooth, WLAN', '25 - Bluetooth, WLAN', '26 - 4G', '26 - 4G', '27 - 5G', '27 - 5G', '28 - WLAN, C2X', '28 - WLAN, C2X'],
                         'F Start(MHz)': [0.15, 0.15, 5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 0.52, 0.52, 70.0, 70.0, 170.0, 174.0, 470.0, 2320.0, 2320.0, 0.000868, 0.000868, 13.5, 13.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 717.0, 717.0, 851.0, 851.0, 1427.0, 1427.0, 1553.0, 1805.0, 1805.0, 2300.0, 2300.0, 2402.0, 2402.0, 2496.0, 2496.0, 3400.0, 3400.0, 5150.0, 5150.0],
                         'F Stop(MHz)': [5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 1.73, 1.73, 120.0, 120.0, 230.0, 241.0, 806.0, 2345.0, 2345.0, 0.000876, 0.000876, 13.9, 13.9, 87.255, 87.255, 164.0, 164.0, 169.83, 169.83, 173.98, 173.98, 317.0, 317.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 894.0, 894.0, 1518.0, 1518.0, 1610.0, 2200.0, 2200.0, 2400.0, 2400.0, 2497.0, 2497.0, 2690.0, 2690.0, 3800.0, 3800.0, 5925.0, 5925.0],
                         'Level Start(dBµV/m)': [52, 62, 62, 52, 29, 39, 42, 52, 42, 52, 63, 53, 33, 26, 25, 18, 28, 28, 35, 62, 52, 26, 46, 24, 44, 41, 8, 8, 41, 8, 41, 8, 41, 40, 20, 25, 45, 45, 25, 25, 45, 20, 40, 45, 25, 37, 57, 37, 57, 41, 61, 26, 57, 37, 44, 64, 72, 52, 44, 64, 52, 72, 52, 72],
                         'Level Stop(dBµV/m)': [52, 62, 39, 29, 29, 39, 42, 52, 53, 63, 63, 53, 33, 26, 25, 18, 28, 28, 35, 62, 52, 26, 46, 24, 44, 41, 8, 8, 41, 8, 41, 8, 41, 40, 20, 25, 45, 45, 25, 25, 45, 20, 40, 45, 25, 37, 57, 37, 57, 41, 61, 26, 57, 37, 44, 64, 72, 52, 44, 64, 52, 72, 52, 72],
                         'Detector': ['Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 9, 9, 9, 9, 120, 9, 9, 120, 9, 120, 9, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 120, 120, 1000, 1000, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_RE_class_5 = {'GroupName': ['Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Basic limit values', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Broadcasting', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
                         'BandName': ['RE_B1', 'RE_B1', 'RE_B2', 'RE_B2', 'RE_B3', 'RE_B3', 'RE_B4', 'RE_B4', 'RE_B5', 'RE_B5', 'RE_B6', 'RE_B6', '1 - MW', '1 - MW', '2 - FM', '2 - FM', '4 - TV III', '3 - DAB', '5 - TV IV/V', '6 - SDARS', '6 - SDARS', '20 - SRD', '20 - SRD', '7 - NFC', '7 - NFC', '8 - 4m/BOS', '8 - 4m/BOS', '9 - 2m/Taxi', '9 - 2m/Taxi', '10 - 2m/BOS', '10 - 2m/BOS', '11 - 2m/BOS', '11 - 2m/BOS', '12 - SRD', '12 - SRD', '13 - Trunked Radio', '13 - Trunked Radio', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - SRD', '16 - SRD', '17 - Trunked Radio', '17 - Trunked Radio', '18 - 2G, 3G, 4G', '18 - 2G, 3G, 4G', '19 - PDC, D-AMPS', '19 - PDC, D-AMPS', '21 - 4G', '21 - 4G', '22 - GNSS', '23 - 2G, 3G, 4G', '23 - 2G, 3G, 4G', '24 - 4G', '24 - 4G', '25 - Bluetooth, WLAN', '25 - Bluetooth, WLAN', '26 - 4G', '26 - 4G', '27 - 5G', '27 - 5G', '28 - WLAN, C2X', '28 - WLAN, C2X'],
                         'F Start(MHz)': [0.15, 0.15, 5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 0.52, 0.52, 70.0, 70.0, 170.0, 174.0, 470.0, 2320.0, 2320.0, 0.000868, 0.000868, 13.5, 13.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 717.0, 717.0, 851.0, 851.0, 1427.0, 1427.0, 1553.0, 1805.0, 1805.0, 2300.0, 2300.0, 2402.0, 2402.0, 2496.0, 2496.0, 3400.0, 3400.0, 5150.0, 5150.0],
                         'F Stop(MHz)': [5.35, 5.35, 20.0, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 1.73, 1.73, 120.0, 120.0, 230.0, 241.0, 806.0, 2345.0, 2345.0, 0.000876, 0.000876, 13.9, 13.9, 87.255, 87.255, 164.0, 164.0, 169.83, 169.83, 173.98, 173.98, 317.0, 317.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 894.0, 894.0, 1518.0, 1518.0, 1610.0, 2200.0, 2200.0, 2400.0, 2400.0, 2497.0, 2497.0, 2690.0, 2690.0, 3800.0, 3800.0, 5925.0, 5925.0],
                         'Level Start(dBµV/m)': [62, 52, 62, 52, 29, 39, 52, 42, 52, 42, 53, 63, 25, 18, 19, 12, 22, 22, 29, 56, 46, 40, 20, 38, 18, 2, 35, 35, 2, 2, 35, 2, 35, 34, 14, 39, 19, 19, 39, 19, 39, 39, 14, 39, 19, 51, 31, 51, 31, 55, 35, 20, 31, 51, 58, 38, 46, 66, 58, 38, 46, 66, 66, 46],
                         'Level Stop(dBµV/m)': [62, 52, 39, 29, 29, 39, 52, 42, 63, 53, 53, 63, 25, 18, 19, 12, 22, 22, 29, 56, 46, 40, 20, 38, 18, 2, 35, 35, 2, 2, 35, 2, 35, 34, 14, 39, 19, 19, 39, 19, 39, 39, 14, 39, 19, 51, 31, 51, 31, 55, 35, 20, 31, 51, 58, 38, 46, 66, 58, 38, 46, 66, 66, 46],
                         'Detector': ['Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average'],
                         'RBW(kHz)': [9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 9, 9, 9, 9, 9, 120, 120, 9, 9, 120, 9, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 120, 120, 1000, 1000, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_SL_class_3 = {'GroupName': ['Basic limit values', 'Basic limit values', 'Broadcasting', 'Broadcasting', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
                         'BandName': ['SL_B1', 'SL_B1', '2 - FM', '2 - FM', '4 - TV III', '3 - DAB', '5 - TV IV/V', '8 - 4m/BOS', '8 - 4m/BOS', '9 - 2m/Taxi', '9 - 2m/Taxi', '10 - 2m/BOS', '10 - 2m/BOS', '11 - 2m/BOS', '11 - 2m/BOS', '12 - SRD', '12 - SRD', '13 - Trunked Radio', '13 - Trunked Radio', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - SRD', '16 - SRD', '17 - Trunked Radio', '17 - Trunked Radio', '18 - 2G, 3G, 4G', '18 - 2G, 3G, 4G', '19 - PDC, D-AMPS', '19 - PDC, D-AMPS', '20 - SRD', '20 - SRD'],
                         'F Start(MHz)': [30.0, 30.0, 70.0, 70.0, 170.0, 174.0, 470.0, 84.015, 84.015, 147.0, 147.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 717.0, 717.0, 851.0, 851.0, 868.0, 868.0],
                         'F Stop(MHz)': [960.0, 960.0, 120.0, 120.0, 230.0, 241.0, 806.0, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 894.0, 894.0, 876.0, 876.0],
                         'Level Start(dBµV)': [71, 61, 25, 18, 28, 28, 28, 41, 8, 8, 41, 41, 8, 8, 41, 27, 7, 38, 18, 38, 18, 18, 38, 27, 7, 18, 38, 44, 24, 44, 24, 33, 13],
                         'Level Stop(dBµV)': [71, 61, 25, 18, 28, 28, 28, 41, 8, 8, 41, 41, 8, 8, 41, 27, 7, 38, 18, 38, 18, 18, 38, 27, 7, 18, 38, 44, 24, 44, 24, 33, 13],
                         'Detector': ['Peak', 'Average', 'QPeak', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average'],
                         'RBW(kHz)': [120, 120, 120, 120, 1000, 1000, 1000, 120, 9, 9, 120, 120, 9, 9, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_SL_class_4 = {'GroupName': ['Basic limit values', 'Basic limit values', 'Broadcasting', 'Broadcasting', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
                         'BandName': ['SL_B1', 'SL_B1', '2 - FM', '2 - FM', '4 - TV III', '3 - DAB', '5 - TV IV/V', '8 - 4m/BOS', '8 - 4m/BOS', '9 - 2m/Taxi', '9 - 2m/Taxi', '10 - 2m/BOS', '10 - 2m/BOS', '11 - 2m/BOS', '11 - 2m/BOS', '12 - SRD', '12 - SRD', '13 - Trunked Radio', '13 - Trunked Radio', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - SRD', '16 - SRD', '17 - Trunked Radio', '17 - Trunked Radio', '18 - 2G, 3G, 4G', '18 - 2G, 3G, 4G', '19 - PDC, D-AMPS', '19 - PDC, D-AMPS', '20 - SRD', '20 - SRD'],
                         'F Start(MHz)': [30.0, 30.0, 70.0, 70.0, 170.0, 174.0, 470.0, 84.015, 84.015, 147.0, 147.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 717.0, 717.0, 851.0, 851.0, 868.0, 868.0],
                         'F Stop(MHz)': [960.0, 960.0, 120.0, 120.0, 230.0, 241.0, 806.0, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 894.0, 894.0, 876.0, 876.0],
                         'Level Start(dBµV)': [61, 71, 12, 19, 22, 22, 22, 2, 35, 2, 35, 2, 35, 35, 2, 21, 1, 32, 12, 32, 12, 32, 12, 21, 1, 12, 32, 18, 38, 38, 18, 7, 27],
                         'Level Stop(dBµV)': [61, 71, 12, 19, 22, 22, 22, 2, 35, 2, 35, 2, 35, 35, 2, 21, 1, 32, 12, 32, 12, 32, 12, 21, 1, 12, 32, 18, 38, 38, 18, 7, 27],
                         'Detector': ['Average', 'Peak', 'Average', 'QPeak', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak'],
                         'RBW(kHz)': [120, 120, 120, 120, 1000, 1000, 1000, 9, 120, 9, 120, 9, 120, 120, 9, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [3000, 3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                         'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_SL_class_5 = {'GroupName': ['Basic limit values', 'Basic limit values', 'Broadcasting', 'Broadcasting', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Broadcasting – Digital', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
                         'BandName': ['SL_B1', 'SL_B1', '2 - FM', '2 - FM', '4 - TV III', '3 - DAB', '5 - TV IV/V', '8 - 4m/BOS', '8 - 4m/BOS', '9 - 2m/Taxi', '9 - 2m/Taxi', '10 - 2m/BOS', '10 - 2m/BOS', '11 - 2m/BOS', '11 - 2m/BOS', '12 - SRD', '12 - SRD', '13 - Trunked Radio', '13 - Trunked Radio', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - SRD', '16 - SRD', '17 - Trunked Radio', '17 - Trunked Radio', '18 - 2G, 3G, 4G', '18 - 2G, 3G, 4G', '19 - PDC, D-AMPS', '19 - PDC, D-AMPS', '20 - SRD', '20 - SRD'],
                         'F Start(MHz)': [30.0, 30.0, 70.0, 70.0, 170.0, 174.0, 470.0, 84.015, 84.015, 147.0, 147.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 717.0, 717.0, 851.0, 851.0, 868.0, 868.0],
                         'F Stop(MHz)': [960.0, 960.0, 120.0, 120.0, 230.0, 241.0, 806.0, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 894.0, 894.0, 876.0, 876.0],
                         'Level Start(dBµV)': [71, 61, 13, 6, 16, 16, 16, 29, -4, -4, 29, 29, -4, -4, 29, 15, -5, 26, 6, 26, 6, 26, 6, -5, 15, 26, 6, 32, 12, 12, 32, 21, 1],
                         'Level Stop(dBµV)': [71, 61, 13, 6, 16, 16, 16, 29, -4, -4, 29, 29, -4, -4, 29, 15, -5, 26, 6, 26, 6, 26, 6, -5, 15, 26, 6, 32, 12, 12, 32, 21, 1],
                         'Detector': ['Peak', 'Average', 'QPeak', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average'],
                         'RBW(kHz)': [120, 120, 120, 120, 1000, 1000, 1000, 120, 9, 9, 120, 120, 9, 9, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9],
                         'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                         'MeasurementTime(ms)': [3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000]}

GS_95002_2_AN_Test_Class_3 = {'GroupName': ['Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Rundfunk', 'Rundfunk', 'Rundfunk', 'Rundfunk'],
                              'BandName': ['AN_B1', 'AN_B1', 'AN_B1', 'AN_B2', 'AN_B2', 'AN_B2', 'AN_B3', 'AN_B3', 'AN_B3', 'AN_B4', 'AN_B4', 'AN_B4', 'AN_B5', 'AN_B5', 'AN_B5', '7 - NFC', '7 - NFC', '8 - 8m/BOS', '8 - 8m/BOS', '9 - 4m/BOS', '9 - 4m/BOS', '1 - MW', '1 - MW', '2 - UKW', '2 - UKW'],
                              'F Start(MHz)': [0.15, 0.15, 0.15, 0.5, 0.5, 0.5, 9.46, 9.46, 9.46, 20.0, 20.0, 20.0, 30.0, 30.0, 30.0, 13.5, 13.5, 30.0, 30.0, 84.015, 84.015, 0.52, 0.52, 70.0, 70.0],
                              'F Stop(MHz)': [0.5, 0.5, 0.5, 9.46, 9.46, 9.46, 20.0, 20.0, 20.0, 30.0, 30.0, 30.0, 108.0, 108.0, 108.0, 13.9, 13.9, 50.0, 50.0, 87.255, 87.255, 1.73, 1.73, 120.0, 120.0],
                              'Level Start(dBµV)': [81, 74, 61, 75, 68, 55, 75, 68, 55, 62, 55, 42, 75, 65, 55, 65, 45, 53, 20, 53, 20, 57, 50, 31, 24],
                              'Level Stop(dBµV)': [81, 74, 61, 75, 68, 55, 62, 55, 42, 62, 55, 42, 75, 65, 55, 65, 45, 53, 20, 53, 20, 57, 50, 31, 24],
                              'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg'],
                              'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 9, 9, 120, 9, 120, 9, 9, 9, 120, 120],
                              'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                              'MeasurementTime(ms)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                              'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_AN_Test_Class_4 = {'GroupName': ['Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Rundfunk', 'Rundfunk', 'Rundfunk', 'Rundfunk'],
                              'BandName': ['AN_B1', 'AN_B1', 'AN_B1', 'AN_B2', 'AN_B2', 'AN_B2', 'AN_B3', 'AN_B3', 'AN_B3', 'AN_B4', 'AN_B4', 'AN_B4', 'AN_B5', 'AN_B5', 'AN_B5', '7 - NFC', '7 - NFC', '8 - 8m/BOS', '8 - 8m/BOS', '9 - 4m/BOS', '9 - 4m/BOS', '1 - MW', '1 - MW', '2 - UKW', '2 - UKW'],
                              'F Start(MHz)': [0.15, 0.15, 0.15, 0.5, 0.5, 0.5, 9.46, 9.46, 9.46, 20.0, 20.0, 20.0, 30.0, 30.0, 30.0, 13.5, 13.5, 30.0, 30.0, 84.015, 84.015, 0.52, 0.52, 70.0, 70.0],
                              'F Stop(MHz)': [0.5, 0.5, 0.5, 9.46, 9.46, 9.46, 20.0, 20.0, 20.0, 30.0, 30.0, 30.0, 108.0, 108.0, 108.0, 13.9, 13.9, 50.0, 50.0, 87.255, 87.255, 1.73, 1.73, 120.0, 120.0],
                              'Level Start(dBµV)': [81, 74, 61, 75, 68, 55, 75, 68, 55, 62, 55, 42, 75, 65, 55, 59, 39, 47, 14, 47, 14, 49, 42, 25, 18],
                              'Level Stop(dBµV)': [81, 74, 61, 75, 68, 55, 62, 55, 42, 62, 55, 42, 75, 65, 55, 59, 39, 47, 14, 47, 14, 49, 42, 25, 18],
                              'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg'],
                              'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 9, 9, 120, 9, 120, 9, 9, 9, 120, 120],
                              'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                              'MeasurementTime(ms)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                              'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_AN_Test_Class_5 = {'GroupName': ['Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Rundfunk', 'Rundfunk', 'Rundfunk', 'Rundfunk'],
                              'BandName': ['AN_B1', 'AN_B1', 'AN_B1', 'AN_B2', 'AN_B2', 'AN_B2', 'AN_B3', 'AN_B3', 'AN_B3', 'AN_B4', 'AN_B4', 'AN_B4', 'AN_B5', 'AN_B5', 'AN_B5', '7 - NFC', '7 - NFC', '8 - 8m/BOS', '8 - 8m/BOS', '9 - 4m/BOS', '9 - 4m/BOS', '1 - MW', '1 - MW', '2 - UKW', '2 - UKW'],
                              'F Start(MHz)': [0.15, 0.15, 0.15, 0.5, 0.5, 0.5, 9.46, 9.46, 9.46, 20.0, 20.0, 20.0, 30.0, 30.0, 30.0, 13.5, 13.5, 30.0, 30.0, 84.015, 84.015, 0.52, 0.52, 70.0, 70.0],
                              'F Stop(MHz)': [0.5, 0.5, 0.5, 9.46, 9.46, 9.46, 20.0, 20.0, 20.0, 30.0, 30.0, 30.0, 108.0, 108.0, 108.0, 13.9, 13.9, 50.0, 50.0, 87.255, 87.255, 1.73, 1.73, 120.0, 120.0],
                              'Level Start(dBµV)': [81, 74, 61, 75, 68, 55, 75, 68, 55, 62, 55, 42, 75, 65, 55, 53, 33, 41, 8, 41, 8, 41, 34, 19, 12],
                              'Level Stop(dBµV)': [81, 74, 61, 75, 68, 55, 62, 55, 42, 62, 55, 42, 75, 65, 55, 53, 33, 41, 8, 41, 8, 41, 34, 19, 12],
                              'Detector': ['Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg'],
                              'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 9, 9, 120, 9, 120, 9, 9, 9, 120, 120],
                              'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                              'MeasurementTime(ms)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                              'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_CV_Test = {'GroupName': ['Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte'],
                      'BandName': ['CV_B1', 'CV_B2', 'CV_B3'],
                      'F Start(MHz)': [0.15, 0.3, 0.5],
                      'F Stop(MHz)': [0.3, 0.5, 30.0],
                      'Level Start(dBµV)': [50, 50, 30],
                      'Level Stop(dBµV)': [50, 30, 30],
                      'Detector': ['Peak', 'Peak', 'Peak'],
                      'RBW(kHz)': [9, 9, 9],
                      'Interpolation': ['LOGLIN', 'LOGLOG', 'LOGLIN'],
                      'MeasurementTime(ms)': [' ', ' ', ' '],
                      'FrequencyStep(kHz)': [' ', ' ', ' ']}

GS_95002_2_RE_Test_Class_3 = {'GroupName': ['Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Rundfunk', 'Rundfunk', 'Rundfunk', 'Rundfunk', 'Rundfunk - Digital', 'Rundfunk - Digital', 'Rundfunk - Digital', 'Rundfunk - Digital', 'Rundfunk - Digital'],
                              'BandName': ['RE_B1', 'RE_B2', 'RE_B3', 'RE_B4', 'RE_B4', 'RE_B4', 'RE_B5', 'RE_B5', 'RE_B5', 'RE_B6', 'RE_B6', 'RE_B6', '7 - NFC', '7 - NFC', '8 - 8m/BOS', '8 - 8m/BOS', '9 - 4m/BOS', '9 - 4m/BOS', '10 - 2m/Taxi', '10 - 2m/Taxi', '11 - 2m/BOS', '11 - 2m/BOS', '12 - 2m/BOS', '12 - 2m/BOS', '13 - SRD', '13 - SRD', '14 - Bündelfunk', '14 - Bündelfunk', '15 - Bündelfunk', '15 - Bündelfunk', '16 - Bündelfunk', '16 - Bündelfunk', '17 - SRD', '17 - SRD', '18 - Bündelfunk', '18 - Bündelfunk', '19 - 2G, 3G, 4G', '19 - 2G, 3G, 4G', '20 - PDC, D-AMPS', '20 - PDC, D-AMPS', '21 - SRD', '21 - SRD', '22 - 4G', '22 - 4G', '23 - GNSS', '24 - 2G, 3G, 4G', '24 - 2G, 3G, 4G', '25 - 4G', '25 - 4G', '26 - Bluetooth, WLAN', '26 - Bluetooth, WLAN', '27 - 4G', '27 - 4G', '28 - 5G', '28 - 5G', '29 - WLAN, C2X', '29 - WLAN, C2X', '1 - MW', '1 - MW', '2 - UKW', '2 - UKW', '4 - TV III', '3 - DAB', '5 - TV IV/V', '6 - SDARS', '6 - SDARS'],
                              'F Start(MHz)': [0.15, 5.35, 20.0, 30.0, 30.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 13.5, 13.5, 30.0, 30.0, 84.015, 84.015, 144.0, 144.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 717.0, 717.0, 851.0, 851.0, 863.0, 863.0, 1427.0, 1427.0, 1553.0, 1805.0, 1805.0, 2300.0, 2300.0, 2402.0, 2402.0, 2496.0, 2496.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 70.0, 70.0, 170.0, 174.0, 470.0, 2320.0, 2320.0],
                              'F Stop(MHz)': [5.35, 20.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 1000.0, 13.9, 13.9, 50.0, 50.0, 87.255, 87.255, 174.0, 174.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 894.0, 894.0, 870.0, 870.0, 1518.0, 1518.0, 1610.0, 2200.0, 2200.0, 2400.0, 2400.0, 2497.0, 2497.0, 2690.0, 2690.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 120.0, 120.0, 230.0, 241.0, 806.0, 2345.0, 2345.0],
                              'Level Start(dBµV/m)': [62, 62, 39, 37, 57, 47, 57, 47, 37, 68, 58, 48, 50, 30, 14, 47, 47, 14, 47, 14, 14, 47, 14, 47, 26, 46, 51, 31, 31, 51, 51, 31, 26, 46, 31, 51, 63, 43, 43, 63, 32, 52, 67, 47, 32, 43, 63, 70, 50, 58, 78, 70, 50, 58, 78, 58, 78, 34, 41, 31, 24, 34, 28, 41, 58, 68],
                              'Level Stop(dBµV/m)': [62, 39, 39, 37, 57, 47, 68, 58, 48, 68, 58, 48, 50, 30, 14, 47, 47, 14, 47, 14, 14, 47, 14, 47, 26, 46, 51, 31, 31, 51, 51, 31, 26, 46, 31, 51, 63, 43, 43, 63, 32, 52, 67, 47, 32, 43, 63, 70, 50, 58, 78, 70, 50, 58, 78, 58, 78, 34, 41, 31, 24, 34, 28, 41, 58, 68],
                              'Detector': ['Peak', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak'], 'RBW(kHz)': [9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 120, 120, 9, 120, 9, 9, 120, 9, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 120, 120, 9, 9, 1000, 1000, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000],
                              'Interpolation': ['LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                              'MeasurementTime(ms)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                              'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_RE_Test_Class_4 = {'GroupName': ['Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Rundfunk', 'Rundfunk', 'Rundfunk', 'Rundfunk', 'Rundfunk - Digital', 'Rundfunk - Digital', 'Rundfunk - Digital', 'Rundfunk - Digital', 'Rundfunk - Digital'],
                              'BandName': ['RE_B1', 'RE_B2', 'RE_B3', 'RE_B4', 'RE_B4', 'RE_B4', 'RE_B5', 'RE_B5', 'RE_B5', 'RE_B6', 'RE_B6', 'RE_B6', '7 - NFC', '7 - NFC', '8 - 8m/BOS', '8 - 8m/BOS', '9 - 4m/BOS', '9 - 4m/BOS', '10 - 2m/Taxi', '10 - 2m/Taxi', '11 - 2m/BOS', '11 - 2m/BOS', '12 - 2m/BOS', '12 - 2m/BOS', '13 - SRD', '13 - SRD', '14 - Bündelfunk', '14 - Bündelfunk', '15 - Bündelfunk', '15 - Bündelfunk', '16 - Bündelfunk', '16 - Bündelfunk', '17 - SRD', '17 - SRD', '18 - Bündelfunk', '18 - Bündelfunk', '19 - 2G, 3G, 4G', '19 - 2G, 3G, 4G', '20 - PDC, D-AMPS', '20 - PDC, D-AMPS', '21 - SRD', '21 - SRD', '22 - 4G', '22 - 4G', '23 - GNSS', '24 - 2G, 3G, 4G', '24 - 2G, 3G, 4G', '25 - 4G', '25 - 4G', '26 - Bluetooth, WLAN', '26 - Bluetooth, WLAN', '27 - 4G', '27 - 4G', '28 - 5G', '28 - 5G', '29 - WLAN, C2X', '29 - WLAN, C2X', '1 - MW', '1 - MW', '2 - UKW', '2 - UKW', '4 - TV III', '3 - DAB', '5 - TV IV/V', '6 - SDARS', '6 - SDARS'],
                              'F Start(MHz)': [0.15, 5.35, 20.0, 30.0, 30.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 13.5, 13.5, 30.0, 30.0, 84.015, 84.015, 144.0, 144.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 717.0, 717.0, 851.0, 851.0, 863.0, 863.0, 1427.0, 1427.0, 1553.0, 1805.0, 1805.0, 2300.0, 2300.0, 2402.0, 2402.0, 2496.0, 2496.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 70.0, 70.0, 170.0, 174.0, 470.0, 2320.0, 2320.0],
                              'F Stop(MHz)': [5.35, 20.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 1000.0, 13.9, 13.9, 50.0, 50.0, 87.255, 87.255, 174.0, 174.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 894.0, 894.0, 870.0, 870.0, 1518.0, 1518.0, 1610.0, 2200.0, 2200.0, 2400.0, 2400.0, 2497.0, 2497.0, 2690.0, 2690.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 120.0, 120.0, 230.0, 241.0, 806.0, 2345.0, 2345.0],
                              'Level Start(dBµV/m)': [62, 62, 39, 37, 47, 57, 57, 47, 37, 48, 58, 68, 24, 44, 41, 8, 41, 8, 8, 41, 41, 8, 8, 41, 40, 20, 25, 45, 45, 25, 45, 25, 40, 20, 25, 45, 37, 57, 37, 57, 46, 26, 41, 61, 26, 57, 37, 64, 44, 52, 72, 44, 64, 72, 52, 52, 72, 26, 33, 25, 18, 28, 22, 35, 52, 62],
                              'Level Stop(dBµV/m)': [62, 39, 39, 37, 47, 57, 68, 58, 48, 48, 58, 68, 24, 44, 41, 8, 41, 8, 8, 41, 41, 8, 8, 41, 40, 20, 25, 45, 45, 25, 45, 25, 40, 20, 25, 45, 37, 57, 37, 57, 46, 26, 41, 61, 26, 57, 37, 64, 44, 52, 72, 44, 64, 72, 52, 52, 72, 26, 33, 25, 18, 28, 22, 35, 52, 62],
                              'Detector': ['Peak', 'Peak', 'Peak', 'CISPR_Avg', 'QPeak', 'Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'QPeak', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak'],
                              'RBW(kHz)': [9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 120, 9, 120, 9, 9, 120, 120, 9, 9, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 120, 120, 9, 9, 1000, 1000, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000],
                              'Interpolation': ['LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                              'MeasurementTime(ms)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                              'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

GS_95002_2_RE_Test_Class_5 = {'GroupName': ['Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Basisgrenzwerte', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Mobile und sonstige Dienste', 'Rundfunk', 'Rundfunk', 'Rundfunk', 'Rundfunk', 'Rundfunk - Digital', 'Rundfunk - Digital', 'Rundfunk - Digital', 'Rundfunk - Digital', 'Rundfunk - Digital'],
                              'BandName': ['RE_B1', 'RE_B2', 'RE_B3', 'RE_B4', 'RE_B4', 'RE_B4', 'RE_B5', 'RE_B5', 'RE_B5', 'RE_B6', 'RE_B6', 'RE_B6', '7 - NFC', '7 - NFC', '8 - 8m/BOS', '8 - 8m/BOS', '9 - 4m/BOS', '9 - 4m/BOS', '10 - 2m/Taxi', '10 - 2m/Taxi', '11 - 2m/BOS', '11 - 2m/BOS', '12 - 2m/BOS', '12 - 2m/BOS', '13 - SRD', '13 - SRD', '14 - Bündelfunk', '14 - Bündelfunk', '15 - Bündelfunk', '15 - Bündelfunk', '16 - Bündelfunk', '16 - Bündelfunk', '17 - SRD', '17 - SRD', '18 - Bündelfunk', '18 - Bündelfunk', '19 - 2G, 3G, 4G', '19 - 2G, 3G, 4G', '20 - PDC, D-AMPS', '20 - PDC, D-AMPS', '21 - SRD', '21 - SRD', '22 - 4G', '22 - 4G', '23 - GNSS', '24 - 2G, 3G, 4G', '24 - 2G, 3G, 4G', '25 - 4G', '25 - 4G', '26 - Bluetooth, WLAN', '26 - Bluetooth, WLAN', '27 - 4G', '27 - 4G', '28 - 5G', '28 - 5G', '29 - WLAN, C2X', '29 - WLAN, C2X', '1 - MW', '1 - MW', '2 - UKW', '2 - UKW', '4 - TV III', '3 - DAB', '5 - TV IV/V', '6 - SDARS', '6 - SDARS'],
                              'F Start(MHz)': [0.15, 5.35, 20.0, 30.0, 30.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 13.5, 13.5, 30.0, 30.0, 84.015, 84.015, 144.0, 144.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 717.0, 717.0, 851.0, 851.0, 863.0, 863.0, 1427.0, 1427.0, 1553.0, 1805.0, 1805.0, 2300.0, 2300.0, 2402.0, 2402.0, 2496.0, 2496.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 70.0, 70.0, 170.0, 174.0, 470.0, 2320.0, 2320.0],
                              'F Stop(MHz)': [5.35, 20.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 1000.0, 13.9, 13.9, 50.0, 50.0, 87.255, 87.255, 174.0, 174.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 894.0, 894.0, 870.0, 870.0, 1518.0, 1518.0, 1610.0, 2200.0, 2200.0, 2400.0, 2400.0, 2497.0, 2497.0, 2690.0, 2690.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 120.0, 120.0, 230.0, 241.0, 806.0, 2345.0, 2345.0],
                              'Level Start(dBµV/m)': [62, 62, 39, 57, 47, 37, 57, 47, 37, 48, 68, 58, 18, 38, 35, 2, 35, 2, 35, 2, 2, 35, 2, 35, 34, 14, 39, 19, 39, 19, 19, 39, 39, 14, 39, 19, 51, 31, 51, 31, 20, 40, 35, 55, 20, 31, 51, 58, 38, 46, 66, 58, 38, 46, 66, 46, 66, 25, 18, 19, 12, 22, 16, 29, 56, 46],
                              'Level Stop(dBµV/m)': [62, 39, 39, 57, 47, 37, 68, 58, 48, 48, 68, 58, 18, 38, 35, 2, 35, 2, 35, 2, 2, 35, 2, 35, 34, 14, 39, 19, 39, 19, 19, 39, 39, 14, 39, 19, 51, 31, 51, 31, 20, 40, 35, 55, 20, 31, 51, 58, 38, 46, 66, 58, 38, 46, 66, 46, 66, 25, 18, 19, 12, 22, 16, 29, 56, 46],
                              'Detector': ['Peak', 'Peak', 'Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                              'RBW(kHz)': [9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 120, 9, 120, 9, 120, 9, 9, 120, 9, 120, 9, 9, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 120, 120, 9, 9, 1000, 1000, 9, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000],
                              'Interpolation': ['LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                              'MeasurementTime(ms)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                              'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

MBN_10284_2_2019_10_AN = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting'],
                          'BandName': ['B1', 'B1', 'B2', 'B2', 'B3', 'B3', '9 - 4m/BOS', '9 - 4m/BOS', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF'],
                          'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 30.0, 30.0, 84.015, 84.015, 0.52, 0.52, 76.0, 76.0],
                          'F Stop(MHz)': [0.52, 0.52, 30.0, 30.0, 108.0, 108.0, 87.255, 87.255, 1.73, 1.73, 108.0, 108.0],
                          'Level Start(dBµV)': [97, 107, 65, 75, 55, 65, 8, 41, 41, 34, 25, 18],
                          'Level Stop(dBµV)': [65, 75, 65, 75, 55, 65, 8, 41, 41, 34, 25, 18],
                          'Detector': ['Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'QPeak', 'Average', 'QPeak', 'Average'],
                          'RBW(kHz)': [9, 9, 9, 9, 120, 120, 9, 120, 9, 9, 120, 120],
                          'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'], 'MeasurementTime(ms)': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000], 'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

MBN_10284_2_2019_10_NFA = {'GroupName': ['Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                           'BandName': ['9 (V) - 4m/BOS', '9 (V) - 4m/BOS', '10 - 2m/Taxi', '11 - 2m/BOS', '11 - 2m/BOS', '12 - 2m/BOS', '12 - 2m/BOS', '13 - SRD', '13 - SRD', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - SRD', '19 - SRD', '20 - Trunked Radio', '20 - Trunked Radio', '21 - 2G, 3G, 4G, 5G', '23 - GNSS (1)', '23 - GNSS (1)', '23 - GNSS (1)', '24 - 3G, 4G, 5G', '25 - GNSS (1)', '25 - GNSS (1)', '25 - GNSS (1)', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 5G', '28 - 5G', '29 - WLAN', '30 - DSRC', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '5 - TV III', '5 - TV III', '3 - DAB', '3 - DAB', '7 - TV IV/V', '7 - TV IV/V', '4 - SDARS', '4 - SDARS'],
                           'F Start(MHz)': [84.015, 84.015, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 380.15, 380.15, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 550.0, 1159.0, 1166.0, 1284.0, 1350.0, 1518.0, 1525.0, 1610.0, 1695.0, 3300.0, 4400.0, 5160.0, 5725.0, 0.52, 0.52, 76.0, 76.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0, 2320.0, 2320.0],
                           'F Stop(MHz)': [87.255, 87.255, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 380.15, 380.15, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 1166.0, 1284.0, 1291.0, 1518.0, 1525.0, 1610.0, 1617.0, 2900.0, 4200.0, 5000.0, 5720.0, 5925.0, 1.73, 1.73, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 710.0, 710.0, 2345.0, 2345.0],
                           'Level Start(dBµV/m)': [-10, 23, -10, 23, -10, 23, -10, 15, -5, 23, -10, 10, 43, 23, -10, 23, -10, 0, 23, -5, 15, 0, 23, 10, 35, -5, -5, 10, 35, -5, -5, 10, 10, 10, 10, 0, 0, 7, 0, 7, 10, 25, 10, 20, 10, 25, 25, 10],
                           'Level Stop(dBµV/m)': [-10, 23, -10, 23, -10, 23, -10, 15, -5, 23, -10, 10, 43, 23, -10, 23, -10, 0, 23, -5, 15, 0, 23, 10, -5, -5, 35, 10, -5, -5, 35, 10, 10, 10, 10, 0, 0, 7, 0, 7, 10, 25, 10, 20, 10, 25, 25, 10],
                           'Detector': ['Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average'],
                           'RBW(kHz)': [9, 120, 9, 120, 9, 120, 9, 9, 9, 120, 9, 9, 120, 120, 9, 120, 9, 120, 120, 9, 9, 120, 120, 1000, 9, 9, 9, 1000, 9, 9, 9, 1000, 1000, 1000, 1000, 1000, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000], 'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                           'MeasurementTime(ms)': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 3000, 1000, 1000, 1000], 'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

MBN_10284_2_2019_10_RE = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                          'BandName': ['B4', 'B5', 'B6', 'B7', 'B7', 'B8', 'B8', 'B9', 'B9', 'B10', 'B10', 'B11', 'B11', '9 (V) - 4m/BOS', '9 (V) - 4m/BOS', '10 - 2m/Taxi', '11 - 2m/BOS', '11 - 2m/BOS', '12 - 2m/BOS', '12 - 2m/BOS', '13 - SRD', '13 - SRD', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - SRD', '19 - SRD', '20 - Trunked Radio', '20 - Trunked Radio', '21 - 2G, 3G, 4G, 5G', '23 - GNSS (1)', '23 - GNSS (1)', '23 - GNSS (1)', '24 - 3G, 4G, 5G', '25 - GNSS (1)', '25 - GNSS (1)', '25 - GNSS (1)', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 5G', '28 - 5G', '29 - WLAN', '30 - DSRC', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '5 - TV III', '5 - TV III', '3 - DAB', '3 - DAB', '7 - TV IV/V', '7 - TV IV/V', '4 - SDARS', '4 - SDARS'],
                          'F Start(MHz)': [0.15, 5.35, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 84.015, 84.015, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 380.15, 380.15, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 550.0, 1159.0, 1166.0, 1284.0, 1350.0, 1518.0, 1525.0, 1610.0, 1695.0, 3300.0, 4400.0, 5160.0, 5725.0, 0.52, 0.52, 76.0, 76.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0, 2320.0, 2320.0],
                          'F Stop(MHz)': [5.35, 20.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 6000.0, 6000.0, 87.255, 87.255, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 380.15, 380.15, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 1166.0, 1284.0, 1291.0, 1518.0, 1525.0, 1610.0, 1617.0, 2900.0, 4200.0, 5000.0, 5720.0, 5925.0, 1.73, 1.73, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 710.0, 710.0, 2345.0, 2345.0],
                          'Level Start(dBµV/m)': [62, 62, 39, 52, 62, 42, 52, 53, 63, 60, 80, 84, 104, 35, 2, 2, 2, 35, 35, 2, 34, 14, 42, 9, 62, 29, 42, 9, 42, 9, 19, 42, 14, 34, 19, 42, 24, 52, 12, 12, 34, 55, 15, 15, 37, 45, 45, 48, 50, 25, 18, 12, 19, 22, 37, 22, 32, 40, 20, 46, 56],
                          'Level Stop(dBµV/m)': [62.0, 39.0, 39.0, 42.0, 52.0, 53.0, 63.0, 53.0, 63.0, 60.0, 80.0, 84.0, 104.0, 35.0, 2.0, 2.0, 2.0, 35.0, 35.0, 2.0, 34.0, 14.0, 42.0, 9.0, 62.0, 29.0, 42.0, 9.0, 42.0, 9.0, 19.0, 42.0, 14.0, 34.0, 19.0, 42.0, 28.8, 12.0, 12.0, 52.0, 34.0, 15.0, 15.0, 55.0, 42.0, 45.0, 45.0, 48.0, 50.0, 25.0, 18.0, 12.0, 19.0, 22.0, 37.0, 22.0, 32.0, 43.6, 23.6, 46.0, 56.0],
                          'Detector': ['Peak', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'QPeak', 'Average', 'Average', 'QPeak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak'],
                          'RBW(kHz)': [9, 9, 9, 120, 120, 120, 120, 120, 120, 1000, 1000, 1000, 1000, 120, 9, 9, 9, 120, 120, 9, 9, 9, 120, 9, 120, 9, 120, 9, 120, 9, 120, 120, 9, 9, 120, 120, 1000, 9, 9, 9, 1000, 9, 9, 9, 1000, 1000, 1000, 1000, 1000, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                          'Interpolation': ['LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN'],
                          'MeasurementTime(ms)': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 3000, 1000, 1000],
                          'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

MPS_GER_LAB_EMC_V01_AN = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits'],
                          'BandName': ['B1', 'B1', 'B2', 'B2'],
                          'F Start(MHz)': [0.15, 0.15, 30.0, 30.0],
                          'F Stop(MHz)': [30, 30, 108, 108],
                          'Level Start(dBµV)': [90, 100, 90, 100],
                          'Level Stop(dBµV)': [90, 100, 90, 100],
                          'Detector': ['Average', 'Peak', 'Average', 'Peak'],
                          'RBW(kHz)': [9, 9, 120, 120],
                          'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                          'MeasurementTime(ms)': [100, 100, 100, 100],
                          'FrequencyStep(kHz)': [' ', ' ', ' ', ' ']}

MPS_GER_LAB_EMC_V02_RE_class_5 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                                  'BandName': ['B4', 'B5', 'B6', 'B7', 'B8', 'B8', 'B9', 'B9', 'B10', 'B10', 'B11', 'B11', 'B12', 'B12', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - Trunked Radio', '19 - Trunked Radio', '21 - Trunked Radio', '21 - Trunked Radio', '25 - 3G, 4G, 5G', '25 - 3G, 4G, 5G', '26 - Beidou', '26 - Beidou', '26 - Beidou', '26 - GPS Galileo', '26 - GPS Galileo', '26 - GPS Galileo', '26 - GLONASS', '26 - GLONASS', '26 - GLONASS', '27 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '28 - 5G', '28 - 5G', '29 - WLAN, DSRC', '29 - WLAN, DSRC', ' C - LW', ' C - LW', ' C - LW', '1 - MW', '1 - MW', '2- SW 49m', '2- SW 49m', '2- SW 49m', '3 - VHF', '3 - VHF', 'C - TV Band I', 'C - TV Band I', 'C - DAB III', 'C - DAB III', 'C - TV Band III', 'C - TV Band III', 'C - TV Band IV', 'C - TV Band IV', '5 - SDARS', '5 - SDARS'],
                                  'F Start(MHz)': [0.009, 0.15, 5.35, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 0.1, 26.5, 26.5, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 460.0, 460.0, 1350.0, 1350.0, 1552.098, 1559.098, 1563.098, 1567.42, 1574.42, 1576.42, 1590.781, 1597.781, 1609.594, 1695.0, 1695.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.15, 0.15, 0.15, 0.52, 0.52, 5.8, 5.8, 5.8, 76.0, 76.0, 41.0, 41.0, 171.0, 171.0, 174.0, 174.0, 468.0, 468.0, 2320.0, 2320.0],
                                  'F Stop(MHz)': [0.15, 5.35, 20.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 6000.0, 6000.0, 0.15, 29.7, 29.7, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 470.0, 470.0, 1518.0, 1518.0, 1559.098, 1563.098, 1570.098, 1574.42, 1576.42, 1583.42, 1597.781, 1609.594, 1616.594, 2900.0, 2900.0, 3800.0, 3800.0, 5925.0, 5925.0, 0.3, 0.3, 0.3, 1.73, 1.73, 6.3, 6.3, 6.3, 108.0, 108.0, 88.0, 88.0, 245.0, 245.0, 230.0, 230.0, 944.0, 944.0, 2345.0, 2345.0],
                                  'Level Start(dBµV/m)': [86, 62, 62, 39, 62, 52, 42, 52, 53, 63, 60, 80, 84, 104, 41, 28, 48, 19, 39, 19, 39, 39, 19, 39, 19, 19, 39, 34, 54, 60, 20, 20, 60, 20, 20, 60, 20, 20, 37, 57, 65, 45, 68, 48, 26, 33, 46, 25, 18, 25, 18, 40, 19, 12, 18, 28, 16, 26, 22, 32, 31, 41, 46, 56],
                                  'Level Stop(dBµV/m)': [62, 62, 39, 39, 52, 42, 53, 63, 53, 63, 60, 80, 84, 104, 41, 28, 48, 19, 39, 19, 39, 39, 19, 39, 19, 19, 39, 34, 54, 20, 20, 60, 20, 20, 60, 20, 20, 60, 42, 62, 65, 45, 68, 48, 26, 33, 46, 25, 18, 25, 18, 40, 19, 12, 18, 28, 16, 26, 22, 32, 31, 41, 46, 56],
                                  'Detector': ['Peak', 'Peak', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'QPeak', 'Peak', 'QPeak', 'Average', 'QPeak', 'Average', 'Peak', 'QPeak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak'],
                                  'RBW(kHz)': [0.2, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0],
                                  'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                                  'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 10000, 3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                                  'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

PSA_B21_7110_MC03_Lacroix = {'GroupName': ['PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA', 'PSA'],
                             'BandName': ['Key less system', 'LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'CB', 'CB', 'VHF1', 'VHF1', 'VHF2', 'VHF2', 'FM', 'FM', 'FM'],
                             'F Start(MHz)': [0.1, 0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 26.0, 26.0, 30.0, 30.0, 68.0, 68.0, 76.0, 76.0, 76.0],
                             'F Stop(MHz)': [0.15, 0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 28.0, 28.0, 54.0, 54.0, 87.0, 87.0, 108.0, 108.0, 108.0],
                             'Level Start(dBµV)': [80, 80, 67, 60, 70, 57, 50, 65, 45, 56, 36, 62, 42, 44, 24, 44, 31, 24],
                             'Level Stop(dBµV)': [80, 80, 67, 60, 70, 57, 50, 65, 45, 56, 36, 62, 42, 44, 24, 44, 31, 24],
                             'Detector': ['Peak', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'QPeak', 'CISPR_Avg'],
                             'RBW(kHz)': [0.2, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0],
                             'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                             'MeasurementTime(ms)': [500, 50, 1000, 50, 5, 1000, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1000, 5],
                             'FrequencyStep(kHz)': [0.1, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]}

PSA_B21_7110_MR01_Permanent_Noise = {'GroupName': ['2004-104', '2004-104', '2004-104', '2004-104', '2004-104', '2004-104', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion'],
                                     'BandName': ['30-75', '30-75', '75-400', '75-400', '400-1000', '400-1000', 'CB', 'CB', 'VHF (1)', 'VHF (1)', 'VHF (2)', 'VHF (2)', 'VHF (3)', 'VHF (3)', 'Japan RKE', 'Japan RKE', 'Japan RKE', 'Japan RKE', 'Japan RKE', 'Japan RKE', 'analog UHF (1)', 'analog UHF (1)', 'RKE (General Case)', 'RKE (General Case)', 'RKE (General Case)', 'RKE (General Case)', 'RKE (General Case)', 'RKE (General Case)', '4G', '4G', 'analog UHF (2)', 'analog UHF (2)', 'GSM 800 and AMPS USA', 'GSM 800 and AMPS USA', 'EGSM/GSM 900 and PDC Japan', 'EGSM/GSM 900 and PDC Japan', 'PDC Japan', 'PDC Japan', 'COMPASS', 'COMPASS', 'COMPASS', 'COMPASS', 'COMPASS', 'COMPASS', 'GPS L1 Civil', 'GPS L1 Civil', 'GPS L1 Civil', 'GPS L1 Civil', 'GPS L1 Civil', 'GPS L1 Civil', 'GLONASS', 'GLONASS', 'GLONASS', 'GLONASS', 'GLONASS', 'GLONASS', 'GSM 1800 (PCN) and 4G', 'GSM 1800 (PCN) and 4G', 'GSM 1900', 'GSM 1900', '3G and PCS USA', '3G and PCS USA', '3G (1)', '3G (1)', '3G (2)', '3G (2)', 'Bluetooth / 802.11 / WiMAX / WLAM', 'Bluetooth / 802.11 / WiMAX / WLAM', '4G (1)', '4G (1)', '4G (2)', '4G (2)', 'Car to X', 'Car to X', 'LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'FM', 'FM', 'FM', 'DAB III', 'DAB III', 'DTTV', 'DTTV', 'DAB L band', 'DAB L band', 'SDARS', 'SDARS'],
                                     'F Start(MHz)': [30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 26.0, 26.0, 30.0, 30.0, 68.0, 68.0, 142.0, 142.0, 300.0, 300.0, 312.85, 313.85, 315.85, 316.85, 380.0, 380.0, 420.0, 420.0, 431.92, 432.92, 434.92, 435.92, 791.0, 791.0, 820.0, 820.0, 860.0, 860.0, 925.0, 925.0, 1477.0, 1477.0, 1553.0, 1553.0, 1560.098, 1560.098, 1562.098, 1562.098, 1567.0, 1567.0, 1574.42, 1574.42, 1576.42, 1576.42, 1591.0, 1591.0, 1598.0, 1598.0, 1606.0, 1606.0, 1803.0, 1803.0, 1850.0, 1850.0, 1900.0, 1900.0, 2010.0, 2010.0, 2108.0, 2108.0, 2400.0, 2400.0, 2620.0, 2620.0, 3400.0, 3400.0, 5850.0, 5850.0, 0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 76.0, 76.0, 76.0, 171.0, 171.0, 470.0, 470.0, 1447.0, 1447.0, 2320.0, 2320.0],
                                     'F Stop(MHz)': [75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 28.0, 28.0, 54.0, 54.0, 87.0, 87.0, 175.0, 175.0, 312.85, 330.0, 313.85, 315.85, 316.85, 330.0, 512.0, 512.0, 431.92, 450.0, 432.92, 434.92, 435.92, 450.0, 821.0, 821.0, 960.0, 960.0, 895.0, 895.0, 960.0, 960.0, 1501.0, 1501.0, 1560.098, 1560.098, 1562.098, 1562.098, 1569.0, 1569.0, 1574.42, 1574.42, 1576.42, 1576.42, 1583.0, 1583.0, 1598.0, 1598.0, 1606.0, 1606.0, 1613.0, 1613.0, 1882.0, 1882.0, 1990.0, 1990.0, 1992.0, 1992.0, 2025.0, 2025.0, 2172.0, 2172.0, 2500.0, 2500.0, 2690.0, 2690.0, 3800.0, 3800.0, 5925.0, 5925.0, 0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 108.0, 108.0, 108.0, 245.0, 245.0, 770.0, 770.0, 1494.0, 1494.0, 2345.0, 2345.0],
                                     'Level Start(dBµV/m)': [52, 62, 52, 42, 53, 63, 52, 32, 38, 58, 21, 41, 27, 47, 30, 44, 30, 18, 18, 30, 30, 50, 30, 44, 30, 18, 18, 30, 30, 50, 56, 36, 50, 30, 50, 30, 30, 50, 76, 56, 16, 36, 16, 36, 56, 76, 36, 16, 16, 36, 76, 76, 36, 16, 36, 16, 30, 50, 50, 30, 30, 50, 50, 30, 50, 30, 30, 50, 30, 50, 50, 30, 50, 30, 43, 36, 56, 43, 36, 56, 52, 32, 38, 18, 25, 22, 42, 57, 47, 24, 44, 50, 30],
                                     'Level Stop(dBµV/m)': [42, 52, 63, 53, 53, 63, 52, 32, 38, 58, 21, 41, 27, 47, 30, 44, 18, 18, 30, 30, 30, 50, 30, 44, 18, 18, 30, 30, 30, 50, 56, 36, 50, 30, 50, 30, 30, 50, 36, 16, 16, 36, 56, 76, 16, 36, 36, 16, 56, 76, 16, 36, 36, 16, 76, 76, 30, 50, 50, 30, 30, 50, 50, 30, 50, 30, 30, 50, 30, 50, 50, 30, 50, 30, 43, 36, 56, 43, 36, 56, 52, 32, 38, 18, 25, 22, 42, 57, 47, 24, 44, 50, 30],
                                     'Detector': ['Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'QPeak', 'Average', 'Peak', 'QPeak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'QPeak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average'],
                                     'RBW(kHz)': [120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000],
                                     'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                                     'MeasurementTime(ms)': [5, 5, 5, 5, 5, 5, 50, 50, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1000, 50, 50, 1000, 50, 50, 50, 50, 5, 5, 1000, 50, 50, 5, 5, 50, 50, 50, 50], 'FrequencyStep(kHz)': [50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 5.0, 5.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 50.0, 50.0, 0.05, 500.0, 500.0, 50.0, 50.0, 500.0, 500.0, 500.0, 500.0]}

PSA_B21_7110_MR01_Short_Noise_V4 = {'GroupName': ['2004-104', '2004-104', '2004-104', '2004-104', '2004-104', '2004-104', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Mobile Services', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion', 'Radiodiffusion'],
                                    'BandName': ['30-75', '30-75', '75-400', '75-400', '400-1000', '400-1000', 'CB', 'CB', 'VHF (1)', 'VHF (1)', 'VHF (2)', 'VHF (2)', 'VHF (3)', 'VHF (3)', 'JAPAN RKE', 'JAPAN RKE', 'JAPAN RKE', 'JAPAN RKE', 'JAPAN RKE', 'JAPAN RKE', 'analog UHF (1)', 'analog UHF (1)', 'RKE (General Case)', 'RKE (General Case)', 'RKE (General Case)', 'RKE (General Case)', 'RKE (General Case)', 'RKE (General Case)', '4G', '4G', 'analog UHF (2)', 'analog UHF (2)', 'GSM 800 and AMPS USA', 'GSM 800 and AMPS USA', 'EGSM/GSM 900 and PDC Japan', 'EGSM/GSM 900 and PDC Japan', 'PDC Japan', 'PDC Japan', 'COMPASS', 'COMPASS', 'COMPASS', 'COMPASS', 'COMPASS', 'COMPASS', 'GPS L1 Civil', 'GPS L1 Civil', 'GPS L1 Civil', 'GPS L1 Civil', 'GPS L1 Civil', 'GPS L1 Civil', 'GLONASS', 'GLONASS', 'GLONASS', 'GLONASS', 'GLONASS', 'GLONASS', 'GSM 1800 (PCN) and 4G', 'GSM 1800 (PCN) and 4G', 'GSM 1900', 'GSM 1900', '3G and PCS USA', '3G and PCS USA', '3G (1)', '3G (1)', '3G (2)', '3G (2)', 'Bluetooth / 802.11 / WiMAX / WLAM', 'Bluetooth / 802.11 / WiMAX / WLAM', '4G (2)', '4G (2)', '4G (3)', '4G (3)', 'Car To X', 'Car To X', 'LW', 'LW', 'LW', 'MW', 'MW', 'MW', 'SW', 'SW', 'FM', 'FM', 'FM', 'DAB III', 'DAB III', 'DTTV', 'DTTV', 'DAB L band', 'DAB L band', 'SDARS', 'SDARS'],
                                    'F Start(MHz)': [30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 26.0, 26.0, 30.0, 30.0, 68.0, 68.0, 142.0, 142.0, 300.0, 300.0, 312.85, 313.85, 315.85, 316.85, 380.0, 380.0, 420.0, 420.0, 431.92, 432.92, 434.92, 435.92, 791.0, 791.0, 820.0, 820.0, 860.0, 860.0, 925.0, 925.0, 1477.0, 1477.0, 1553.0, 1553.0, 1560.098, 1560.098, 1562.098, 1562.098, 1567.0, 1567.0, 1574.42, 1574.42, 1576.42, 1576.42, 1591.0, 1591.0, 1598.0, 1598.0, 1606.0, 1606.0, 1803.0, 1803.0, 1850.0, 1850.0, 1900.0, 1900.0, 2010.0, 2010.0, 2108.0, 2108.0, 2400.0, 2400.0, 2620.0, 2620.0, 3400.0, 3400.0, 5850.0, 5850.0, 0.15, 0.15, 0.15, 0.53, 0.53, 0.53, 5.9, 5.9, 76.0, 76.0, 76.0, 171.0, 171.0, 470.0, 470.0, 1447.0, 1447.0, 2320.0, 2320.0],
                                    'F Stop(MHz)': [75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 28.0, 28.0, 54.0, 54.0, 87.0, 87.0, 175.0, 175.0, 312.85, 330.0, 313.85, 315.85, 316.85, 330.0, 512.0, 512.0, 450.0, 431.92, 432.92, 434.92, 435.92, 450.0, 821.0, 821.0, 960.0, 960.0, 895.0, 895.0, 960.0, 960.0, 1501.0, 1501.0, 1560.098, 1560.098, 1562.098, 1562.098, 1569.0, 1569.0, 1574.42, 1574.42, 1576.42, 1576.42, 1583.0, 1583.0, 1598.0, 1598.0, 1606.0, 1606.0, 1613.0, 1613.0, 1882.0, 1882.0, 1990.0, 1990.0, 1992.0, 1992.0, 2025.0, 2025.0, 2172.0, 2172.0, 2500.0, 2500.0, 2690.0, 2690.0, 3800.0, 3800.0, 5925.0, 5925.0, 0.3, 0.3, 0.3, 1.8, 1.8, 1.8, 6.2, 6.2, 108.0, 108.0, 108.0, 245.0, 245.0, 770.0, 770.0, 1494.0, 1494.0, 2345.0, 2345.0],
                                    'Level Start(dBµV/m)': [62, 52, 42, 52, 63, 53, 58, 32, 64, 38, 47, 21, 53, 27, 30, 50, 30, 18, 18, 30, 56, 30, 50, 30, 30, 18, 18, 30, 30, 56, 62, 36, 56, 30, 30, 56, 56, 30, 82, 56, 42, 16, 42, 16, 56, 82, 16, 42, 42, 16, 82, 56, 42, 16, 42, 16, 30, 56, 30, 56, 30, 56, 30, 56, 30, 56, 56, 30, 56, 30, 56, 30, 56, 30, 49, 62, 36, 36, 49, 62, 32, 58, 44, 43, 18, 22, 48, 63, 47, 50, 24, 30, 56],
                                    'Level Stop(dBµV/m)': [52, 42, 53, 63, 63, 53, 58, 32, 64, 38, 47, 21, 53, 27, 30, 50, 18, 18, 30, 30, 56, 30, 50, 30, 18, 18, 30, 30, 30, 56, 62, 36, 56, 30, 30, 56, 56, 30, 42, 16, 42, 16, 82, 56, 16, 42, 16, 42, 82, 56, 42, 16, 42, 16, 82, 56, 30, 56, 30, 56, 30, 56, 30, 56, 30, 56, 56, 30, 56, 30, 56, 30, 56, 30, 49, 62, 36, 36, 49, 62, 32, 58, 44, 43, 18, 22, 48, 63, 47, 50, 24, 30, 56],
                                    'Detector': ['Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'QPeak', 'Peak', 'Average', 'Average', 'QPeak', 'Peak', 'Average', 'Peak', 'Peak', 'QPeak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak'],
                                    'RBW(kHz)': [120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000],
                                    'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                                    'MeasurementTime(ms)': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1000, 50, 50, 50, 1000, 50, 50, 50, 5, 1000, 5, 50, 50, 5, 5, 50, 50, 50, 50], 'FrequencyStep(kHz)': [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 5, 5, 5, 5, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 5, 5, 5, 5, 5, 5, 5, 5, 50, 50, 50, 500, 500, 50, 50, 500, 500, 500, 500]}

RE_ALSE_Non_Spark_Requirements_reduced = {'GroupName': ['30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Below 30M', 'Below 30M'],
                                          'BandName': ['M1', 'NA1a, NA1b', 'NA1a, NA1b', 'M2', 'JB1', 'JB1', 'G2', 'G2', 'NA2a, NA2b', 'NA2a, NA2b', 'G3', 'G3', 'G4a', 'G4a', 'G4a', 'M3', 'G4b', 'G4b', 'G4b', 'NA3a, NA3b', 'NA3a, NA3b', 'NA4', 'NA4', 'G5a', 'G5a', 'G5a', 'G5b', 'G5b', 'G5b', 'G5c', 'G5c', 'G5c', 'G5d', 'G6a', 'G6b', 'G7', 'G1', 'G1'],
                                          'F Start(MHz)': [30.0, 45.1, 45.1, 75.0, 75.2, 75.2, 86.6, 86.6, 148.8, 148.8, 172.4, 172.4, 310.0, 313.0, 317.0, 400.0, 429.0, 432.0, 436.0, 450.0, 450.0, 806.0, 806.0, 1168.45, 1175.45, 1177.45, 1552.052, 1559.052, 1563.144, 1567.42, 1574.42, 1576.42, 1598.0625, 2400.0, 5170.0, 5850.0, 0.53, 0.53],
                                          'F Stop(MHz)': [75.0, 47.9, 47.9, 400.0, 90.9, 90.9, 109.1, 109.1, 164.7, 164.7, 242.4, 242.4, 313.0, 317.0, 320.0, 1000.0, 432.0, 436.0, 439.0, 520.0, 520.0, 870.0, 870.0, 1175.45, 1177.45, 1184.45, 1559.052, 1563.144, 1570.144, 1574.42, 1576.42, 1583.42, 1605.375, 2490.0, 5250.0, 5925.0, 1.71, 1.71],
                                          'Level Start(dBµV/m)': [49, 17, 9, 39, 10, 2, 17, 9, 9, 17, 10, 2, 17, 7, 17, 50, 21, 11, 21, 9, 17, 17, 9, 41, 1, 1, 41, 1, 1, 41, 1, 1, 17, 100, 100, 100, 14, 20],
                                          'Level Stop(dBµV/m)': [39, 17, 9, 50, 10, 2, 17, 9, 9, 17, 10, 2, 17, 7, 17, 50, 21, 11, 21, 9, 17, 17, 9, 1, 1, 41, 1, 1, 41, 1, 1, 41, 17, 100, 100, 100, 14, 20],
                                          'Detector': ['Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak'],
                                          'RBW(kHz)': [120, 9, 9, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 9, 9, 9, 9, 9, 9, 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 9, 9, 9, 9],
                                          'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                                          'MeasurementTime(ms)': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                                          'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

RE_ALSE_Non_Spark_Requirements = {'GroupName': ['30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Above 1G', 'Below 30M', 'Below 30M'],
                                  'BandName': ['M1', 'NA1a, NA1b', 'NA1a, NA1b', 'M2', 'JB1', 'JB1', 'G2', 'G2', 'NA2a, NA2b', 'NA2a, NA2b', 'G3', 'G3', 'G4a', 'G4a', 'G4a', 'M3', 'G4b', 'G4b', 'G4b', 'NA3a, NA3b', 'NA3a, NA3b', 'NA4', 'NA4', 'G5a', 'G5a', 'G5a', 'G5b', 'G5b', 'G5b', 'G5c', 'G5c', 'G5c', 'G5d', 'G6a', 'G6b', 'G7', 'G1', 'G1'],
                                  'F Start(MHz)': [30.0, 45.1, 45.1, 75.0, 75.2, 75.2, 86.6, 86.6, 148.8, 148.8, 172.4, 172.4, 310.0, 313.0, 317.0, 400.0, 429.0, 432.0, 436.0, 450.0, 450.0, 806.0, 806.0, 1168.45, 1175.45, 1177.45, 1552.052, 1559.052, 1563.144, 1567.42, 1574.42, 1576.42, 1598.0625, 2400.0, 5170.0, 5850.0, 0.53, 0.53],
                                  'F Stop(MHz)': [75.0, 47.9, 47.9, 400.0, 90.9, 90.9, 109.1, 109.1, 164.7, 164.7, 242.4, 242.4, 313.0, 317.0, 320.0, 1000.0, 432.0, 436.0, 439.0, 520.0, 520.0, 870.0, 870.0, 1175.45, 1177.45, 1184.45, 1559.052, 1563.144, 1570.144, 1574.42, 1576.42, 1583.42, 1605.375, 2490.0, 5250.0, 5925.0, 1.71, 1.71],
                                  'Level Start(dBµV/m)': [52, 12, 20, 42, 12, 20, 20, 12, 20, 12, 20, 12, 20, 10, 20, 53, 24, 14, 24, 12, 20, 20, 12, 44, 4, 4, 44, 4, 4, 44, 4, 4, 20, 100, 100, 100, 30, 24],
                                  'Level Stop(dBµV/m)': [42, 12, 20, 53, 12, 20, 20, 12, 20, 12, 20, 12, 20, 10, 20, 53, 24, 14, 24, 12, 20, 20, 12, 4, 4, 44, 4, 4, 44, 4, 4, 44, 20, 100, 100, 100, 30, 24],
                                  'Detector': ['Average', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average'],
                                  'RBW(kHz)': [120, 9, 9, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 9, 9, 9, 9, 9, 9, 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 9, 9, 9, 9],
                                  'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                                  'MeasurementTime(ms)': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                                  'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

RE_ALSE_Spark_Requirements = {'GroupName': ['30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', '30M-1G', 'below 30M'],
                              'BandName': ['M1', 'NA1a, NA1b', 'M2', 'JB1', 'G2', 'NA2a, NA2b', 'G3', 'G4a', 'M3', 'G4b', 'NA3a, NA3b', 'NA4', 'G1'],
                              'F Start(MHz)': [30.0, 45.1, 75.0, 75.2, 86.6, 148.8, 172.4, 310.0, 400.0, 429.0, 450.0, 806.0, 0.53],
                              'F Stop(MHz)': [75.0, 47.9, 400.0, 90.9, 109.1, 164.7, 242.4, 320.0, 1000.0, 439.0, 520.0, 870.0, 1.71],
                              'Level Start(dBµV/m)': [62, 24, 52, 24, 24, 24, 24, 30, 63, 30, 24, 24, 54],
                              'Level Stop(dBµV/m)': [52, 24, 63, 24, 24, 24, 24, 30, 63, 30, 24, 24, 54],
                              'Detector': ['QPeak', 'QPeak', 'QPeak', 'QPeak', 'QPeak', 'QPeak', 'QPeak', 'QPeak', 'QPeak', 'QPeak', 'QPeak', 'QPeak', 'QPeak'],
                              'RBW(kHz)': [120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 9],
                              'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                              'MeasurementTime(ms)': [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
                              'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

RNDS_C_00517_v1_1_AN = {'GroupName': ['Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'], 'BandName': ['LW', 'LW', 'MW', 'MW', 'SW 1', 'SW 1', 'SW 2', 'SW 2', 'FM', 'FM', 'CB', 'CB', 'VHF', 'VHF', 'VHF (4m)', 'VHF (4m)'],
                        'F Start(MHz)': [0.1, 0.1, 0.53, 0.53, 5.9, 5.9, 6.2, 6.2, 76.0, 76.0, 26.0, 26.0, 30.0, 30.0, 68.0, 68.0],
                        'F Stop(MHz)': [0.53, 0.53, 5.9, 5.9, 6.2, 6.2, 26.0, 26.0, 108.0, 108.0, 30.0, 30.0, 68.0, 68.0, 87.0, 87.0],
                        'Level Start(dBµV)': [70, 60, 50, 60, 39, 49, 60, 50, 28, 21, 36, 46, 52, 42, 24, 34],
                        'Level Stop(dBµV)': [70, 60, 50, 60, 39, 49, 60, 50, 28, 21, 36, 46, 52, 42, 24, 34],
                        'Detector': ['QPeak', 'Average', 'Average', 'QPeak', 'Average', 'QPeak', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'QPeak', 'QPeak', 'Average', 'Average', 'QPeak'],
                        'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 9, 9, 120, 120, 120, 120],
                        'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                        'MeasurementTime(ms)': [1000, 100, 100, 1000, 100, 1000, 1000, 100, 1000, 10, 100, 1000, 1000, 10, 10, 1000],
                        'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

RNDS_C_00517_v1_1_RE = {'GroupName': ['Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Analog Broadcast', 'Base limit', 'Base limit', 'Base limit', 'Base limit', 'Base limit', 'Base limit', 'Digital Broadcast', 'Digital Broadcast', 'Digital Broadcast', 'Digital Broadcast', 'Digital Broadcast', 'Digital Broadcast', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services', 'Mobile and other services'],
                        'BandName': ['LW', 'LW', 'AB2', 'AB2', 'MW', 'MW', 'AB4', 'AB4', 'KW', 'KW', 'AB6', 'AB6', 'FM', 'FM', 'B8', 'B8', 'B9', 'B9', 'B10', 'B10', 'DAB III', 'DAB III', 'TV Band IV', 'TV Band IV', 'SDARS', 'SDARS', 'CB', 'CB', 'VHF (4m)', 'VHF (4m)', 'VHF (2m)', 'VHF (2m)', 'RKE 1', 'RKE 1', 'TETRA 1', 'TETRA 1', 'TETRA 2', 'TETRA 2', 'RKE 2', 'RKE 2', 'TETRA POL', 'TETRA POL', 'LTE 1 (4G)', 'LTE 1 (4G)', 'GSM 850 (2G)', 'GSM 850 (2G)', 'GSM 900 (2G)', 'GSM 900 (2G)', 'GNSS', 'GSM 1800 (2G)', 'GSM 1800 (2G)', '3G', '3G', 'GSM 1900 (2G)', 'GSM 1900 (2G)', 'WIFI 802.11b & BT', 'WIFI 802.11b & BT', 'LTE 2 (4G)', 'LTE 2 (4G)', 'WIFI 802.11g/n', 'WIFI 802.11g/n', 'ITS', 'ITS'],
                        'F Start(MHz)': [0.1, 0.1, 0.3, 0.3, 0.52, 0.52, 2.0, 2.0, 5.8, 5.8, 6.2, 6.2, 76.0, 76.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 171.0, 171.0, 468.0, 468.0, 2320.0, 2320.0, 26.0, 26.0, 68.0, 68.0, 142.0, 142.0, 313.0, 313.0, 380.0, 380.0, 420.0, 420.0, 432.0, 432.0, 460.0, 460.0, 703.0, 703.0, 859.0, 859.0, 915.0, 915.0, 1558.0, 1805.0, 1805.0, 1900.0, 1900.0, 1930.0, 1930.0, 2400.0, 2400.0, 2496.0, 2496.0, 4915.0, 4915.0, 5875.0, 5875.0],
                        'F Stop(MHz)': [0.3, 0.3, 0.52, 0.52, 2.0, 2.0, 5.8, 5.8, 6.2, 6.2, 26.0, 26.0, 108.0, 108.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 245.0, 245.0, 895.0, 895.0, 2345.0, 2345.0, 30.0, 30.0, 87.0, 87.0, 175.0, 175.0, 317.0, 317.0, 400.0, 400.0, 430.0, 430.0, 436.0, 436.0, 470.0, 470.0, 821.0, 821.0, 895.0, 895.0, 960.0, 960.0, 1616.0, 1880.0, 1880.0, 2170.0, 2170.0, 1995.0, 1995.0, 2500.0, 2500.0, 2690.0, 2690.0, 5825.0, 5825.0, 5905.0, 5905.0],
                        'Level Start(dBµV/m)': [30, 63, 73, 40, 26, 54, 34, 62, 39, 28, 51, 34, 25, 12, 56, 46, 36, 46, 57, 47, 22, 32, 28, 43, 36, 46, 28, 45, 18, 25, 18, 25, 30, 23, 22, 40, 40, 22, 25, 18, 22, 40, 30, 40, 43, 30, 30, 43, 4, 30, 43, 46, 36, 43, 30, 36, 46, 50, 40, 46, 56, 46, 56],
                        'Level Stop(dBµV/m)': [30, 63, 73, 40, 26, 54, 34, 62, 39, 28, 51, 34, 25, 12, 46, 36, 47, 57, 57, 47, 22, 32, 28, 43, 36, 46, 28, 45, 18, 25, 18, 25, 30, 23, 22, 40, 40, 22, 25, 18, 22, 40, 30, 40, 43, 30, 30, 43, 4, 30, 43, 46, 36, 43, 30, 36, 46, 50, 40, 46, 56, 46, 56],
                        'Detector': ['Average', 'QPeak', 'QPeak', 'Average', 'Average', 'QPeak', 'Average', 'QPeak', 'QPeak', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'QPeak', 'QPeak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'QPeak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak'],
                        'RBW(kHz)': [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 1000, 1000, 120, 120, 120, 120, 9, 120, 120, 1000, 1000, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                        'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                        'MeasurementTime(ms)': [100, 1000, 1000, 100, 100, 1000, 100, 1000, 1000, 100, 1000, 100, 1000, 10, 1000, 10, 10, 1000, 1000, 10, 100, 100, 100, 100, 100, 100, 100, 1000, 10, 1000, 10, 1000, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 100, 100, 10, 10, 10, 10, 100, 10, 10, 100, 100, 10, 10, 100, 100, 100, 100, 100, 100, 100, 100],
                        'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2018_AN_class_3 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio broadcasting - digital', 'Radio broadcasting - digital'],
                            'BandName': ['B1', 'B1', 'B2', 'B2', 'B3', 'B3', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '11 - 4m/BOS', '11 - 4m/BOS', '1 - MW', '1 - MW', '2 - SW 49m', '2 - SW 49m', '3 - VHF', '3 - VHF', '6 - TV II', '6 - TV II'],
                            'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 0.52, 0.52, 5.8, 5.8, 76.0, 76.0, 99.0, 99.0],
                            'F Stop(MHz)': [0.52, 0.52, 30.0, 30.0, 108.0, 108.0, 0.15, 29.7, 29.7, 87.255, 87.255, 1.73, 1.73, 6.3, 6.3, 108.0, 108.0, 108.0, 108.0],
                            'Level Start(dBµV)': [107, 97, 75, 65, 55, 65, 93, 75, 55, 20, 43, 57, 50, 52, 45, 31, 24, 55, 40],
                            'Level Stop(dBµV)': [75, 65, 75, 65, 55, 65, 93, 75, 55, 20, 43, 57, 50, 52, 45, 31, 24, 55, 40],
                            'Detector': ['Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'QPeak', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'Peak', 'Average'],
                            'RBW(kHz)': [9, 9, 9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000],
                            'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 10000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2018_AN_class_4 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio broadcasting - digital', 'Radio broadcasting - digital'],
                            'BandName': ['B1', 'B1', 'B2', 'B2', 'B3', 'B3', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '11 - 4m/BOS', '11 - 4m/BOS', '1 - MW', '1 - MW', '2 - SW 49m', '2 - SW 49m', '3 - VHF', '3 - VHF', '6 - TV II', '6 - TV II'],
                            'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 0.52, 0.52, 5.8, 5.8, 76.0, 76.0, 99.0, 99.0],
                            'F Stop(MHz)': [0.52, 0.52, 30.0, 30.0, 108.0, 108.0, 0.15, 29.7, 29.7, 87.255, 87.255, 1.73, 1.73, 6.3, 6.3, 108.0, 108.0, 108.0, 108.0],
                            'Level Start(dBµV)': [97, 107, 65, 75, 65, 55, 83, 69, 49, 14, 37, 49, 42, 46, 39, 25, 18, 49, 34],
                            'Level Stop(dBµV)': [65, 75, 65, 75, 65, 55, 83, 69, 49, 14, 37, 49, 42, 46, 39, 25, 18, 49, 34],
                            'Detector': ['Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'QPeak', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'Peak', 'Average'],
                            'RBW(kHz)': [9, 9, 9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000],
                            'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 10000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2018_AN_class_5 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio broadcasting - digital', 'Radio broadcasting - digital'],
                            'BandName': ['B1', 'B1', 'B2', 'B2', 'B3', 'B3', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '11 - 4m/BOS', '11 - 4m/BOS', '1 - MW', '1 - MW', '2 - SW 49m', '2 - SW 49m', '3 - VHF', '3 - VHF', '6 - TV II', '6 - TV II'],
                            'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 0.52, 0.52, 5.8, 5.8, 76.0, 76.0, 99.0, 99.0],
                            'F Stop(MHz)': [0.52, 0.52, 30.0, 30.0, 108.0, 108.0, 0.15, 29.7, 29.7, 87.255, 87.255, 1.73, 1.73, 6.3, 6.3, 108.0, 108.0, 108.0, 108.0],
                            'Level Start(dBµV)': [107, 97, 65, 75, 55, 65, 73, 63, 43, 31, 8, 34, 41, 33, 40, 19, 12, 28, 43],
                            'Level Stop(dBµV)': [75, 65, 65, 75, 55, 65, 73, 63, 43, 31, 8, 34, 41, 33, 40, 19, 12, 28, 43],
                            'Detector': ['Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'QPeak', 'Average', 'QPeak', 'QPeak', 'Average', 'Average', 'Peak'],
                            'RBW(kHz)': [9, 9, 9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000],
                            'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 10000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2018_RE_class_3 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B4', 'B5', 'B6', 'B7', 'B8', 'B8', 'B9', 'B9', 'B10', 'B10', 'B11', 'B11', 'B12', 'B12', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '11 - 4m/BOS', '11 - 4m/BOS', '12 - 2m/Taxi', '12 - 2m/Taxi', '13 - 2m/BOS', '13 - 2m/BOS', '14 - 2m/BOS', '14 - 2m/BOS', '15 - SRD', '15 - SRD', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - Trunked Radio', '19 - Trunked Radio', '20 - SRD', '20 - SRD', '21 - Trunked Radio', '21 - Trunked Radio', '22 - 2G, 3G, 4G, 5G', '22 - 2G, 3G, 4G, 5G', '23 - SRD', '23 - SRD', '25 - 3G, 4G, 5G', '25 - 3G, 4G, 5G', '26 - Beidou', '26 - Beidou', '26 - Beidou', '26 - GPS Galileo', '26 - GPS Galileo', '26 - GPS Galileo', '26 - GLONASS', '26 - GLONASS', '26 - GLONASS', '27 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '28 - 5G', '28 - 5G', '29 - WLAN, DSRC', '29 - WLAN, DSRC', '1 - MW', '1 - MW', '2- SW 49m', '2- SW 49m', '3 - VHF', '3 - VHF', '6 - TV II', '6 - TV II', '7 - TV III', '7 - TV III', '4 - DAB', '4 - DAB', '8 - TV IV/V', '8 - TV IV/V', '5 - SDARS', '5 - SDARS'],
                            'F Start(MHz)': [0.009, 0.15, 5.35, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 1350.0, 1350.0, 1552.098, 1559.098, 1563.098, 1567.42, 1574.42, 1576.42, 1590.781, 1597.781, 1609.594, 1695.0, 1695.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 5.8, 5.8, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0, 2320.0, 2320.0], 'F Stop(MHz)': [0.15, 5.35, 20.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 6000.0, 6000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1518.0, 1518.0, 1559.098, 1563.098, 1570.098, 1574.42, 1576.42, 1583.42, 1597.781, 1609.594, 1616.594, 2900.0, 2900.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 6.3, 6.3, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0, 2345.0, 2345.0],
                            'Level Start(dBµV/m)': [86, 62, 62, 39, 62, 52, 42, 52, 63, 53, 80, 60, 84, 104, 61, 40, 60, 37, 14, 37, 14, 37, 14, 14, 37, 26, 46, 31, 51, 31, 51, 51, 31, 31, 51, 26, 46, 51, 25, 67, 47, 52, 32, 66, 46, 72, 32, 32, 72, 32, 32, 72, 32, 32, 69, 49, 57, 77, 80, 60, 41, 34, 37, 30, 24, 31, 34, 49, 34, 49, 44, 34, 32, 52, 68, 58],
                            'Level Stop(dBµV/m)': [62, 62, 39, 39, 52, 42, 53, 63, 63, 53, 80, 60, 84, 104, 61, 40, 60, 37, 14, 37, 14, 37, 14, 14, 37, 26, 46, 31, 51, 31, 51, 51, 31, 31, 51, 26, 46, 51, 25, 67, 47, 52, 32, 66, 46, 32, 32, 72, 32, 32, 72, 32, 32, 72, 74, 54, 57, 77, 80, 60, 41, 34, 37, 30, 24, 31, 34, 49, 34, 49, 44, 34, 37, 57, 68, 58],
                            'Detector': ['Peak', 'Peak', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'QPeak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average'],
                            'RBW(kHz)': [0.2, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 9.0, 9.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0],
                            'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000], 'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2018_RE_class_4 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B4', 'B5', 'B6', 'B7', 'B8', 'B8', 'B9', 'B9', 'B10', 'B10', 'B11', 'B11', 'B12', 'B12', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '11 - 4m/BOS', '11 - 4m/BOS', '12 - 2m/Taxi', '12 - 2m/Taxi', '13 - 2m/BOS', '13 - 2m/BOS', '14 - 2m/BOS', '14 - 2m/BOS', '15 - SRD', '15 - SRD', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - Trunked Radio', '19 - Trunked Radio', '20 - SRD', '20 - SRD', '21 - Trunked Radio', '21 - Trunked Radio', '22 - 2G, 3G, 4G, 5G', '22 - 2G, 3G, 4G, 5G', '23 - SRD', '23 - SRD', '25 - 3G, 4G, 5G', '25 - 3G, 4G, 5G', '26 - Beidou', '26 - Beidou', '26 - Beidou', '26 - GPS Galileo', '26 - GPS Galileo', '26 - GPS Galileo', '26 - GLONASS', '26 - GLONASS', '26 - GLONASS', '27 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '28 - 5G', '28 - 5G', '29 - WLAN, DSRC', '29 - WLAN, DSRC', '1 - MW', '1 - MW', '2- SW 49m', '2- SW 49m', '3 - VHF', '3 - VHF', '6 - TV II', '6 - TV II', '7 - TV III', '7 - TV III', '4 - DAB', '4 - DAB', '8 - TV IV/V', '8 - TV IV/V', '5 - SDARS', '5 - SDARS'],
                            'F Start(MHz)': [0.009, 0.15, 5.35, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 1350.0, 1350.0, 1552.098, 1559.098, 1563.098, 1567.42, 1574.42, 1576.42, 1590.781, 1597.781, 1609.594, 1695.0, 1695.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 5.8, 5.8, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0, 2320.0, 2320.0],
                            'F Stop(MHz)': [0.15, 5.35, 20.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 6000.0, 6000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1518.0, 1518.0, 1559.098, 1563.098, 1570.098, 1574.42, 1576.42, 1583.42, 1597.781, 1609.594, 1616.594, 2900.0, 2900.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 6.3, 6.3, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0, 2345.0, 2345.0],
                            'Level Start(dBµV/m)': [86, 62, 62, 39, 52, 62, 52, 42, 63, 53, 80, 60, 104, 84, 51, 34, 54, 31, 8, 8, 31, 8, 31, 31, 8, 20, 40, 45, 25, 25, 45, 25, 45, 25, 45, 40, 20, 25, 45, 61, 41, 46, 26, 60, 40, 66, 26, 26, 66, 26, 26, 66, 26, 26, 43, 63, 51, 71, 74, 54, 26, 33, 24, 31, 18, 25, 43, 28, 28, 43, 38, 28, 46, 26, 62, 52], 'Level Stop(dBµV/m)': [62, 62, 39, 39, 42, 52, 63, 53, 63, 53, 80, 60, 104, 84, 51, 34, 54, 31, 8, 8, 31, 8, 31, 31, 8, 20, 40, 45, 25, 25, 45, 25, 45, 25, 45, 40, 20, 25, 45, 61, 41, 46, 26, 60, 40, 26, 26, 66, 26, 26, 66, 26, 26, 66, 48, 68, 51, 71, 74, 54, 26, 33, 24, 31, 18, 25, 43, 28, 28, 43, 38, 28, 51, 31, 62, 52],
                            'Detector': ['Peak', 'Peak', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'QPeak', 'Average', 'QPeak', 'Average', 'QPeak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average'],
                            'RBW(kHz)': [0.2, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 9.0, 9.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0],
                            'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2018_RE_class_5 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B4', 'B5', 'B6', 'B7', 'B8', 'B8', 'B9', 'B9', 'B10', 'B10', 'B11', 'B11', 'B12', 'B12', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '11 - 4m/BOS', '11 - 4m/BOS', '12 - 2m/Taxi', '12 - 2m/Taxi', '13 - 2m/BOS', '13 - 2m/BOS', '14 - 2m/BOS', '14 - 2m/BOS', '15 - SRD', '15 - SRD', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - Trunked Radio', '19 - Trunked Radio', '20 - SRD', '20 - SRD', '21 - Trunked Radio', '21 - Trunked Radio', '22 - 2G, 3G, 4G, 5G', '22 - 2G, 3G, 4G, 5G', '23 - SRD', '23 - SRD', '25 - 3G, 4G, 5G', '25 - 3G, 4G, 5G', '26 - Beidou', '26 - Beidou', '26 - Beidou', '26 - GPS Galileo', '26 - GPS Galileo', '26 - GPS Galileo', '26 - GLONASS', '26 - GLONASS', '26 - GLONASS', '27 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '28 - 5G', '28 - 5G', '29 - WLAN, DSRC', '29 - WLAN, DSRC', '1 - MW', '1 - MW', '2- SW 49m', '2- SW 49m', '3 - VHF', '3 - VHF', '6 - TV II', '6 - TV II', '7 - TV III', '7 - TV III', '4 - DAB', '4 - DAB', '8 - TV IV/V', '8 - TV IV/V', '5 - SDARS', '5 - SDARS'],
                            'F Start(MHz)': [0.009, 0.15, 5.35, 20.0, 30.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 1350.0, 1350.0, 1552.098, 1559.098, 1563.098, 1567.42, 1574.42, 1576.42, 1590.781, 1597.781, 1609.594, 1695.0, 1695.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 5.8, 5.8, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0, 2320.0, 2320.0], 'F Stop(MHz)': [0.15, 5.35, 20.0, 30.0, 75.0, 75.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 6000.0, 6000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1518.0, 1518.0, 1559.098, 1563.098, 1570.098, 1574.42, 1576.42, 1583.42, 1597.781, 1609.594, 1616.594, 2900.0, 2900.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 6.3, 6.3, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0, 2345.0, 2345.0],
                            'Level Start(dBµV/m)': [86, 62, 62, 39, 62, 52, 42, 52, 63, 53, 60, 80, 104, 84, 41, 48, 28, 2, 25, 25, 2, 25, 2, 2, 25, 14, 34, 19, 39, 19, 39, 19, 39, 39, 19, 34, 14, 19, 39, 55, 35, 40, 20, 34, 54, 60, 20, 20, 60, 20, 20, 60, 20, 20, 57, 37, 45, 65, 48, 68, 18, 25, 25, 18, 19, 12, 37, 22, 37, 22, 32, 22, 40, 20, 46, 56],
                            'Level Stop(dBµV/m)': [62, 62, 39, 39, 52, 42, 53, 63, 63, 53, 60, 80, 104, 84, 41, 48, 28, 2, 25, 25, 2, 25, 2, 2, 25, 14, 34, 19, 39, 19, 39, 19, 39, 39, 19, 34, 14, 19, 39, 55, 35, 40, 20, 34, 54, 20, 20, 60, 20, 20, 60, 20, 20, 60, 62, 42, 45, 65, 48, 68, 18, 25, 25, 18, 19, 12, 37, 22, 37, 22, 32, 22, 45, 25, 46, 56],
                            'Detector': ['Peak', 'Peak', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'QPeak', 'QPeak', 'Average', 'QPeak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak'],
                            'RBW(kHz)': [0.2, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 9.0, 9.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0],
                            'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2018_SL_class_3 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B21', 'B21', 'B22', 'B22', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '11 - 4m/BOS', '11 - 4m/BOS', '12 - 2m/Taxi', '12 - 2m/Taxi', '13 - 2m/BOS', '13 - 2m/BOS', '14 - 2m/BOS', '14 - 2m/BOS', '15 - SRD', '15 - SRD', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - Trunked Radio', '19 - Trunked Radio', '20 - SRD', '20 - SRD', '21 - Trunked Radio', '21 - Trunked Radio', '22 - 2G, 3G, 4G, 5G', '22 - 2G, 3G, 4G, 5G', '23 - SRD', '23 - SRD', '1 - MW', '1 - MW', ' 2 - SW 49m', ' 2 - SW 49m', '3 - VHF', '3 - VHF', '6 - TV II', '6 - TV II', '7 - TV III', '7 - TV III', '4 - DAB', '4 - DAB', '8 - TV IV/V', '8 - TV IV/V'],
                            'F Start(MHz)': [0.15, 0.15, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 0.52, 0.52, 5.8, 5.8, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0], 'F Stop(MHz)': [30.0, 30.0, 1000.0, 1000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1.73, 1.73, 6.3, 6.3, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0],
                            'Level Start(dBµV)': [61, 51, 71, 61, 64, 63, 43, 31, 8, 31, 8, 31, 8, 31, 8, 27, 7, 38, 18, 38, 18, 38, 18, 38, 18, 27, 7, 38, 18, 48, 28, 33, 13, 44, 37, 40, 33, 25, 18, 43, 28, 43, 28, 38, 28, 43, 28],
                            'Level Stop(dBµV)': [61, 51, 71, 61, 64, 63, 43, 31, 8, 31, 8, 31, 8, 31, 8, 27, 7, 38, 18, 38, 18, 38, 18, 38, 18, 27, 7, 38, 18, 48, 28, 33, 13, 44, 37, 40, 33, 25, 18, 43, 28, 43, 28, 38, 28, 43, 28],
                            'Detector': ['Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                            'RBW(kHz)': [9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                            'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2018_SL_class_4 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B21', 'B21', 'B22', 'B22', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '11 - 4m/BOS', '11 - 4m/BOS', '12 - 2m/Taxi', '12 - 2m/Taxi', '13 - 2m/BOS', '13 - 2m/BOS', '14 - 2m/BOS', '14 - 2m/BOS', '15 - SRD', '15 - SRD', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - Trunked Radio', '19 - Trunked Radio', '20 - SRD', '20 - SRD', '21 - Trunked Radio', '21 - Trunked Radio', '22 - 2G, 3G, 4G, 5G', '22 - 2G, 3G, 4G, 5G', '23 - SRD', '23 - SRD', '1 - MW', '1 - MW', ' 2 - SW 49m', ' 2 - SW 49m', '3 - VHF', '3 - VHF', '6 - TV II', '6 - TV II', '7 - TV III', '7 - TV III', '4 - DAB', '4 - DAB', '8 - TV IV/V', '8 - TV IV/V'],
                            'F Start(MHz)': [0.15, 0.15, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 0.52, 0.52, 5.8, 5.8, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0],
                            'F Stop(MHz)': [30.0, 30.0, 1000.0, 1000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1.73, 1.73, 6.3, 6.3, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0],
                            'Level Start(dBµV)': [61, 51, 71, 61, 54, 57, 37, 25, 2, 25, 2, 25, 2, 25, 2, 21, 1, 32, 12, 32, 12, 32, 12, 32, 12, 21, 1, 32, 12, 42, 22, 27, 7, 36, 29, 34, 27, 19, 12, 37, 22, 37, 22, 32, 22, 37, 22],
                            'Level Stop(dBµV)': [61, 51, 71, 61, 54, 57, 37, 25, 2, 25, 2, 25, 2, 25, 2, 21, 1, 32, 12, 32, 12, 32, 12, 32, 12, 21, 1, 32, 12, 42, 22, 27, 7, 36, 29, 34, 27, 19, 12, 37, 22, 37, 22, 32, 22, 37, 22],
                            'Detector': ['Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                            'RBW(kHz)': [9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                            'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2018_SL_class_5 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B21', 'B21', 'B22', 'B22', '9 - 125kHz', '10 - CB radio', '10 - CB radio', '11 - 4m/BOS', '11 - 4m/BOS', '12 - 2m/Taxi', '12 - 2m/Taxi', '13 - 2m/BOS', '13 - 2m/BOS', '14 - 2m/BOS', '14 - 2m/BOS', '15 - SRD', '15 - SRD', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - Trunked Radio', '19 - Trunked Radio', '20 - SRD', '20 - SRD', '21 - Trunked Radio', '21 - Trunked Radio', '22 - 2G, 3G, 4G, 5G', '22 - 2G, 3G, 4G, 5G', '23 - SRD', '23 - SRD', '1 - MW', '1 - MW', ' 2 - SW 49m', ' 2 - SW 49m', '3 - VHF', '3 - VHF', '6 - TV II', '6 - TV II', '7 - TV III', '7 - TV III', '4 - DAB', '4 - DAB', '8 - TV IV/V', '8 - TV IV/V'],
                            'F Start(MHz)': [0.15, 0.15, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 0.52, 0.52, 5.8, 5.8, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0],
                            'F Stop(MHz)': [30.0, 30.0, 1000.0, 1000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1.73, 1.73, 6.3, 6.3, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0],
                            'Level Start(dBµV)': [61, 51, 71, 61, 44, 51, 31, 19, -4, 19, -4, 19, -4, 19, -4, 15, -5, 26, 6, 26, 6, 26, 6, 26, 6, 15, -5, 26, 6, 36, 16, 21, 1, 28, 21, 28, 21, 13, 6, 31, 16, 31, 16, 26, 16, 31, 16],
                            'Level Stop(dBµV)': [61, 51, 71, 61, 44, 51, 31, 19, -4, 19, -4, 19, -4, 19, -4, 15, -5, 26, 6, 26, 6, 26, 6, 26, 6, 15, -5, 26, 6, 36, 16, 21, 1, 28, 21, 28, 21, 13, 6, 31, 16, 31, 16, 26, 16, 31, 16],
                            'Detector': ['Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                            'RBW(kHz)': [9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                            'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2021_AN_class_3 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio broadcasting - digital', 'Radio broadcasting - digital'],
                            'BandName': ['B1', 'B1', 'B2', 'B2', 'B3', 'B3', '4 - 125kHz', '5 - CB radio', '5 - CB radio', '6 - 4m/BOS', '6 - 4m/BOS', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '3 - TV II', '3 - TV II'],
                            'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0],
                            'F Stop(MHz)': [0.52, 0.52, 30.0, 30.0, 108.0, 108.0, 0.15, 29.7, 29.7, 87.255, 87.255, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0],
                            'Level Start(dBµV)': [97, 107, 65, 75, 55, 65, 93, 55, 75, 20, 43, 57, 50, 31, 24, 40, 55],
                            'Level Stop(dBµV)': [65, 75, 65, 75, 55, 65, 93, 55, 75, 20, 43, 57, 50, 31, 24, 40, 55],
                            'Detector': ['Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'Peak'],
                            'RBW(kHz)': [9, 9, 9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000],
                            'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2021_AN_class_4 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio broadcasting - digital', 'Radio broadcasting - digital'],
                            'BandName': ['B1', 'B1', 'B2', 'B2', 'B3', 'B3', '4 - 125kHz', '5 - CB radio', '5 - CB radio', '6 - 4m/BOS', '6 - 4m/BOS', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '3 - TV II', '3 - TV II'],
                            'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0],
                            'F Stop(MHz)': [0.52, 0.52, 30.0, 30.0, 108.0, 108.0, 0.15, 29.7, 29.7, 87.255, 87.255, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0],
                            'Level Start(dBµV)': [107, 97, 65, 75, 55, 65, 83, 69, 49, 14, 37, 49, 42, 18, 25, 49, 34],
                            'Level Stop(dBµV)': [75, 65, 65, 75, 55, 65, 83, 69, 49, 14, 37, 49, 42, 18, 25, 49, 34],
                            'Detector': ['Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'QPeak', 'Average', 'Average', 'QPeak', 'Peak', 'Average'],
                            'RBW(kHz)': [9, 9, 9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000],
                            'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 3000, 10000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2021_AN_class_5 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio broadcasting - digital', 'Radio broadcasting - digital'],
                            'BandName': ['B1', 'B1', 'B2', 'B2', 'B3', 'B3', '4 - 125kHz', '5 - CB radio', '5 - CB radio', '6 - 4m/BOS', '6 - 4m/BOS', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '3 - TV II', '3 - TV II'],
                            'F Start(MHz)': [0.15, 0.15, 0.52, 0.52, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0],
                            'F Stop(MHz)': [0.52, 0.52, 30.0, 30.0, 108.0, 108.0, 0.15, 29.7, 29.7, 87.255, 87.255, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0],
                            'Level Start(dBµV)': [107, 97, 65, 75, 55, 65, 73, 63, 43, 8, 31, 41, 34, 12, 19, 28, 43],
                            'Level Stop(dBµV)': [75, 65, 65, 75, 55, 65, 73, 63, 43, 8, 31, 41, 34, 12, 19, 28, 43],
                            'Detector': ['Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'QPeak', 'Average', 'Average', 'QPeak', 'Average', 'Peak'],
                            'RBW(kHz)': [9, 9, 9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 120, 120, 1000, 1000],
                            'Interpolation': ['LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 3000, 10000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2021_RE_class_3 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B4', 'B5', 'B6', 'B7', 'B8', 'B8', 'B8', 'B9', 'B9', 'B9', 'B10', 'B10', 'B10', 'B11', 'B11', 'B12', 'B12', '8 - 125kHz', '9 - CB radio', '9 - CB radio', '10 - 4m/BOS', '10 - 4m/BOS', '11 - 2m/Taxi', '11 - 2m/Taxi', '12 - 2m/BOS', '12 - 2m/BOS', '13 - 2m/BOS', '13 - 2m/BOS', '14 - SRD', '14 - SRD', '15 - Trunked Radio', '15 - Trunked Radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - SRD', '19 - SRD', '20 - Trunked Radio', '20 - Trunked Radio', '21 - 2G, 3G, 4G, 5G', '21 - 2G, 3G, 4G, 5G', '22 - SRD', '22 - SRD', '23 - GPS, Galileo I', '23 - GPS, Galileo I', '23 - GPS, Galileo I', '23 - Glonass I', '23 - GPS, Galileo II', '23 - Glonass I', '23 - Beidou I', '23 - Glonass I', '23 - Beidou I', '23 - GPS, Galileo II', '23 - GPS, Galileo II', '23 - Beidou I', '23 - GPS I', '23 - GPS I', '23 - GPS I', ' 24 - 3G, 4G, 5G', ' 24 - 3G, 4G, 5G', '25 - Beidou II', '25 - Galileo', '25 - Beidou II', '25 - GPS II', '25 - Beidou II', '25 - Galileo', '25 - GPS II', '25 - GPS II', '25 - Galileo', '25 - Beidou III', '25 - Beidou III', '25 - Beidou III', '25 - Glonass II', '25 - Glonass II', '25 - Glonass II', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 5G', '27 - 5G', '28 - WLAN, DSRC', '28 - WLAN, DSRC', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '5 - TV II', '5 - TV II', '6 - TV III', '6 - TV III', '3 - DAB', '3 - DAB', '7 - TV IV/V', '7 - TV IV/V', '4 - SDARS', '4 - SDARS'],
                            'F Start(MHz)': [0.009, 0.15, 5.35, 20.0, 30.0, 30.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 1164.0, 1175.45, 1177.45, 1188.0, 1195.0, 1197.0, 1198.14, 1205.0, 1205.14, 1206.14, 1208.14, 1209.14, 1217.0, 1226.6, 1228.6, 1350.0, 1350.0, 1552.098, 1559.0, 1559.098, 1563.0, 1563.098, 1574.42, 1574.42, 1576.42, 1576.42, 1580.742, 1587.742, 1591.742, 1593.0, 1597.625, 1606.375, 1695.0, 1695.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0, 2320.0, 2320.0],
                            'F Stop(MHz)': [0.15, 5.35, 20.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 1000.0, 3000.0, 3000.0, 6000.0, 6000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1175.45, 1177.45, 1188.0, 1197.0, 1206.14, 1205.0, 1205.14, 1214.0, 1209.14, 1208.14, 1219.0, 1216.14, 1226.6, 1228.6, 1237.0, 1518.0, 1518.0, 1559.098, 1574.42, 1563.098, 1574.42, 1570.098, 1576.42, 1576.42, 1587.0, 1591.0, 1587.742, 1591.742, 1598.742, 1597.625, 1606.375, 1610.0, 2900.0, 2900.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0, 2345.0, 2345.0],
                            'Level Start(dBµV/m)': [86, 62, 62, 39, 62, 42, 49, 52, 39, 32, 43, 50, 63, 60, 80, 84, 104, 61, 19, 39, 14, 37, 14, 37, 37, 14, 14, 37, 26, 46, 51, 31, 51, 31, 31, 51, 31, 51, 46, 26, 51, 25, 47, 67, 32, 52, 72, 32, 32, 72, 72, 32, 72, 32, 32, 32, 32, 32, 72, 32, 32, 66, 46, 72, 72, 32, 72, 32, 32, 32, 32, 32, 72, 32, 32, 72, 32, 32, 49, 69, 77, 57, 80, 60, 34, 41, 24, 31, 49, 34, 34, 49, 44, 34, 41, 56, 68, 58],
                            'Level Stop(dBµV/m)': [62, 62, 39, 39, 52, 32, 39, 63, 50, 43, 43, 50, 63, 60, 80, 84, 104, 61, 19, 39, 14, 37, 14, 37, 37, 14, 14, 37, 26, 46, 51, 31, 51, 31, 31, 51, 31, 51, 46, 26, 51, 25, 47, 67, 32, 52, 32, 32, 72, 32, 32, 32, 32, 72, 32, 32, 72, 72, 32, 32, 72, 66, 46, 32, 32, 32, 32, 72, 32, 32, 72, 72, 32, 32, 72, 32, 32, 72, 54, 74, 77, 57, 80, 60, 34, 41, 24, 31, 49, 34, 34, 49, 44, 34, 41, 56, 68, 58],
                            'Detector': ['Peak', 'Peak', 'Peak', 'Peak', 'Peak', 'Average', 'QPeak', 'Peak', 'QPeak', 'Average', 'Average', 'QPeak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'QPeak', 'Average', 'QPeak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average'],
                            'RBW(kHz)': [0.2, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0],
                            'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2021_RE_class_4 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B4', 'B5', 'B6', 'B7', 'B8', 'B8', 'B8', 'B9', 'B9', 'B9', 'B10', 'B10', 'B10', 'B11', 'B11', 'B12', 'B12', '8 - 125kHz', '9 - CB radio', '9 - CB radio', '10 - 4m/BOS', '10 - 4m/BOS', '11 - 2m/Taxi', '11 - 2m/Taxi', '12 - 2m/BOS', '12 - 2m/BOS', '13 - 2m/BOS', '13 - 2m/BOS', '14 - SRD', '14 - SRD', '15 - Trunked Radio', '15 - Trunked Radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - SRD', '19 - SRD', '20 - Trunked Radio', '20 - Trunked Radio', '21 - 2G, 3G, 4G, 5G', '21 - 2G, 3G, 4G, 5G', '22 - SRD', '22 - SRD', '23 - GPS, Galileo I', '23 - GPS, Galileo I', '23 - GPS, Galileo I', '23 - Glonass I', '23 - GPS, Galileo II', '23 - Glonass I', '23 - Beidou I', '23 - Glonass I', '23 - Beidou I', '23 - GPS, Galileo II', '23 - GPS, Galileo II', '23 - Beidou I', '23 - GPS I', '23 - GPS I', '23 - GPS I', '24 - 3G, 4G, 5G', '24 - 3G, 4G, 5G', '25 - Beidou II', '25 - Galileo', '25 - Beidou II', '25 - GPS II', '25 - Beidou II', '25 - Galileo', '25 - GPS II', '25 - Galileo', '25 - GPS II', '25 - Beidou III', '25 - Beidou III', '25 - Beidou III', '25 - Glonass II', '25 - Glonass II', '25 - Glonass II', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 5G', '27 - 5G', '28 - WLAN, DSRC', '28 - WLAN, DSRC', '1 - MW', '1 - MW', '3 - VHF', '3 - VHF', '5 - TV II', '5 - TV II', '6 - TV III', '6 - TV III', '3 - DAB', '3 - DAB', '7 - TV IV/V', '7 - TV IV/V', '4 - SDARS', '4 - SDARS'],
                            'F Start(MHz)': [0.009, 0.15, 5.35, 20.0, 30.0, 30.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 1164.0, 1175.45, 1177.45, 1188.0, 1195.0, 1197.0, 1198.14, 1205.0, 1205.14, 1206.14, 1208.14, 1209.14, 1217.0, 1226.6, 1228.6, 1350.0, 1350.0, 1552.098, 1559.0, 1559.098, 1563.0, 1563.098, 1574.42, 1574.42, 1576.42, 1576.42, 1580.742, 1587.742, 1591.742, 1593.0, 1597.625, 1606.375, 1695.0, 1695.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0, 2320.0, 2320.0],
                            'F Stop(MHz)': [0.15, 5.35, 20.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 1000.0, 3000.0, 3000.0, 6000.0, 6000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1175.45, 1177.45, 1188.0, 1197.0, 1206.14, 1205.0, 1205.14, 1214.0, 1209.14, 1208.14, 1219.0, 1216.14, 1226.6, 1228.6, 1237.0, 1518.0, 1518.0, 1559.098, 1574.42, 1563.098, 1574.42, 1570.098, 1576.42, 1576.42, 1591.0, 1587.0, 1587.742, 1591.742, 1598.742, 1597.625, 1606.375, 1610.0, 2900.0, 2900.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0, 2345.0, 2345.0],
                            'Level Start(dBµV/m)': [86, 62, 62, 39, 42, 62, 49, 39, 32, 52, 63, 50, 43, 60, 80, 104, 84, 51, 33, 13, 31, 8, 31, 8, 31, 8, 8, 31, 20, 40, 45, 25, 25, 45, 45, 25, 45, 25, 20, 40, 25, 45, 61, 41, 26, 46, 66, 26, 26, 66, 66, 26, 66, 26, 26, 26, 26, 26, 66, 26, 26, 60, 40, 66, 66, 26, 66, 26, 26, 26, 26, 26, 66, 26, 26, 66, 26, 26, 63, 43, 51, 71, 54, 74, 33, 26, 25, 18, 28, 43, 43, 28, 38, 28, 26, 46, 62, 52], 'Level Stop(dBµV/m)': [62, 62, 39, 39, 32, 52, 39, 50, 43, 63, 63, 50, 43, 60, 80, 104, 84, 51, 33, 13, 31, 8, 31, 8, 31, 8, 8, 31, 20, 40, 45, 25, 25, 45, 45, 25, 45, 25, 20, 40, 25, 45, 61, 41, 26, 46, 26, 26, 66, 26, 26, 26, 26, 66, 26, 26, 66, 66, 26, 26, 66, 60, 40, 26, 26, 26, 26, 66, 26, 26, 66, 66, 26, 26, 66, 26, 26, 66, 68, 48, 51, 71, 54, 74, 33, 26, 25, 18, 28, 43, 43, 28, 38, 28, 31, 51, 62, 52],
                            'Detector': ['Peak', 'Peak', 'Peak', 'Peak', 'Average', 'Peak', 'QPeak', 'QPeak', 'Average', 'Peak', 'Peak', 'QPeak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'QPeak', 'Average', 'QPeak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average'],
                            'RBW(kHz)': [0.2, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0],
                            'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 10000, 10000, 3000, 3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2021_RE_class_5 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B4', 'B5', 'B6', 'B7', 'B8', 'B8', 'B8', 'B9', 'B9', 'B9', 'B10', 'B10', 'B10', 'B11', 'B11', 'B12', 'B12', '8 - 125kHz', '9 - CB radio', '9 - CB radio', '10 - 4m/BOS', '10 - 4m/BOS', '11 - 2m/Taxi', '11 - 2m/Taxi', '12 - 2m/BOS', '12 - 2m/BOS', '13 - 2m/BOS', '13 - 2m/BOS', '14 - SRD', '14 - SRD', '15 - Trunked Radio', '15 - Trunked Radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - Trunked Radio', '18 - Trunked Radio', '19 - SRD', '19 - SRD', '20 - Trunked Radio', '20 - Trunked Radio', '21 - 2G, 3G, 4G, 5G', '21 - 2G, 3G, 4G, 5G', '22 - SRD', '22 - SRD', '23 - GPS, Galileo I', '23 - GPS, Galileo I', '23 - GPS, Galileo I', '23 - Glonass I', '23 - GPS, Galileo II', '23 - Glonass I', '23 - Beidou I', '23 - Glonass I', '23 - Beidou I', '23 - GPS, Galileo II', '23 - GPS, Galileo II', '23 - Beidou I', '23 - GPS I', '23 - GPS I', '23 - GPS I', '24 - 3G, 4G, 5G', '24 - 3G, 4G, 5G', '25 - Beidou II', '25 - Galileo', '25 - Beidou II', '25 - GPS II', '25 - Beidou II', '25 - GPS II', '25 - Galileo', '25 - Galileo', '25 - GPS II', '25 - Beidou III', '25 - Beidou III', '25 - Beidou III', '25 - Glonass II', '25 - Glonass II', '25 - Glonass II', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '26 - 2G, 3G, 4G, 5G, Bluetooth, WLAN', '27 - 5G', '27 - 5G', '28 - WLAN, DSRC', '28 - WLAN, DSRC', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '5 - TV II', '5 - TV II', '6 - TV III', '6 - TV III', '3 - DAB', '3 - DAB', '7 - TV IV/V', '7 - TV IV/V', '4 - SDARS', '4 - SDARS'],
                            'F Start(MHz)': [0.009, 0.15, 5.35, 20.0, 30.0, 30.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 3000.0, 3000.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 1164.0, 1175.45, 1177.45, 1188.0, 1195.0, 1197.0, 1198.14, 1205.0, 1205.14, 1206.14, 1208.14, 1209.14, 1217.0, 1226.6, 1228.6, 1350.0, 1350.0, 1552.098, 1559.0, 1559.098, 1563.0, 1563.098, 1574.42, 1574.42, 1576.42, 1576.42, 1580.742, 1587.742, 1591.742, 1593.0, 1597.625, 1606.375, 1695.0, 1695.0, 3400.0, 3400.0, 5150.0, 5150.0, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0, 2320.0, 2320.0],
                            'F Stop(MHz)': [0.15, 5.35, 20.0, 30.0, 75.0, 75.0, 75.0, 400.0, 400.0, 400.0, 1000.0, 1000.0, 1000.0, 3000.0, 3000.0, 6000.0, 6000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1175.45, 1177.45, 1188.0, 1197.0, 1206.14, 1205.0, 1205.14, 1214.0, 1209.14, 1208.14, 1219.0, 1216.14, 1226.6, 1228.6, 1237.0, 1518.0, 1518.0, 1559.098, 1574.42, 1563.098, 1574.42, 1570.098, 1576.42, 1576.42, 1591.0, 1587.0, 1587.742, 1591.742, 1598.742, 1597.625, 1606.375, 1610.0, 2900.0, 2900.0, 3800.0, 3800.0, 5925.0, 5925.0, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0, 2345.0, 2345.0],
                            'Level Start(dBµV/m)': [86, 62, 62, 39, 62, 42, 49, 39, 52, 32, 63, 43, 50, 80, 60, 104, 84, 41, 7, 27, 25, 2, 2, 25, 25, 2, 25, 2, 34, 14, 39, 19, 39, 19, 39, 19, 39, 19, 14, 34, 19, 39, 55, 35, 20, 40, 60, 20, 20, 60, 60, 20, 60, 20, 20, 20, 20, 20, 60, 20, 20, 54, 34, 60, 60, 20, 60, 20, 20, 20, 20, 20, 60, 20, 20, 60, 20, 20, 37, 57, 65, 45, 48, 68, 25, 18, 12, 19, 37, 22, 37, 22, 32, 22, 20, 40, 56, 46],
                            'Level Stop(dBµV/m)': [62, 62, 39, 39, 52, 32, 39, 50, 63, 43, 63, 43, 50, 80, 60, 104, 84, 41, 7, 27, 25, 2, 2, 25, 25, 2, 25, 2, 34, 14, 39, 19, 39, 19, 39, 19, 39, 19, 14, 34, 19, 39, 55, 35, 20, 40, 20, 20, 60, 20, 20, 20, 20, 60, 20, 20, 60, 60, 20, 20, 60, 54, 34, 20, 20, 20, 20, 60, 20, 20, 60, 60, 20, 20, 60, 20, 20, 60, 42, 62, 65, 45, 48, 68, 25, 18, 12, 19, 37, 22, 37, 22, 32, 22, 25, 45, 56, 46],
                            'Detector': ['Peak', 'Peak', 'Peak', 'Peak', 'Peak', 'Average', 'QPeak', 'QPeak', 'Peak', 'Average', 'Peak', 'Average', 'QPeak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Average', 'Peak', 'Peak', 'Average', 'Average', 'Peak', 'QPeak', 'Average', 'Average', 'QPeak', 'Peak', 'Average', 'Peak', 'Average', 'Peak', 'Average', 'Average', 'Peak', 'Peak', 'Average'],
                            'RBW(kHz)': [0.2, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 120.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 9.0, 9.0, 120.0, 120.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0],
                            'Interpolation': ['LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLOG', 'LOGLOG', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 10000, 10000, 3000, 3000, 3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2021_SL_class_3 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B21', 'B21', 'B22', 'B22', '7 - 125kHz', '8 - CB radio', '8 - CB radio', '9 - 4m/BOS', '9 - 4m/BOS', '10 - 2m/Taxi', '10 - 2m/Taxi', '11 - 2m/BOS', '11 - 2m/BOS', '12 - 2m/BOS', '12 - 2m/BOS', '13 - SRD', '13 - SRD', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - SRD', '18 - SRD', '19 - Trunked Radio', '19 - Trunked Radio', '20 - 2G, 3G, 4G, 5G', '20 - 2G, 3G, 4G, 5G', '21 - SRD', '21 - SRD', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '4- TV II', '4- TV II', '5 - TV III', '5 - TV III', '3 - DAB', '3 - DAB', '6 - TV IV/V', '6 - TV IV/V'],
                            'F Start(MHz)': [0.15, 0.15, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0],
                            'F Stop(MHz)': [30.0, 30.0, 1000.0, 1000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0],
                            'Level Start(dBµV)': [61, 51, 71, 61, 64, 63, 43, 31, 8, 31, 8, 31, 8, 31, 8, 27, 7, 38, 18, 38, 18, 38, 18, 38, 18, 27, 7, 38, 18, 48, 28, 33, 13, 44, 37, 25, 18, 43, 28, 43, 28, 38, 28, 43, 28], 'Level Stop(dBµV)': [61, 51, 71, 61, 64, 63, 43, 31, 8, 31, 8, 31, 8, 31, 8, 27, 7, 38, 18, 38, 18, 38, 18, 38, 18, 27, 7, 38, 18, 48, 28, 33, 13, 44, 37, 25, 18, 43, 28, 43, 28, 38, 28, 43, 28],
                            'Detector': ['Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg'],
                            'RBW(kHz)': [9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 9, 9, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                            'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2021_SL_class_4 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B21', 'B21', 'B22', 'B22', '7 - 125kHz', '8 - CB radio', '8 - CB radio', '9 - 4m/BOS', '9 - 4m/BOS', '10 - 2m/Taxi', '10 - 2m/Taxi', '11 - 2m/BOS', '11 - 2m/BOS', '12 - 2m/BOS', '12 - 2m/BOS', '13 - SRD', '13 - SRD', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - SRD', '18 - SRD', '19 - Trunked Radio', '19 - Trunked Radio', '20 - 2G, 3G, 4G, 5G', '20 - 2G, 3G, 4G, 5G', '21 - SRD', '21 - SRD', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '4 - TV II', '4 - TV II', '5 - TV III', '5 - TV III', '3 - DAB', '3 - DAB', '6 - TV IV/V', '6 - TV IV/V'],
                            'F Start(MHz)': [0.15, 0.15, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0],
                            'F Stop(MHz)': [30.0, 30.0, 1000.0, 1000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0],
                            'Level Start(dBµV)': [61, 51, 61, 71, 54, 57, 37, 2, 25, 2, 25, 2, 25, 2, 25, 1, 21, 12, 32, 12, 32, 12, 32, 32, 12, 21, 1, 12, 32, 22, 42, 7, 27, 29, 36, 12, 19, 37, 22, 22, 37, 22, 32, 37, 22],
                            'Level Stop(dBµV)': [61, 51, 61, 71, 54, 57, 37, 2, 25, 2, 25, 2, 25, 2, 25, 1, 21, 12, 32, 12, 32, 12, 32, 32, 12, 21, 1, 12, 32, 22, 42, 7, 27, 29, 36, 12, 19, 37, 22, 22, 37, 22, 32, 37, 22],
                            'Detector': ['Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg'],
                            'RBW(kHz)': [9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 9, 9, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                            'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}

TL_81000_2021_SL_class_5 = {'GroupName': ['Base Limits', 'Base Limits', 'Base Limits', 'Base Limits', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Mobile and Others Services', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio Broadcasting', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital', 'Radio BroadCasting - Digital'],
                            'BandName': ['B21', 'B21', 'B22', 'B22', '7 - 125kHz', '8 - CB radio', '8 - CB radio', '9 - 4m/BOS', '9 - 4m/BOS', '10 - 2m/Taxi', '10 - 2m/Taxi', '11 - 2m/BOS', '11 - 2m/BOS', '12 - 2m/BOS', '12 - 2m/BOS', '13 - SRD', '13 - SRD', '14 - Trunked Radio', '14 - Trunked Radio', '15 - Trunked Radio', '15 - Trunked Radio', '16 - Trunked Radio', '16 - Trunked Radio', '17 - Trunked Radio', '17 - Trunked Radio', '18 - SRD', '18 - SRD', '19 - Trunked Radio', '19 - Trunked Radio', '20 - 2G, 3G, 4G, 5G', '20 - 2G, 3G, 4G, 5G', '21 - SRD', '21 - SRD', '1 - MW', '1 - MW', '2 - VHF', '2 - VHF', '4 - TV II', '4 - TV II', '5 - TV III', '5 - TV III', '3 - DAB', '3 - DAB', '6 - TV IV/V', '6 - TV IV/V'],
                            'F Start(MHz)': [0.15, 0.15, 30.0, 30.0, 0.1, 26.5, 26.5, 84.015, 84.015, 146.0, 146.0, 167.56, 167.56, 172.16, 172.16, 313.0, 313.0, 380.0, 380.0, 390.0, 390.0, 406.0, 406.0, 420.0, 420.0, 433.0, 433.0, 460.0, 460.0, 555.0, 555.0, 863.0, 863.0, 0.52, 0.52, 76.0, 76.0, 99.0, 99.0, 170.0, 170.0, 174.0, 174.0, 470.0, 470.0],
                            'F Stop(MHz)': [30.0, 30.0, 1000.0, 1000.0, 0.15, 29.7, 29.7, 87.255, 87.255, 164.0, 164.0, 169.38, 169.38, 173.98, 173.98, 317.0, 317.0, 385.0, 385.0, 400.0, 400.0, 410.0, 410.0, 430.0, 430.0, 435.0, 435.0, 470.0, 470.0, 960.0, 960.0, 870.0, 870.0, 1.73, 1.73, 108.0, 108.0, 108.0, 108.0, 230.0, 230.0, 241.0, 241.0, 806.0, 806.0],
                            'Level Start(dBµV)': [61, 51, 71, 61, 44, 31, 51, -4, 19, 19, -4, -4, 19, -4, 19, -5, 15, 6, 26, 26, 6, 26, 6, 26, 6, 15, -5, 6, 26, 36, 16, 21, 1, 21, 28, 6, 13, 31, 16, 16, 31, 16, 26, 16, 31],
                            'Level Stop(dBµV)': [61, 51, 71, 61, 44, 31, 51, -4, 19, 19, -4, -4, 19, -4, 19, -5, 15, 6, 26, 26, 6, 26, 6, 26, 6, 15, -5, 6, 26, 36, 16, 21, 1, 21, 28, 6, 13, 31, 16, 16, 31, 16, 26, 16, 31],
                            'Detector': ['Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'QPeak', 'CISPR_Avg', 'QPeak', 'Peak', 'CISPR_Avg', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak', 'CISPR_Avg', 'Peak'],
                            'RBW(kHz)': [9, 9, 120, 120, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 120, 120, 120, 120, 120, 120, 120, 120, 9, 9, 120, 120, 1000, 1000, 9, 9, 9, 9, 120, 120, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                            'Interpolation': ['LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN', 'LOGLIN'],
                            'MeasurementTime(ms)': [3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 10000, 3000, 10000, 3000, 3000, 3000, 3000, 3000, 3000, 3000, 3000],
                            'FrequencyStep(kHz)': [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']}


Limit_database = {'CE AN Non-Spark Requirements (reduced)': CE_AN_Non_Spark_Requirements_reduced, 'CE AN Non-Spark Requirements': CE_AN_Non_Spark_Requirements, 'CE AN Spark Requirements': CE_AN_Spark_Requirements, 'CISPR 25 (2016) 4.0 AN - class 1': CISPR_25_4_AN_class_1, 'CISPR 25 (2016) 4.0 AN - class 2': CISPR_25_4_AN_class_2, 'CISPR 25 (2016) 4.0 AN - class 3': CISPR_25_4_AN_class_3, 'CISPR 25 (2016) 4.0 AN - class 4': CISPR_25_4_AN_class_4, 'CISPR 25 (2016) 4.0 AN - class 5': CISPR_25_4_AN_class_5, 'CISPR 25 (2016) 4.0 RE - class 5': CISPR_25_4_RE_class_5, 'CISPR 25 (2021-12) 5.0 AN - class 1': CISPR_25_5_AN_class_1, 'CISPR 25 (2021-12) 5.0 AN - class 2': CISPR_25_5_AN_class_2, 'CISPR 25 (2021-12) 5.0 AN - class 3': CISPR_25_5_AN_class_3, 'CISPR 25 (2021-12) 5.0 AN - class 4': CISPR_25_5_AN_class_4, 'CISPR 25 (2021-12) 5.0: AN - class 5': CISPR_25_5_AN_class_5, 'CISPR 25 (2021-12) 5.0 RE - class 1': CISPR_25_5_RE_class_1, 'CISPR 25 (2021-12) 5.0 RE - class 2': CISPR_25_5_RE_class_2, 'CISPR 25 (2021-12) 5.0 RE - class 3': CISPR_25_5_RE_class_3, 'CISPR 25 (2021-12) 5.0 RE - class 4': CISPR_25_5_RE_class_4, 'CISPR 25 (2021-12) 5.0: RE - class 5': CISPR_25_5_RE_class_5, 'FMC1278 (2021-10) CE420 - HV': FMC1278_CE420_HV, 'FMC1278 (2021-10) CE420 - LV': FMC1278_CE420_LV, 'FMC1278 (2021-10) RE310': FMC1278_RE310, 'GMW3097_Table3_NonSpark': GMW3097_Table3_NonSpark, 'GS 95002 (2019-10) CV': GS_95002_CV, 'GS 95002-2 (2019-10) AN - class 3': GS_95002_2_AN_class_3, 'GS 95002-2 (2019-10) AN - class 4': GS_95002_2_AN_class_4, 'GS 95002-2 (2019-10) AN - class 5': GS_95002_2_AN_class_5, 'GS 95002-2 (2019-10) RE - class 4': GS_95002_2_RE_class_4, 'GS 95002-2 (2019-10) RE - class 5': GS_95002_2_RE_class_5, 'GS 95002-2 (2019-10) SL - class 3': GS_95002_2_SL_class_3, 'GS 95002-2 (2019-10) SL - class 4': GS_95002_2_SL_class_4, 'GS 95002-2 (2019-10) SL - class 5': GS_95002_2_SL_class_5, 'GS 95002-2 (2021-05) AN-Test - Class 3': GS_95002_2_AN_Test_Class_3, 'GS 95002-2 (2021-05) AN-Test - Class 4': GS_95002_2_AN_Test_Class_4, 'GS 95002-2 (2021-05) AN-Test - Class 5': GS_95002_2_AN_Test_Class_5, 'GS 95002-2 (2021-05) CV-Test': GS_95002_2_CV_Test, 'GS 95002-2 (2021-05) RE-Test - Class 3': GS_95002_2_RE_Test_Class_3, 'GS 95002-2 (2021-05) RE-Test - Class 4': GS_95002_2_RE_Test_Class_4, 'GS 95002-2 (2021-05) RE-Test - Class 5': GS_95002_2_RE_Test_Class_5, 'MBN 10284-2 2019-10 AN': MBN_10284_2_2019_10_AN, 'MBN 10284-2 2019-10 NFA': MBN_10284_2_2019_10_NFA, 'MBN 10284-2 2019-10 RE': MBN_10284_2_2019_10_RE, 'MPS GER-LAB EMC_V0.1 AN': MPS_GER_LAB_EMC_V01_AN, 'MPS GER-LAB EMC_V0.2 RE - class 5': MPS_GER_LAB_EMC_V02_RE_class_5, 'PSA B21 7110 MC03 Lacroix': PSA_B21_7110_MC03_Lacroix, 'PSA B21 7110 MR01 Permanent Noise': PSA_B21_7110_MR01_Permanent_Noise, 'PSA B21 7110 MR01 Short Noise V4': PSA_B21_7110_MR01_Short_Noise_V4, 'RE ALSE Non-Spark Requirements (reduced)': RE_ALSE_Non_Spark_Requirements_reduced, 'RE ALSE Non-Spark Requirements': RE_ALSE_Non_Spark_Requirements, 'RE ALSE Spark Requirements': RE_ALSE_Spark_Requirements, 'RNDS-C-00517 v1.1 AN': RNDS_C_00517_v1_1_AN, 'RNDS-C-00517 v1.1 RE': RNDS_C_00517_v1_1_RE, 'TL 81000 (2018-03) AN - class 3': TL_81000_2018_AN_class_3, 'TL 81000 (2018-03) AN - class 4': TL_81000_2018_AN_class_4, 'TL 81000 (2021-09): AN - class 5': TL_81000_AN_class_5, 'TL 81000 (2018-03) RE - class 3': TL_81000_2018_RE_class_3, 'TL 81000 (2018-03) RE - class 4': TL_81000_2018_RE_class_4, 'TL 81000 (2021-09): RE - class 5': TL_81000_2018_RE_class_5, 'TL 81000 (2018-03) SL - class 3': TL_81000_2018_SL_class_3, 'TL 81000 (2018-03) SL - class 4': TL_81000_2018_SL_class_4, 'TL 81000 (2021-09): SL - class 5': TL_81000_2018_SL_class_5, 'TL 81000 (2021-09) AN - class 3': TL_81000_2021_AN_class_3, 'TL 81000 (2021-09) AN - class 4': TL_81000_2021_AN_class_4, 'TL 81000 (2021-09) AN - class 5': TL_81000_2021_AN_class_5, 'TL 81000 (2021-09) RE - class 3': TL_81000_2021_RE_class_3, 'TL 81000 (2021-09) RE - class 4': TL_81000_2021_RE_class_4, 'TL 81000 (2021-09) RE - class 5': TL_81000_2021_RE_class_5, 'TL 81000 (2021-09) SL - class 3': TL_81000_2021_SL_class_3, 'TL 81000 (2021-09) SL - class 4': TL_81000_2021_SL_class_4, 'TL 81000 (2021-09) SL - class 5': TL_81000_2021_SL_class_5}

default_colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
name2color = {'Blue':'#1f77b4', 'Orange':'#ff7f0e', 'Green':'#2ca02c', 'Red':'#d62728', 'Purple':'#9467bd', 'Brown':'#8c564b', 'Pink':'#e377c2', 'Gray':'#7f7f7f', 'Light green':'#bcbd22','Light blue':'#17becf'}
detector2color = {'Peak':'#1f77b4', 'QPeak':'#d62728', 'AVG':'#2ca02c'}

detector_to_color_gradient = {
    'Peak': {'9 kHz': 'rgb(106,174,214)', '120 kHz': 'rgb(46,126,188)', '200 kHz': 'rgb(46,126,188)', '1 MHz': 'rgb(8,74,145)'},
    'QPeak': {'9 kHz': 'rgb(251,105,74)', '120 kHz': 'rgb(217,37,35)', '200 kHz': 'rgb(217,37,35)', '1 MHz': 'rgb(152,12,19)'},
    'AVG': {'9 kHz': 'rgb(115,196,118)', '120 kHz': 'rgb(47,151,78)', '200 kHz': 'rgb(47,151,78)', '1 MHz': 'rgb(0,100,40)'}
}

Gradient = {'Blue' : 'Blues', 'Orange' : 'Oranges', 'Green' : 'Greens', 'Red' : 'Reds', 'Purple' : 'Purples', 'Brown' : 'copper', 'Pink' : 'RdPu', 'Gray' : 'Grays', 'BuGn' : 'BuGn', 'GnBu' : 'GnBu'}

emission_h_layout = {'height': '600px',
               'hovermode': 'closest',
               'legend': {'bordercolor': 'gray',
                          'borderwidth': 0.5,
                          'orientation': 'h',
                          'x': 0.5,
                          'xanchor': 'center',
                          'y': -0.15},
               'margin': {'b': 50, 'l': 50, 'r': 30, 't': 25},
               'plot_bgcolor': 'white',
               'template': '...',
               'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Horizontal Polarization'},
               'xaxis': {'gridcolor': 'lightgrey',
                         'hoverformat': ('<b> {meta[0]}<br> Frequency (MHz):</b> {x:.2f} <b> <br> Level (dBµV/m):</b> {y:.2f}'),
                         'linecolor': 'black',
                         'mirror': True,
                         'range': [],
                         'showline': True,
                         'tickfont': {'size': 12, 'weight': 'bold'},
                         'ticks': 'outside',
                         'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Frequency (MHz)'},
                         'type': 'log'},
               'yaxis': {'gridcolor': 'lightgrey',
                         'linecolor': 'black',
                         'mirror': True,
                         'range': 'auto',
                         'showline': True,
                         'tickfont': {'size': 12, 'weight': 'bold'},
                         'ticks': 'outside',
                         'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Level (dBµV/m)'}}}

emission_conduction_ground_layout = {'height': '600px',
               'hovermode': 'closest',
               'legend': {'bordercolor': 'gray',
                          'borderwidth': 0.5,
                          'orientation': 'h',
                          'x': 0.5,
                          'xanchor': 'center',
                          'y': -0.15},
               'margin': {'b': 50, 'l': 50, 'r': 30, 't': 25},
               'plot_bgcolor': 'white',
               'template': '...',
               'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Ground Polarization'},
               'xaxis': {'gridcolor': 'lightgrey',
                         'hoverformat': ('<b> {meta[0]}<br> Frequency (MHz):</b> {x:.2f} <b> <br> Level (dBµV/m):</b> {y:.2f}'),
                         'linecolor': 'black',
                         'mirror': True,
                         'range': [],
                         'showline': True,
                         'tickfont': {'size': 12, 'weight': 'bold'},
                         'ticks': 'outside',
                         'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Frequency (MHz)'},
                         'type': 'log'},
               'yaxis': {'gridcolor': 'lightgrey',
                         'linecolor': 'black',
                         'mirror': True,
                         'range': 'auto',
                         'showline': True,
                         'tickfont': {'size': 12, 'weight': 'bold'},
                         'ticks': 'outside',
                         'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Level (dBµV/m)'}}}

emission_v_layout = {'height': '600px',
               'hovermode': 'closest',
               'legend': {'bordercolor': 'gray',
                          'borderwidth': 0.5,
                          'orientation': 'h',
                          'x': 0.5,
                          'xanchor': 'center',
                          'y': -0.15},
               'margin': {'b': 50, 'l': 50, 'r': 30, 't': 25},
               'plot_bgcolor': 'white',
               'template': '...',
               'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Vertical Polarization'},
               'xaxis': {'gridcolor': 'lightgrey',
                         'hoverformat': ('<b> {meta[0]}<br> Frequency (MHz):</b> {x:.2f} <b> <br> Level (dBµV/m):</b> {y:.2f}'),
                         'linecolor': 'black',
                         'mirror': True,
                         'range': [],
                         'showline': True,
                         'tickfont': {'size': 12, 'weight': 'bold'},
                         'ticks': 'outside',
                         'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Frequency (MHz)'},
                         'type': 'log'},
               'yaxis': {'gridcolor': 'lightgrey',
                         'linecolor': 'black',
                         'mirror': True,
                         'range': 'auto',
                         'showline': True,
                         'tickfont': {'size': 12, 'weight': 'bold'},
                         'ticks': 'outside',
                         'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Level (dBµV/m)'}},
                'shape': [],
                'annotations': [],
                }

emission_conduction_supply_layout = {'height': '600px',
               'hovermode': 'closest',
               'legend': {'bordercolor': 'gray',
                          'borderwidth': 0.5,
                          'orientation': 'h',
                          'x': 0.5,
                          'xanchor': 'center',
                          'y': -0.15},
               'margin': {'b': 50, 'l': 50, 'r': 30, 't': 25},
               'plot_bgcolor': 'white',
               'template': '...',
               'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Supply Polarization'},
               'xaxis': {'gridcolor': 'lightgrey',
                         'hoverformat': ('<b> {meta[0]}<br> Frequency (MHz):</b> {x:.2f} <b> <br> Level (dBµV/m):</b> {y:.2f}'),
                         'linecolor': 'black',
                         'mirror': True,
                         'range': [],
                         'showline': True,
                         'tickfont': {'size': 12, 'weight': 'bold'},
                         'ticks': 'outside',
                         'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Frequency (MHz)'},
                         'type': 'log'},
               'yaxis': {'gridcolor': 'lightgrey',
                         'linecolor': 'black',
                         'mirror': True,
                         'range': 'auto',
                         'showline': True,
                         'tickfont': {'size': 12, 'weight': 'bold'},
                         'ticks': 'outside',
                         'title': {'font': {'size': 16, 'weight': 'bold'}, 'text': 'Level (dBµV/m)'}},
                'shape': [],
                'annotations': [],
                }

sidebar_style = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "300px",
    "padding": "20px",
    "background-color": "#F4F6F7",  # Light gray background for the sidebar
    "color": "#34495E",  # Dark text color for readability
    "box-shadow": "0px 0px 10px rgba(0, 0, 0, 0.1)",  # Subtle shadow for depth
    "transform": "translateX(100%)",  # Hidden by default
    "transition": "transform 0.3s ease",
    "z-index": "1000",  # To make sure sidebar is on top
    # "overflow-y": "scroll",
    # "overflow-x": "fixed"
}

# Button styles
button_style = {
    "width": "100%",  # Make the button take full width of sidebar
    "padding": "15px",
    "margin-bottom": "10px",  # Space between buttons
    "background-color": "#1F3A68",  # MPS-style blue background
    "color": "#FFF",  # White text
    "border": "none",
    "cursor": "pointer",
    "font-size": "18px",
    "font-family": "Arial, sans-serif",  # Clean sans-serif font
    "border-radius": "5px",  # Rounded corners for the buttons
    "transition": "background-color 0.3s ease",  # Button hover effect
}

submenu_style = {
    "display": "none",  # Submenu hidden initially
    "padding": "10px",
    "background-color": "#E9EFF1",  # Light blue background for submenu
    "color": "#34495E",  # Dark text for submenu
    "transition": "transform 0.3s ease",
    "transform": "translateY(-100%)",  # Hidden by default, off-screen
}

submenu_active_style = {
    "display": "block",  # Show submenu
    "transform": "translateY(0)",  # Slide it down
}

# Content area style
content_style = {
    "margin-right": "0px",  # No margin initially, so sidebar slides over
    "padding": "20px",
    "background-color": "#FFFFFF",  # White background for main content
    "color": "#34495E",  # Dark text color for readability
}

columnDefs_suspectTable = [{"checkboxSelection": {'function': "params.data.disabled == 'False'"}, 'showDisabledCheckboxes': True, "headerCheckboxSelection": True, 'width': 50, 'pinned': 'left'},
    {"headerName":"Suspects: Test Name","field": "Test Name", 'width': 400, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Scan","field": "Scan", 'flex':1, "filter": "agNumberColumnFilter", "filterParams": {"filterOptions": ["Equals", "Does not equals", "Greater than", "Less than", "Between"], "debounceMs": 500}},
    {"headerName":"Band","field": "Band", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Polarization","field": "Polarization", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Frequency (MHz)","field": "Frequency", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Detector","field": "Detector", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Meas.Value (dBµV/m)","field": "MeasValue", 'flex':1, "filter": "agNumberColumnFilter", "filterParams": {"filterOptions": ["Equals", "Does not equals", "Greater than", "Less than", "Between"], "debounceMs": 500}},
    {"headerName":"Limit.Value (dBµV/m)","field": "LimitValue", 'flex':1, "filter": "agNumberColumnFilter", "filterParams": {"filterOptions": ["Equals", "Does not equals", "Greater than", "Less than", "Between"], "debounceMs": 500}},
    {"headerName":"Diff (dB)","field": "Diff", 'flex':1, "filter": "agNumberColumnFilter", "filterParams": {"filterOptions": ["Equals", "Does not equals", "Greater than", "Less than", "Between"], "debounceMs": 500}},
    {"headerName":"RBW","field": "RBW", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Conclusion","field": "Pass_Fail", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"field": "disabled", "hide": True}]

getRowStyle_suspect = {
    "styleConditions": [
        {
            "condition": "params.data.Pass_Fail == 'Pass'",
            "style": {"backgroundColor": "green", "color": "white", "font-weight":"bold"},
        },
        {
            "condition": "params.data.Pass_Fail == 'Fail'",
            "style": {"backgroundColor": "red", "color": "white", "font-weight":"bold"},
        },
{
            "condition": "params.data.Pass_Fail == 'Inconclusive'",
            "style": {"backgroundColor": "orange", "color": "white", "font-weight":"bold"},
        },
    ]
}

check = html.Img(src="https://cdn-icons-png.flaticon.com/512/5610/5610944.png",style={'height': '20px','width':'20px'})
cross = html.Img(src="https://cdn-icons-png.flaticon.com/512/10100/10100000.png",style={'height': '20px','width':'20px'})

logo=html.Img(src="https://community.element14.com/e14/assets/main/mfg-group-assets/monolithicpowersystemsLogo.png",style={'height': '50px','margin-right':'10px'})
title=html.H1("Emission With Bands",style={'font-size':50,'font-weight':'bold'})
location=html.H1("Ettenheim EMC Lab",style={'font-size':50,'font-weight':'bold','text-align':'right'})
footer=html.Footer([html.P('Copyright © 2024 Monolithic Power Systems, Inc. All rights reserved.',style={'text-align':'center','color':'#666'})],style={'position':'relative','bottom':'0','width':'100%','padding':'20px 0px','background-color':'#e0e0e0','text-align':'center','margin-top':'20px'})

columnDefs_tests=[{"headerName":"",
        "field": "Show",
        "cellRenderer": "Button",
        "cellRendererParams": {'className': "block text-center text-md text-white rounded no-underline cursor-pointer hover:bg-blue-600", },
        'width': 70, 'pinned': 'left', 'cellStyle': {'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, 'sortable': False},
    {"headerName": "Test Name", "field": "Test Name", 'flex':1, "hide": False, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName": "Type", "field": "Type", 'width': 250, "hide": False, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName": "Limits", "field": "Limits", 'flex': 1, "hide": False, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Frequency Range","field": "Frequency Range", 'width': 180, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Operation Mode","field": "Operation Mode", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Modification","field": "Modification", 'flex': 1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName": "Date", "field": "Date", 'width': 200, "filter": "agDateColumnFilter", "filterParams": {"filterOptions": ["Equals", "Before", "After", "Between"]}},
    {"headerName":"Conclusion","field": "Test_Pass", 'width': 150, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}}]

columnDefs_scans=[
    {"headerName":"<",
        "field": "",
        "headerComponent": "ButtonHeader",
        'width': 70, 'pinned': 'left', 'headerComponentParams': {'className': "block text-center text-md text-white rounded no-underline cursor-pointer hover:bg-blue-600 d-flex align-items-center justify-content-center"}, 'sortable': False,
     },
    {"headerName":"Scan","field": "Scan", 'flex':1, "checkboxSelection": True, "headerCheckboxSelection": True, "filter": "agNumberColumnFilter", "filterParams": {"filterOptions": ["Equals", "Does not equals", "Greater than", "Less than", "Between"], "debounceMs": 500}},
    {"headerName":"Bands","field": "Bands", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Frequency Range","field": "Frequency Range", 'width': 250, "filter": "agNumberColumnFilter", "filterParams": {"filterOptions": ["Equals", "Does not equals", "Greater than", "Less than", "Between"], "debounceMs": 500}},
    {"headerName":"Step","field": "Frequency Step", 'flex':1, "filter": "agNumberColumnFilter", "filterParams": {"filterOptions": ["Equals", "Does not equals", "Greater than", "Less than", "Between"], "debounceMs": 500}},
    {"headerName":"Polarization","field": "Polarization", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"RBW","field": "RBW", 'flex':1, "filter": "agNumberColumnFilter", "filterParams": {"filterOptions": ["Equals", "Does not equals", "Greater than", "Less than", "Between"], "debounceMs": 500}},
    {"headerName": "Meas. Time", "field": "Meas Time", 'flex': 1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Detector","field": "Detector", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"headerName":"Conclusion","field": "Test_Pass", 'flex':1, "filter": "agTextColumnFilter", "filterParams": {"filterOptions": ["contains", "notContains", "Equals", "Does not equals"], "debounceMs": 500}},
    {"field": "Test Name", "hide": True},
    {"field": "Type", "hide": True},
    {"field": "Limits", "hide": True},
    {"headerName":"Test_data","field": "Test_data", "hide": True}]

getRowStyle_test = {
    "styleConditions": [
        {
            "condition": "params.data.Test_Pass == 'PASSED'",
            "style": {"backgroundColor": "green", "color": "white", "font-weight":"bold"},
        },
        {
            "condition": "params.data.Test_Pass == 'FAILED'",
            "style": {"backgroundColor": "red", "color": "white", "font-weight":"bold"},
        },
{
            "condition": "params.data.Test_Pass == 'INCONCLUSIVE'",
            "style": {"backgroundColor": "orange", "color": "white", "font-weight":"bold"},
        },
    ]
}

app = dash.Dash(__name__, include_assets_files=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

columnDefs_limits = [{"checkboxSelection": {'function': "params.data.disabled == 'False'"}, 'showDisabledCheckboxes': True, "headerCheckboxSelection": True, 'width': 50, 'pinned': 'left'},
    {"headerName":"Name","field": "Name", 'flex':1},
    {"field": "disabled", "hide": True}]

columnDefs_noise = [{"headerName":"", "checkboxSelection": True, "headerCheckboxSelection": True, 'width': 50, 'pinned': 'left'},
    {"headerName":"Name","field": "Name", 'flex':1},
    {"headerName": "Bands", "field": "Bands", 'flex': 1},
    {"headerName": "Frequency Range", "field": "Frequency Range", 'flex': 1},
    {"headerName": "Detector", "field": "Detector", 'flex': 1},
    {"headerName": "Data", "field": "Data", "hide": True}]

columnDefs_line = [{"headerName":"Name","field": "Name", 'width': 500},
    {"headerName":"Color","field": "Color",'width':'90px','editable':True, 'flex':1,'cellEditor':'agSelectCellEditor', 'cellEditorParams': {'values':['Blue', 'Orange', 'Green', 'Red', 'Purple', 'Brown', 'Pink', 'Gray', 'Light green','Light blue']}},
    {"headerName":"Width","field": "Width",'width':'90px','editable':True, 'flex':1,'cellEditor':{"function": "NumberInput"},"cellEditorParams" : {"placeholder": "Enter a number"}},
    {"headerName":"Type","field": "Type",'width':'90px', 'editable':True, 'flex':1,'cellEditor':'agSelectCellEditor', 'cellEditorParams': {'values':['solid','dash','dot']}}]

limits_table_h = dag.AgGrid(
        id="limits-table-h",
        rowData=[],
        columnDefs=columnDefs_limits,
        dashGridOptions={"rowSelection": "multiple", "rowDragManaged": True,
                "rowDragEntireRow": True,
                "rowDragMultiRow": True,
                "suppressMoveWhenRowDragging": True},
        defaultColDef={'resizable': True},
        selectAll=True,
        style={'center':True,'fontSize':'12px','height':'300px','width':'100%'})

line_table_h = dag.AgGrid(
        id="line-table-h",
        rowData=[],
        columnDefs=columnDefs_line,
        dashGridOptions={"rowDragManaged": True,
                "rowDragEntireRow": True,
                "rowDragMultiRow": True,
                "suppressMoveWhenRowDragging": True},
        defaultColDef={'resizable': True},
        style={'center':True,'fontSize':'12px','height':'300px','width':'100%'})

line_table_Div_h = html.Div([dbc.Stack([limits_table_h, line_table_h,],gap=2)],id='line-table-container-h',style={'width':800,'display':'none','position':'fixed','top':'20%','right':'305px','bg-color':'rgba(255,255,255,0.95)','padding':'10px 10px','boxShadow':'0px 4px 8px rgba(0,0,0,0.1)','zIndex':'1002','borderRadius':'8px','overflow':'auto'})

line_table_btn_h = html.Button('Show Line Display Parameters',id='line-table-btn-h',n_clicks=0,style={'width':'230px','height':'50px',"padding": "15px","background-color": "#1F3A68","color": "#FFF","border": "none","cursor": "pointer","font-size": "14px","font-family": "Arial, sans-serif","border-radius": "5px"})

line_menu_h = html.Div([dbc.Row((line_table_btn_h),justify='center')],style={'padding':'10px'})

limits_table_v = dag.AgGrid(
        id="limits-table-v",
        rowData=[],
        columnDefs=columnDefs_limits,
        dashGridOptions={"rowSelection": "multiple", "rowDragManaged": True,
                         "rowDragEntireRow": True,
                         "rowDragMultiRow": True,
                         "suppressMoveWhenRowDragging": True},
        defaultColDef={'resizable': True},
        style={'center':True,'fontSize':'12px','height':'300px','width':'100%'})

line_table_v = dag.AgGrid(
        id="line-table-v",
        rowData=[],
        columnDefs=columnDefs_line,
        dashGridOptions={"rowSelection": "multiple", "rowDragManaged": True,
                         "rowDragEntireRow": True,
                         "rowDragMultiRow": True,
                         "suppressMoveWhenRowDragging": True},
        defaultColDef={'resizable': True},
        style={'center':True,'fontSize':'12px','height':'300px','width':'100%'})

line_table_Div_v = html.Div([dbc.Stack([limits_table_v, line_table_v],gap=2)],id='line-table-container-v',style={'width':800,'display':'none','position':'fixed','top':'20%','right':'305px','bg-color':'rgba(255,255,255,0.95)','padding':'10px 10px','boxShadow':'0px 4px 8px rgba(0,0,0,0.1)','zIndex':'1002','borderRadius':'8px','overflow':'auto'})

line_table_btn_v = html.Button('Show Line Display Parameters',id='line-table-btn-v',n_clicks=0,style={'width':'230px','height':'50px',"padding": "15px","background-color": "#1F3A68","color": "#FFF","border": "none","cursor": "pointer","font-size": "14px","font-family": "Arial, sans-serif","border-radius": "5px"})

line_menu_v = html.Div([dbc.Row((line_table_btn_v),justify='center')],style={'padding':'10px'})

project = dbc.Stack([
                html.Div(dcc.Dropdown(placeholder="Select a project",id='Project-list',options=[],style={'width':'500px'})),
                html.Div(dcc.Upload(id='load-project',children=[html.Button('Load a project',id='Load-project',n_clicks=0,style={'width':'150px','borderRadius':'5px'})])),
                html.Div(html.Button('Remove a project',id='Remove-project',n_clicks=0,style={'width':'150px','borderRadius':'5px'})),
                html.Div(dbc.Button(id='project-loading-screen', children=['No loaded project'],disabled=True, style = {'width':'270px', 'borderRadius':'5px', 'border':'none','align-items':'center', 'font-weight':'bold', 'backgroundColor':'#119DFF'})),
            ],direction="horizontal",gap=3,style={'margin-left':'30px','align-items':'center'})

limits = dbc.Stack([
                html.Div(dcc.Dropdown(placeholder="Select a limit",id='limit-list',options=[limit for limit in Limit_database],style={'width':'400px'}, disabled = True)),
                html.Div(dcc.Upload(id='load-limits', accept='.txt,.csv,.xlsx',children=[html.Button('Load limits',id='Load-limit',n_clicks=0,style={'width':'150px','borderRadius':'5px'})])),
                html.Div(dbc.Button(id='limits-loading-screen', children=['No limits selected'],disabled=True, style = {'width':'270px', 'borderRadius':'5px', 'border':'none','align-items':'center', 'font-weight':'bold', 'backgroundColor':'#119DFF'})),
            ],direction="horizontal",gap=3,style={'margin-left':'10px','align-items':'center'})

project_limits = dbc.Row([dbc.Col(project), dbc.Col(limits)],style={'margin-bottom':'20px'})

table = dcc.Loading([dag.AgGrid(
        id="Test-table",
        rowData=[],
        columnDefs=columnDefs_tests,
        defaultColDef={'resizable': True},
        getRowStyle=getRowStyle_test,
        style={'width':'100%','center':True},
        dangerously_allow_code=True,
        dashGridOptions={"rowSelection": "multiple", "suppressRowClickSelection": True, "animateRows": False,"domLayout": "autoHeight", "overlayNoRowsTemplate": "Select a project","rowDragManaged": True, "rowDragEntireRow": True, "suppressMoveWhenRowDragging": True, 'suppressRowTransform': True})],
        overlay_style={"visibility":"visible", "filter": "blur(2px)"},type="circle")

emission_horizontal=dcc.Loading([dcc.Graph(id='emission_radiated_horizontal', figure={ 'data':[], 'layout':emission_h_layout}, config={'toImageButtonOptions': {'filename':'EmissionWithBand_EMC_chart_screenshot'}, 'responsive':True, 'displaylogo':False, 'editable':True, 'edits': {'annotationTail':False, 'annotationText':True, 'axisTitleText':False, 'colorbarPosition':False, 'colorbarTitleText':False, 'legendPosition':False, 'legendText':False, 'shapePosition':False, 'titleText':False}, 'modeBarButtonsToRemove': ['zoom', 'pan','zoomin','zoomout','autoscale','resetscale','lasso2d', 'select2d']},style={'height': '600px','width':'100%','fontWeight':'bold', 'display':'block'})], id='loading-emission_horizontal', overlay_style={"visibility":"unvisible", "filter": "blur(2px)"},type="circle")
emission_vertical=dcc.Loading([dcc.Graph(id='emission_radiated_vertical', figure={ 'data':[], 'layout':emission_v_layout}, config={'toImageButtonOptions': {'filename':'EmissionWithBand_EMC_chart_screenshot'}, 'responsive':True, 'displaylogo':False, 'editable':True, 'edits': {'annotationTail':False, 'annotationText':True, 'axisTitleText':False, 'colorbarPosition':False, 'colorbarTitleText':False, 'legendPosition':False, 'legendText':False, 'shapePosition':False, 'titleText':False}, 'modeBarButtonsToRemove': ['zoom', 'pan','zoomin','zoomout','autoscale','resetscale','lasso2d', 'select2d']},style={'height': '600px','width':'100%','fontWeight':'bold', 'display':'block'})], id='loading-emission_vertical',overlay_style={"visibility":"visible", "filter": "blur(2px)"},type="circle")

suspectTable_radiated = dag.AgGrid(
        id = "suspectsTable-radiated",
        rowData = [],
        columnDefs = columnDefs_suspectTable,
        getRowStyle=getRowStyle_suspect,
        defaultColDef = {'resizable': True},
        style = {'width':'100%','center':True, 'display':'block'},
        dashGridOptions = {"rowSelection": "multiple", "suppressRowClickSelection": True, "animateRows": False,"domLayout": "autoHeight", "rowDragManaged": True, 'isRowSelectable': True,
                "rowDragEntireRow": True,
                "suppressMoveWhenRowDragging": True,
                "isRowSelectable": {'function': "params.data.disabled == 'False'"}})

suspectTable_conducted = dag.AgGrid(
        id = "suspectsTable-conducted",
        rowData = [],
        columnDefs = columnDefs_suspectTable,
        getRowStyle=getRowStyle_suspect,
        defaultColDef = {'resizable': True, "filter": "agTextColumnFilter"},
        style = {'width':'100%','center':True, 'display':'block'},
        dashGridOptions = {"rowSelection": "multiple", "suppressRowClickSelection": True, "animateRows": False,"domLayout": "autoHeight", "rowDragManaged": True,
                "rowDragEntireRow": True,
                "suppressMoveWhenRowDragging": True,
                "isRowSelectable": {'function': "params.data.disabled == 'False'"}})

emission_table=html.Div([dbc.Stack([emission_horizontal, emission_vertical, suspectTable_radiated], gap=3, style={'height': '100%','width':'100%','border':'1px solid #d6d6d6','border-top':'none','margin-top':'-20px', 'padding':'10px'})])

emission_conducted_ground = dcc.Loading([dcc.Graph(id='emission_conducted_ground', figure={ 'data':[], 'layout':emission_conduction_ground_layout}, config={'toImageButtonOptions': {'filename':'EmissionWithBand_EMC_chart_screenshot'}, 'responsive':True, 'displaylogo':False, 'editable':True, 'edits': {'annotationTail':False, 'annotationText':True, 'axisTitleText':False, 'colorbarPosition':False, 'colorbarTitleText':False, 'legendPosition':False, 'legendText':False, 'shapePosition':False, 'titleText':False}, 'modeBarButtonsToRemove': ['zoom', 'pan','zoomin','zoomout','autoscale','resetscale','lasso2d', 'select2d']},style={'height': '600px','width':'100%','fontWeight':'bold', 'display':'block'})], id='loading-emission_ground', overlay_style={"visibility":"unvisible", "filter": "blur(2px)"},type="circle")
emission_conducted_supply = dcc.Loading([dcc.Graph(id='emission_conducted_supply', figure={ 'data':[], 'layout':emission_conduction_supply_layout}, config={'toImageButtonOptions': {'filename':'EmissionWithBand_EMC_chart_screenshot'}, 'responsive':True, 'displaylogo':False, 'editable':True, 'edits': {'annotationTail':False, 'annotationText':True, 'axisTitleText':False, 'colorbarPosition':False, 'colorbarTitleText':False, 'legendPosition':False, 'legendText':False, 'shapePosition':False, 'titleText':False}, 'modeBarButtonsToRemove': ['zoom', 'pan','zoomin','zoomout','autoscale','resetscale','lasso2d', 'select2d']},style={'height': '600px','width':'100%','fontWeight':'bold', 'display':'block'})], id='loading-emission_supply', overlay_style={"visibility":"unvisible", "filter": "blur(2px)"},type="circle")

conduction_table = html.Div([dbc.Stack([emission_conducted_ground, emission_conducted_supply, suspectTable_conducted], gap=3, style={'height': '100%','width':'100%','border':'1px solid #d6d6d6','border-top':'none','margin-top':'-20px', 'padding':'10px'})])

tables=html.Div([
    dcc.Tabs(id='test-tabs',value=None, children=[
        dcc.Tab(id='emission-radiated-electric-tab', label='Emission - Radiated Electric', value='emission-radiated-electric-tab',disabled=True,children=emission_table,style={'font-size':18,'font-weight': 'bold'},selected_style={'font-size':18,'font-weight': 'bold'}),
        dcc.Tab(id='emission-conducted-voltage-tab', label='Emission - Conducted Voltage', value='emission-conducted-voltage-tab',disabled=True,children = conduction_table ,style={'font-size':18,'font-weight': 'bold'},selected_style={'font-size':18,'font-weight': 'bold'}),
        dcc.Tab(id='report-tab', label='Report', value='report-tab',disabled=True,children=[html.Div('',style={'border':'1px solid #d6d6d6','border-top':'none'})],style={'font-size':18,'font-weight': 'bold'},selected_style={'font-size':18,'font-weight': 'bold'})
    ],style={'padding':'20px 0px'})])

log_btn_h = html.Div([html.Label('Horizontal Graph',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'}),html.Label('X axis Scale',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'}),dcc.RadioItems(id='xaxis-emission_h',options=[{'label':' Logarithmic','value':'log'},{'label':' Linear','value':'linear'}],value='log',inline=True,labelStyle={'fontWeight':'bold','margin-right':'10px','margin-bottom':'10px'},className='radio-item-spacing')])
input_x_min_max_h = html.Div([dbc.Row(html.Label('X axis limits',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'})),
                            dbc.Row([dbc.Col([dbc.Stack([html.Label('Min',style={'fontWeight':'bold'}),dcc.Input(id='input_x_min-emission_h',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)]),dbc.Col([dbc.Stack([html.Label('Max',style={'fontWeight':'bold'}),dcc.Input(id='input_x_max-emission_h',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)])],className="g-0",style={'margin-bottom':'10px'})])
input_y_min_max_h = html.Div([dbc.Row(html.Label('Y axis limits',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'})),
                            dbc.Row([dbc.Col([dbc.Stack([html.Label('Min',style={'fontWeight':'bold'}),dcc.Input(id='input_y_min-emission_h',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)]),dbc.Col([dbc.Stack([html.Label('Max',style={'fontWeight':'bold'}),dcc.Input(id='input_y_max-emission_h',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)])],className="g-0")])

log_btn_v = html.Div([html.Label('Vertical Graph',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'}),html.Label('X axis Scale',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'}),dcc.RadioItems(id='xaxis-emission_v',options=[{'label':' Logarithmic','value':'log'},{'label':' Linear','value':'linear'}],value='log',inline=True,labelStyle={'fontWeight':'bold','margin-right':'10px','margin-bottom':'10px'},className='radio-item-spacing')])
input_x_min_max_v = html.Div([dbc.Row(html.Label('X axis limits',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'})),
                            dbc.Row([dbc.Col([dbc.Stack([html.Label('Min',style={'fontWeight':'bold'}),dcc.Input(id='input_x_min-emission_v',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)]),dbc.Col([dbc.Stack([html.Label('Max',style={'fontWeight':'bold'}),dcc.Input(id='input_x_max-emission_v',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)])],className="g-0",style={'margin-bottom':'10px'})])
input_y_min_max_v = html.Div([dbc.Row(html.Label('Y axis limits',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'})),
                            dbc.Row([dbc.Col([dbc.Stack([html.Label('Min',style={'fontWeight':'bold'}),dcc.Input(id='input_y_min-emission_v',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)]),dbc.Col([dbc.Stack([html.Label('Max',style={'fontWeight':'bold'}),dcc.Input(id='input_y_max-emission_v',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)])],className="g-0")])

Cursor_menu_h=html.Div([
    dbc.Row(dbc.Stack([html.Label('Activate cursors',style={'fontWeight':'bold','margin-right':'10px'}),daq.BooleanSwitch(id='activate-cursor-h',on=False)],direction="horizontal",gap=0.5,style={'padding':'5px 20px','margin-bottom':'5px'})),
    dbc.Row([dcc.Dropdown(id='cursor-list-h',options=[],placeholder="Select a line",style={'width':'240px','display': 'none','margin-bottom':'5px'})]),
    dbc.Row(html.Label(f'ΔFrequency (MHz) = - \n ΔLevel (dBμV/m) = -',id='cursor-output-h',style={"white-space": "pre",'fontWeight':'bold','display': 'none'}))],style={'padding':'10px'})

horizontal_parameters_menu = html.Div([dbc.Stack([log_btn_h, input_x_min_max_h, input_y_min_max_h, Cursor_menu_h, line_menu_h], gap = 1)],id='Div_axes_param_h',style={'border':'1px solid #d6d6d6','border-radius':'10px','padding':'10px','margin-bottom':'10px', 'display':'none'})

Cursor_menu_v=html.Div([
    dbc.Row(dbc.Stack([html.Label('Activate cursors',style={'fontWeight':'bold','margin-right':'10px'}),daq.BooleanSwitch(id='activate-cursor-v',on=False)],direction="horizontal",gap=0.5,style={'padding':'5px 20px','margin-bottom':'5px'})),
    dbc.Row([dcc.Dropdown(id='cursor-list-v',options=[],placeholder="Select a line",style={'width':'240px','display': 'none','margin-bottom':'5px'})]),
    dbc.Row(html.Label(f'ΔFrequency (MHz) = - \n ΔLevel (dBμV/m) = -',id='cursor-output-v',style={"white-space": "pre",'fontWeight':'bold','display': 'none'}))],style={'padding':'10px'})

vertical_parameters_menu = html.Div([dbc.Stack([log_btn_v,input_x_min_max_v,input_y_min_max_v, Cursor_menu_v, line_menu_v], gap = 1)],id='Div_axes_param_v',style={'border':'1px solid #d6d6d6','border-radius':'10px','padding':'10px','margin-bottom':'10px', 'display':'none'})

line_table_btn = html.Button('Show Line Display Parameters',id='line_table_btn',n_clicks=0,style={'width':'230px','height':'50px',"padding": "15px","background-color": "#1F3A68","color": "#FFF","border": "none","cursor": "pointer","font-size": "14px","font-family": "Arial, sans-serif","border-radius": "5px"})

line_menu = html.Div([dbc.Row(html.Label('Line Display Parameters',style={'margin-bottom':'5px','margin-left':'25px','fontWeight':'bold'})),dbc.Row((line_table_btn),justify='center')],style={'border':'1px solid #d6d6d6','border-radius':'10px','padding':'10px','margin-bottom':'10px'})

marker_btn = html.Button('Clear Markers',id='clear_markers_btn',n_clicks=0,style={'width':'230px','height':'50px',"padding": "15px","background-color": "#1F3A68","color": "#FFF","border": "none","cursor": "pointer","font-size": "14px","font-family": "Arial, sans-serif","border-radius": "5px"})
marker_menu = html.Div([dbc.Row(dbc.Stack([html.Label('Activate Markers',style={'fontWeight':'bold','margin-right':'10px'}),daq.BooleanSwitch(id='activate-marker',on=False)],direction="horizontal",gap=0.5,style={'padding':'5px 20px','margin-bottom':'5px'}),justify='center'),dbc.Row([marker_btn],justify='center')],style={'border':'1px solid #d6d6d6','border-radius':'10px','padding':'10px','margin-bottom':'10px'})

minimize_suspectTable_radiated_btn = html.Div([dbc.Row(html.Button('Hide Suspect Table',id='minimize_suspectTable_radiated_btn',n_clicks=1,style={'width':'230px','height':'50px',"padding": "15px","background-color": "#1F3A68","color": "#FFF","border": "none","cursor": "pointer","font-size": "14px","font-family": "Arial, sans-serif","border-radius": "5px"}),justify='center')],style={'border':'1px solid #d6d6d6','border-radius':'10px','padding':'10px','margin-bottom':'10px'})

log_btn_ground = html.Div([html.Label('Ground Graph',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'}),html.Label('X axis Scale',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'}),dcc.RadioItems(id='xaxis-emission_ground',options=[{'label':' Logarithmic','value':'log'},{'label':' Linear','value':'linear'}],value='log',inline=True,labelStyle={'fontWeight':'bold','margin-right':'10px','margin-bottom':'10px'},className='radio-item-spacing')])
input_x_min_max_ground = html.Div([dbc.Row(html.Label('X axis limits',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'})),
                            dbc.Row([dbc.Col([dbc.Stack([html.Label('Min',style={'fontWeight':'bold'}),dcc.Input(id='input_x_min-emission_ground',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)]),dbc.Col([dbc.Stack([html.Label('Max',style={'fontWeight':'bold'}),dcc.Input(id='input_x_max-emission_ground',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)])],className="g-0",style={'margin-bottom':'10px'})])
input_y_min_max_ground = html.Div([dbc.Row(html.Label('Y axis limits',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'})),
                            dbc.Row([dbc.Col([dbc.Stack([html.Label('Min',style={'fontWeight':'bold'}),dcc.Input(id='input_y_min-emission_ground',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)]),dbc.Col([dbc.Stack([html.Label('Max',style={'fontWeight':'bold'}),dcc.Input(id='input_y_max-emission_ground',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)])],className="g-0")])
Cursor_menu_ground=html.Div([
    dbc.Row(dbc.Stack([html.Label('Activate cursors',style={'fontWeight':'bold','margin-right':'10px'}),daq.BooleanSwitch(id='activate-cursor-ground',on=False)],direction="horizontal",gap=0.5,style={'padding':'5px 20px','margin-bottom':'5px'})),
    dbc.Row([dcc.Dropdown(id='cursor-list-ground',options=[],placeholder="Select a line",style={'width':'240px','display': 'none','margin-bottom':'5px'})]),
    dbc.Row(html.Label(f'ΔFrequency (MHz) = - \n ΔLevel (dBμV/m) = -',id='cursor-output-ground',style={"white-space": "pre",'fontWeight':'bold','display': 'none'}))],style={'padding':'10px'})

limits_table_ground = dag.AgGrid(
        id="limits-table-ground",
        rowData=[],
        columnDefs=columnDefs_limits,
        dashGridOptions={"rowDragManaged": True,
                         "rowDragEntireRow": True,
                         "rowSelection": "multiple",
                         "suppressMoveWhenRowDragging": True,
                         "isRowSelectable": {'function': "params.data.disabled == 'False'"}},
        defaultColDef={'resizable': True},
        style={'center':True,'fontSize':'12px','height':'300px','width':'100%'})

# noise_table_ground = dag.AgGrid(
#         id = "noise-table-ground",
#         rowData = [],
#         columnDefs = columnDefs_noise,
#         dashGridOptions={"rowDragManaged": True,
#                          "rowDragEntireRow": True,
#                          "rowSelection": "multiple",
#                          "suppressMoveWhenRowDragging": True},
#         defaultColDef = {'resizable': True},
#         selectAll = True,
#         style = {'center':True,'fontSize':'12px','height':'300px','width':'100%'})

line_table_ground = dag.AgGrid(
        id="line-table-ground",
        rowData=[],
        columnDefs=columnDefs_line,
        dashGridOptions={"rowDragManaged": True,
                         "rowDragEntireRow": True,
                         "rowSelection": "multiple",
                         "suppressMoveWhenRowDragging": True},
        defaultColDef={'resizable': True, "filter": "agTextColumnFilter"},
        style={'center':True,'fontSize':'12px','height':'300px','width':'100%'})

line_table_Div_ground = html.Div([dbc.Stack([limits_table_ground, line_table_ground,],gap=2)],id='line-table-container-ground',style={'width':800,'display':'none','position':'fixed','top':'20%','right':'305px','bg-color':'rgba(255,255,255,0.95)','padding':'10px 10px','boxShadow':'0px 4px 8px rgba(0,0,0,0.1)','zIndex':'1002','borderRadius':'8px','overflow':'auto'})

line_table_btn_ground = html.Button('Show Line Display Parameters',id='line-table-btn-ground',n_clicks=0,style={'width':'230px','height':'50px',"padding": "15px","background-color": "#1F3A68","color": "#FFF","border": "none","cursor": "pointer","font-size": "14px","font-family": "Arial, sans-serif","border-radius": "5px"})

line_menu_ground = html.Div([dbc.Row((line_table_btn_ground),justify='center')],style={'padding':'10px'})

ground_parameters_menu_conducted = html.Div([dbc.Stack([log_btn_ground,input_x_min_max_ground,input_y_min_max_ground, Cursor_menu_ground, line_menu_ground], gap = 1)],id='Div_axes_param_ground',style={'border':'1px solid #d6d6d6','border-radius':'10px','padding':'10px','margin-bottom':'10px', 'display':'none'})

log_btn_supply = html.Div([html.Label('Supply Graph',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'}),html.Label('X axis Scale',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'}),dcc.RadioItems(id='xaxis-emission_supply',options=[{'label':' Logarithmic','value':'log'},{'label':' Linear','value':'linear'}],value='log',inline=True,labelStyle={'fontWeight':'bold','margin-right':'10px','margin-bottom':'10px'},className='radio-item-spacing')])
input_x_min_max_supply = html.Div([dbc.Row(html.Label('X axis limits',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'})),
                            dbc.Row([dbc.Col([dbc.Stack([html.Label('Min',style={'fontWeight':'bold'}),dcc.Input(id='input_x_min-emission_supply',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)]),dbc.Col([dbc.Stack([html.Label('Max',style={'fontWeight':'bold'}),dcc.Input(id='input_x_max-emission_supply',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)])],className="g-0",style={'margin-bottom':'10px'})])
input_y_min_max_supply = html.Div([dbc.Row(html.Label('Y axis limits',style={'fontWeight':'bold','margin-left':'20px','margin-bottom':'5px'})),
                            dbc.Row([dbc.Col([dbc.Stack([html.Label('Min',style={'fontWeight':'bold'}),dcc.Input(id='input_y_min-emission_supply',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)]),dbc.Col([dbc.Stack([html.Label('Max',style={'fontWeight':'bold'}),dcc.Input(id='input_y_max-emission_supply',type='number',value=None,debounce = True,style={'width':'75px', 'textAlign':'center'})],direction="horizontal",gap=2)])],className="g-0")])
Cursor_menu_supply=html.Div([
    dbc.Row(dbc.Stack([html.Label('Activate cursors',style={'fontWeight':'bold','margin-right':'10px'}),daq.BooleanSwitch(id='activate-cursor-supply',on=False)],direction="horizontal",gap=0.5,style={'padding':'5px 20px','margin-bottom':'5px'})),
    dbc.Row([dcc.Dropdown(id='cursor-list-supply',options=[],placeholder="Select a line",style={'width':'240px','display': 'none','margin-bottom':'5px'})]),
    dbc.Row(html.Label(f'ΔFrequency (MHz) = - \n ΔLevel (dBμV/m) = -',id='cursor-output-supply',style={"white-space": "pre",'fontWeight':'bold','display': 'none'}))],style={'padding':'10px'})

limits_table_supply = dag.AgGrid(
        id="limits-table-supply",
        rowData=[],
        columnDefs=columnDefs_limits,
        dashGridOptions={"rowDragManaged": True,
                         "rowDragEntireRow": True,
                         "rowSelection": "multiple",
                         "suppressMoveWhenRowDragging": True,
                         "isRowSelectable": {'function': "params.data.disabled == 'False'"}},
        defaultColDef={"rowDragManaged": True,
                "rowDragEntireRow": True,
                "rowSelection": "multiple",
                "suppressMoveWhenRowDragging": True, "filter": "agTextColumnFilter"},
        style={'center':True,'fontSize':'12px','height':'300px','width':'100%'})

line_table_supply = dag.AgGrid(
        id="line-table-supply",
        rowData=[],
        columnDefs=columnDefs_line,
        defaultColDef={"rowDragManaged": True,
                "rowDragEntireRow": True,
                "rowSelection": "multiple",
                "suppressMoveWhenRowDragging": True, "filter": "agTextColumnFilter"},
        style={'center':True,'fontSize':'12px','height':'300px','width':'100%'})

line_table_Div_supply = html.Div([dbc.Stack([limits_table_supply, line_table_supply],gap=2)],id='line-table-container-supply',style={'width':800,'display':'none','position':'fixed','top':'20%','right':'305px','bg-color':'rgba(255,255,255,0.95)','padding':'10px 10px','boxShadow':'0px 4px 8px rgba(0,0,0,0.1)','zIndex':'1002','borderRadius':'8px','overflow':'auto'})

line_table_btn_supply = html.Button('Show Line Display Parameters',id='line-table-btn-supply',n_clicks=0,style={'width':'230px','height':'50px',"padding": "15px","background-color": "#1F3A68","color": "#FFF","border": "none","cursor": "pointer","font-size": "14px","font-family": "Arial, sans-serif","border-radius": "5px"})

line_menu_supply = html.Div([dbc.Row((line_table_btn_supply),justify='center')],style={'padding':'10px'})

supply_parameters_menu_conducted = html.Div([dbc.Stack([log_btn_supply,input_x_min_max_supply,input_y_min_max_supply, Cursor_menu_supply, line_menu_supply], gap = 1)],id='Div_axes_param_supply',style={'border':'1px solid #d6d6d6','border-radius':'10px','padding':'10px','margin-bottom':'10px', 'display':'none'})

marker_btn_conducted = html.Button('Clear Markers',id='clear_markers_btn_conducted',n_clicks=0,style={'width':'230px','height':'50px',"padding": "15px","background-color": "#1F3A68","color": "#FFF","border": "none","cursor": "pointer","font-size": "14px","font-family": "Arial, sans-serif","border-radius": "5px"})
marker_menu_conducted = html.Div([dbc.Row(dbc.Stack([html.Label('Activate Markers',style={'fontWeight':'bold','margin-right':'10px'}),daq.BooleanSwitch(id='activate-marker-conducted',on=True)],direction="horizontal",gap=0.5,style={'padding':'5px 20px','margin-bottom':'5px'}),justify='center'),dbc.Row([marker_btn_conducted],justify='center')],style={'border':'1px solid #d6d6d6','border-radius':'10px','padding':'10px','margin-bottom':'10px'})

minimize_suspectTable_conducted_btn = html.Div([dbc.Row(html.Button('Hide Suspect Table',id='minimize_suspectTable_conducted_btn',n_clicks=1,style={'width':'230px','height':'50px',"padding": "15px","background-color": "#1F3A68","color": "#FFF","border": "none","cursor": "pointer","font-size": "14px","font-family": "Arial, sans-serif","border-radius": "5px"}),justify='center')],style={'border':'1px solid #d6d6d6','border-radius':'10px','padding':'10px','margin-bottom':'10px'})

default_colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
name2color = {'Blue':'#1f77b4', 'Orange':'#ff7f0e', 'Green':'#2ca02c', 'Red':'#d62728', 'Purple':'#9467bd', 'Brown':'#8c564b', 'Pink':'#e377c2', 'Gray':'#7f7f7f', 'Light green':'#bcbd22','Light blue':'#17becf'}

app.layout = html.Div([
    # Button to toggle the sidebar
    html.Button("Graph Parameters", id="toggle-button", n_clicks=0, disabled=True,
                style={
                    "position": "fixed",
                    "right": "20px",
                    "top": "94px",
                    "z-index": "1001",
                    "background-color": "#1F3A68",  # MPS-style blue background
                    "color": "#FFF",
                    "border": "none",
                    "padding": "10px 20px",
                    "cursor": "pointer",
                    "font-size": "16px",
                    "border-radius": "5px",
                    "transition": "background-color 0.3s ease",  # Button hover effect
                    "transition": "transform 0.3s ease",
                }),

    # Sidebar div
    html.Div(id="sidebar", style=sidebar_style, children=[
        html.H2("Graph Parameters", style={"font-size": "24px", "margin-bottom": "20px", "font-weight": "bold", "font-family": "Arial, sans-serif"}),
        html.Hr(style={"border-color": "#BDC3C7"}),  # Light gray line

        # Emission Results Button
        html.Button("Radiated Electric", id="radiated-btn", style=button_style, disabled=True),

        # Emission Results Submenu
        html.Div(id="radiated-electric-submenu", children=[
            dbc.Stack([horizontal_parameters_menu, vertical_parameters_menu, marker_menu, minimize_suspectTable_radiated_btn], gap=1)
        ], style=submenu_style),

        # Immunity Button
        html.Button("Conducted Voltage", id="conducted-btn", style=button_style, disabled=True),

        # Immunity Submenu
        html.Div(id="conducted-voltage-submenu", children=[
            dbc.Stack([ground_parameters_menu_conducted, supply_parameters_menu_conducted, marker_menu_conducted, minimize_suspectTable_conducted_btn], gap=1)
        ], style=submenu_style),
    ]),

    # Main content area
    html.Div([
        html.Div([
            html.Div([
                logo, title
            ], style={'display': 'flex', 'align-items': 'center'}),
            location
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'space-between',
                  'padding': '10px 20px', 'background-color': '#1E2A38', 'color': 'white', 'margin-bottom': '20px'}),
        html.Div(
            [project_limits, table, tables], style={'flex': '1', 'margin': '0 20px'}),
        footer,
        line_table_Div_h,
        line_table_Div_v,
        line_table_Div_ground,
        line_table_Div_supply,
        dcc.Store(id='left-cursor-h', data=None),
        dcc.Store(id='left-cursor-v', data=None),
        dcc.Store(id='right-cursor-h', data=None),
        dcc.Store(id='right-cursor-v', data=None),
        dcc.Store(id='markers-h', data=[]),
        dcc.Store(id='markers-v', data=[]),
        dcc.Store(id='left-cursor-ground', data=None),
        dcc.Store(id='left-cursor-supply', data=None),
        dcc.Store(id='cursor_data', data={'left': {},'right': {}}),
        dcc.Store(id='right-cursor-supply', data=None),
        dcc.Store(id='markers-ground', data=[]),
        dcc.Store(id='markers-supply', data=[]),
        dcc.Store(id='colors', data=default_colors),
        dcc.Store(id='limit_database', data=Limit_database),
        dcc.Store(id='rowData_tests', data={}),
        dcc.Store(id='rowData_scans', data={}),
        dcc.Store(id='selected-data-conducted', data = []),
        dcc.Store(id='selected-data-radiated', data = []),
        dcc.Store(id='hide-button', data = None),
    ], style={'display': 'flex', 'flexDirection': 'column', 'minHeight': '100vh'})
])

# clientside_callback(
#     """
#     function(params) {
#         const columnId = params.columnId;
#         const button = document.createElement('button');
#         button.innerText = 'Hide';
#         button.onclick = function() {
#             const dashCallback = window.dash_clientside[window.dash_clientside.callback_contexts[0]];
#             dashCallback({"index":0, "value": columnId});
#         };
#         return button;
#     }
#     """,
#     Output("Test-table", 'cellRendererData'),
#     Input("Test-table", 'columnDefs'),
# )

# @app.callback(Output('noise-table-ground', 'rowData'),
#     Input("Test-table", "selectedRows"),
#     State('noise-table-ground', 'rowData'),
#     prevent_initial_call=True
#     )
#
# def fill_noise_table_ground(selectedRows, rowData):
#     return
#
# def fill_noise_table(selectedRows, rowData):
#     if selectedRows:
#
#     return

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Input('line-table-ground', 'virtualRowData'),
    State('emission_conducted_ground', 'figure'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def emphasize_chart_ground(line_table, figure):
    if line_table:
        result = emphasize_chart(line_table, figure)
        return result
    else:
        raise PreventUpdate

@app.callback(Output('emission_conducted_supply', 'figure', allow_duplicate = True),
    Input('line-table-supply', 'virtualRowData'),
    State('emission_conducted_supply', 'figure'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def emphasize_chart_supply(line_table, figure):
    if line_table:
        return emphasize_chart(line_table, figure)
    else:
        raise PreventUpdate

@app.callback(Output('emission_radiated_horizontal', 'figure', allow_duplicate = True),
    Input('line-table-h', 'virtualRowData'),
    State('emission_radiated_horizontal', 'figure'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def emphasize_chart_horizontal(line_table, figure):
    if line_table:
        return emphasize_chart(line_table, figure)
    else:
        raise PreventUpdate

@app.callback(Output('emission_conducted_supply', 'figure', allow_duplicate = True),
    Input('line-table-v', 'virtualRowData'),
    State('emission_radiated_vertical', 'figure'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def emphasize_chart_vertical(line_table, figure):
    if line_table:
        return emphasize_chart(line_table, figure)
    else:
        raise PreventUpdate


def returnSum(myDict):
    list = []
    for i in myDict:
        list = list + myDict[i]

    return list

def emphasize_chart(line_table, figure):
    color_to_color_gradient = {'Blue': {}, 'Orange': {}, 'Green': {}, 'Red': {}, 'Purple': {}, 'Brown': {}, 'Pink': {},
                               'Gray': {}, 'Light green': {}, 'Light blue': {}}
    for index, trace in enumerate(figure['data']):
        if 'Limit' not in trace['name'] and 'Suspect' not in trace['name']:
            if trace['meta']['Color'][0] in color_to_color_gradient[trace['meta']['Color'][1]]:
                color_to_color_gradient[trace['meta']['Color'][1]][trace['meta']['Color'][0]].append(index)
            else:
                color_to_color_gradient[trace['meta']['Color'][1]][trace['meta']['Color'][0]] = [index]

    key_index = []
    for color, list_color in color_to_color_gradient.items():
        val = returnSum(list_color)
        if len(val) > 1:
            for item_init in val:
                for item in val:
                    if item_init != item:
                        if len(set(figure['data'][item_init]['x']) & set(figure['data'][item]['x'])) > 1:
                            key_index.append(item_init)
                            key_index.append(item)
                            break

    if key_index != []:
        color_order = {}
        for color, color_list in color_to_color_gradient.items():
            for key in list(color_list.keys()):
                for index in color_list[key]:
                    if index in key_index:
                        code_list = key.replace('rgb(', '').replace(')', '').split(',')
                        b = [int(item) for item in code_list]
                        sum_code = sum(b)
                        color_order[key] = sum_code
        color_order = dict(sorted(color_order.items(), key=lambda item: item[1]))
        color_order = list(color_order.keys())
        index = 0
        for row in line_table:
            for trace_index, trace in enumerate(figure['data']):
                if row['Name'] == trace['meta']['Name'] and trace_index in key_index:
                    trace['line']['color'] = color_order[index]
                    trace['meta']['Color'][0] = color_order[index]

                    for cursor in trace['meta']['Cursors']:
                        for shape in figure['layout']['shapes']:
                            if shape['name'] == cursor:
                                shape['line']['color'] = trace['meta']['Color'][0]
                        for annotation in figure['layout']['annotations']:
                            if annotation['name'] == cursor:
                                annotation['bgcolor'] = trace['meta']['Color'][0]

                    for trace in figure['data']:
                        if trace['name'] in figure['data'][trace_index]['meta']['Limits']:
                            trace['fillcolor'] = color_order[index]
                    index += 1

    return figure

@app.callback(Output('test-tabs', 'value', allow_duplicate = True),
    Input('emission-conducted-voltage-tab', 'disabled'),
    Input('emission-radiated-electric-tab', 'disabled'),
    prevent_initial_call=True
    )

def show_tab_content(disabled_emission_conducted_voltage_tab, disabled_emission_radiated_electric_tab):
    triggered_id = ctx.triggered_id
    if disabled_emission_conducted_voltage_tab is True and disabled_emission_radiated_electric_tab is True:
        return None
    elif triggered_id == 'emission-conducted-voltage-tab' and disabled_emission_conducted_voltage_tab is False:
        return 'emission-conducted-voltage-tab'
    elif triggered_id == 'emission-conducted-voltage-tab' and disabled_emission_conducted_voltage_tab is True:
        return 'emission-radiated-electric-tab'
    elif triggered_id == 'emission-radiated-electric-tab' and disabled_emission_radiated_electric_tab is False:
        return 'emission-radiated-electric-tab'
    elif triggered_id == 'emission-radiated-electric-tab' and disabled_emission_radiated_electric_tab is True:
        return 'emission-conducted-voltage-tab'

@app.callback(Output('suspectsTable-conducted', 'rowData'),
    Output('suspectsTable-conducted', 'style'),
    Output('suspectsTable-conducted', 'selectedRows'),
    Output('suspectsTable-radiated', 'rowData'),
    Output('suspectsTable-radiated', 'style'),
    Output('suspectsTable-radiated', 'selectedRows'),
    Input('selected-data-conducted', "data"),
    Input('selected-data-radiated', "data"),
    State("Test-table", "rowData"),
    State('suspectsTable-radiated', 'style'),
    State('suspectsTable-conducted', 'style'),
    cancel=[Input("Test-table", "selectedRows")])

def select_emission_graph(data_conducted, data_radiated, rowData_scan, style_suspectsTable_radiated, style_suspectsTable_conducted):
    triggered_id = ctx.triggered_id
    if triggered_id == 'selected-data-conducted':
        rowData_suspectsTable_conducted, style_suspectsTable_conducted, selectedRows_suspectsTable_conducted = suspectsTable(data_conducted, style_suspectsTable_conducted)
        return rowData_suspectsTable_conducted, style_suspectsTable_conducted, selectedRows_suspectsTable_conducted, no_update, no_update, no_update
    elif triggered_id == 'selected-data-radiated':
        rowData_suspectsTable_radiated, style_suspectsTable_radiated, selectedRows_suspectsTable_radiated = suspectsTable(data_radiated, style_suspectsTable_radiated)
        return no_update, no_update, no_update, rowData_suspectsTable_radiated, style_suspectsTable_radiated, selectedRows_suspectsTable_radiated
    else:
        raise PreventUpdate

def suspectsTable(selectedRows, style):
    rowData = []
    if selectedRows:
        time.sleep(1)
        for row in selectedRows:
            if row['Data'][1]:
                suspects = pd.read_json(row['Data'][1])
                test_name = row['Test Name']
                for i in range(len(suspects)):
                    Scan = int(suspects.iloc[i]['Scan'])
                    Band = str(suspects.iloc[i]['Band'])
                    Polarization = suspects.iloc[i]['Polarization']
                    Frequency = suspects.iloc[i]['Frequency (MHz)']
                    if Frequency.split(' ')[1] == 'kHz':
                        Frequency = (float(Frequency.split(' ')[0]))/(10**3)
                    else:
                        Frequency = float(Frequency.split(' ')[0])
                    Detector = str(suspects.iloc[i]['Detector'])
                    if Detector == 'CAVG':
                        Detector = 'AVG'
                    MeasValue = int(suspects.iloc[i]['Meas.Value (dBµV/m)'])
                    LimitValue = int(suspects.iloc[i]['Limit.Value (dBµV/m)'])
                    Diff = int(suspects.iloc[i]['Diff (dB)'])
                    RBW = suspects.iloc[i]['RBW']
                    Pass_Fail = suspects.iloc[i]['Pass/Fail']
                    rowData.append({
                        "Test Name": test_name,
                        "Scan": Scan,
                        "Band": Band,
                        "Polarization": Polarization,
                        "Frequency": Frequency,
                        "Detector": Detector,
                        "MeasValue": MeasValue,
                        "LimitValue": LimitValue,
                        "Diff": Diff,
                        "RBW": RBW,
                        "Pass_Fail": Pass_Fail,
                        'disabled': 'False'})
    if rowData != []:
        style['display'] = 'block'
        selected = rowData
    else:
        style['display'] = 'none'
        selected = []
    return rowData, style, selected

@app.callback(Output('suspectsTable-conducted', 'style', allow_duplicate = True),
    Output('minimize_suspectTable_conducted_btn', "children"),
    Input('minimize_suspectTable_conducted_btn', "n_clicks"),
    State('suspectsTable-conducted', 'style'),
    prevent_initial_call=True)

def minimize_suspectTable_conducted(n_clicks, style):
    return minimize_suspectTable(n_clicks, style)

@app.callback(Output('suspectsTable-radiated', 'style', allow_duplicate = True),
    Output('minimize_suspectTable_radiated_btn', "children"),
    Input('minimize_suspectTable_radiated_btn', "n_clicks"),
    State('suspectsTable-radiated', 'style'),
    prevent_initial_call=True)

def minimize_suspectTable_radiated(n_clicks, style):
    return minimize_suspectTable(n_clicks, style)

def minimize_suspectTable(n_clicks, style):
    if n_clicks % 2 == 1:
        style['display'], children = 'block', 'Hide Suspect Table'
    else:
        style['display'], children = 'none', 'Show Suspect Table'
    return style, children

@app.callback(Output('emission_conducted_ground', "figure", allow_duplicate = True),
    Output('emission_conducted_supply', "figure", allow_duplicate = True),
    Output('emission_conducted_ground', 'relayoutData'),
    Output('emission_conducted_supply', 'relayoutData'),
    Output('emission_conducted_ground', 'style'),
    Output('emission_conducted_supply', 'style'),
    Output('loading-emission_ground', 'display'),
    Output('loading-emission_supply', 'display'),
    Output('cursor-list-ground','options'),
    Output('cursor-list-ground','value'),
    Output('cursor-list-supply','options'),
    Output('cursor-list-supply','value'),
    Output('activate-cursor-ground','on'),
    Output('activate-cursor-supply','on'),
    Output('cursor_data', 'data',allow_duplicate = True),
    Output('emission-conducted-voltage-tab','disabled'),
    Output('test-tabs','value', allow_duplicate=True),
    Output('markers-ground', 'data',allow_duplicate = True),
    Output('markers-supply','data', allow_duplicate = True),
    Output('cursor-output-ground', 'children', allow_duplicate = True),
    Output('cursor-output-supply', 'children', allow_duplicate = True),
    Output('Div_axes_param_ground', 'style'),
    Output('Div_axes_param_supply', 'style'),
    Output('limits-table-ground', 'rowData'),
    Output('line-table-ground', 'rowData'),
    Output('limits-table-supply', 'rowData'),
    Output('line-table-supply', 'rowData'),
    Output('limits-table-ground', 'selectedRows'),
    Output('limits-table-supply', 'selectedRows'),
    Output('line-table-container-ground', 'style', allow_duplicate=True),
    Output('line-table-btn-ground', 'children', allow_duplicate=True),
    Output('line-table-container-supply', 'style', allow_duplicate=True),
    Output('line-table-btn-supply', 'children', allow_duplicate=True),
    Output("conducted-btn",'disabled'),
    Input('selected-data-conducted', "data"),
    State('suspectsTable-conducted', 'rowData'),
    State("Test-table", "selectedRows"),
    State('emission_conducted_ground', 'figure'),
    State('emission_conducted_supply', 'figure'),
    State('emission_conducted_ground', 'style'),
    State('emission_conducted_supply', 'style'),
    State('loading-emission_ground', 'display'),
    State('loading-emission_supply', 'display'),
    State('xaxis-emission_ground', 'value'),
    State('xaxis-emission_supply', 'value'),
    State('cursor-list-ground','options'),
    State('cursor-list-ground','value'),
    State('cursor-list-supply', 'options'),
    State('cursor-list-supply', 'value'),
    State('emission-conducted-voltage-tab','disabled'),
    State('test-tabs','value'),
    State('cursor-output-ground', 'children'),
    State('limit-list','value'),
    State('Div_axes_param_ground', 'style'),
    State('Div_axes_param_supply', 'style'),
    State('markers-ground', 'data'),
    State('markers-supply', 'data'),
    State('rowData_tests', 'data'),
    State('limits-table-ground', 'rowData'),
    State('line-table-ground', 'rowData'),
    State('limits-table-supply', 'rowData'),
    State('line-table-supply', 'rowData'),
    State('line-table-container-ground', 'style'),
    State('line-table-btn-ground', 'children'),
    State('line-table-container-supply', 'style'),
    State('line-table-btn-supply', 'children'),
    State('cursor_data', 'data'),
    State('activate-cursor-ground', 'on'),
    State('activate-cursor-supply', 'on'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def emission_conducted(data, suspectsTable, selectedRows, figure_ground, figure_supply, style_ground, style_supply, loading_emission_ground, loading_emission_supply, log_ground, log_supply, cursor_options_ground, cursor_value_ground, cursor_options_supply, cursor_value_supply, emission_tab, test_tab, cursor_output, limit, Div_axes_param_ground, Div_axes_param_supply, markers_ground, markers_supply, rowData_tests, rowData_limit_ground, rowData_line_ground, rowData_limit_supply, rowData_line_supply, line_param_ground, btn_txt_ground, line_param_supply, btn_txt_supply, cursor_data, activate_cursor_ground, activate_cursor_supply):
    selectedRows_ground, selectedRows_supply = [], []
    if data != []:
        cursor_data = {'left': {}, 'right': {}}
        figure_ground['data'], figure_supply['data'] = [], []
        figure_ground['layout']['shapes'], figure_supply['layout']['shapes'] = [], []
        figure_ground['layout']['annotations'], figure_supply['layout']['annotations'] = [], []
        cursor_options_ground = []
        options = []
        cursor_output = f'ΔFrequency (MHz) = - \n ΔLevel (dBμV/m) = -'
        if activate_cursor_ground == False:
            activate_cursor_ground = no_update
        if activate_cursor_supply == False:
            activate_cursor_supply = no_update

        for row in data:
            if row['Polarization'] == 'Ground':
                figure = figure_ground
                cursor_options = cursor_options_ground
                cursor_value = cursor_value_ground
            else:
                figure = figure_supply
                cursor_options = cursor_options_supply
                cursor_value = cursor_value_supply
            meta = {'Name': '', 'Type': '', 'Detector': '', 'Bands': [], 'RBW': '', 'Color': '', 'Suspects': [], 'Limits': [], 'Cursors': []}
            figure, meta['Suspects'] = plot_suspect(row, figure)
            meta['Name'] = row["Test Name"] + '-' + row["Bands"] + '-' + row["RBW"] + '-' + row['Detector'].replace('Meas.','').replace(' (dBµV/m)','')
            meta['Type'] = 'Line'
            meta['Detector'] = row['Detector']
            meta['Bands'] = row["Bands"].split(',')
            meta['RBW'] = row["RBW"]
            meta['Color'] = [detector_to_color_gradient[row['Detector']][row['RBW']], 'Blue' if row['Detector'] == 'Peak' else 'Red' if row['Detector'] == 'QPeak' else 'Green' if row['Detector'] == 'AVG' else None]
            df = pd.read_json(row['Data'][0])
            color = detector_to_color_gradient[row['Detector']][row['RBW']]
            figure, meta = plot_limit(row, row['Limits'], meta, figure, row['Detector'], color, 'Level Start(dBµV)')
            figure['data'].append(dict(x=df.iloc[:, 0], y=df.iloc[:, 1], mode="lines",
                                                  name=row["Test Name"] + '-' + row["RBW"] + '-' + row['Detector'].replace('Meas.', '').replace(' (dBµV/m)', ''),
                                                  hoverinfo='none', showlegend=True, meta=meta, visible=True,
                                                  line=dict(color=color, dash='solid', width=1),
                                                  hovertemplate=f'<b>{row["Test Name"]} - {row["RBW"]} - {row["Detector"].replace("Meas.", "").replace(" (dBµV/m)", "")}</b><br>' + '<b>Frequency (MHz):</b> %{x:.2f}<br>' + '<b>Level (dBµV/m):</b> %{y:.2f} <extra></extra>'))
            cursor_options, cursor_value = set_cursor_list(figure)
            if row['Polarization'] == 'Ground':
                cursor_options_ground = cursor_options
                cursor_value_ground = cursor_value
            else:
                cursor_options_supply = cursor_options
                cursor_value_supply = cursor_value

        if markers_ground != []:
            name = []
            for trace in figure_ground['data']:
                name.append(trace['name'])
            new = []
            for marker in markers_ground:
                if marker['chart_name'] in name:
                    figure_ground['data'].append(marker['trace'])
                    figure_ground['layout']['annotations'].append(marker['annotation'])
                    new.append(marker)
            markers_ground = new
        if markers_supply != []:
            name = []
            for trace in figure_supply['data']:
                name.append(trace['name'])
            new = []
            for marker in markers_supply:
                if marker['chart_name'] in name:
                    figure_supply['data'].append(marker['trace'])
                    figure_supply['layout']['annotations'].append(marker['annotation'])
                    new.append(marker)
            markers_supply = new

        if figure_ground['data'] == []:
            style_ground['display'] = 'none'
            Div_axes_param_ground['display'] = 'none'
            loading_emission_ground = 'hide'
            btn_txt_ground = 'Show Line Display Parameters'
            line_param_ground['display'] = 'none'
        else:
            style_ground['display'] = 'block'
            Div_axes_param_ground['display'] = 'block'
            loading_emission_ground = 'auto'
            x_max, y_max, x_min, y_min = find_min_max(figure_ground)
            if log_ground =='log':
                x_min, x_max = math.log(x_min, 10), math.log(x_max, 10)
            figure_ground['layout']['xaxis']['range'] = (x_min, x_max)
            figure_ground['layout']['yaxis']['autorange'] = True
            figure_ground = set_color(figure_ground)
        if figure_supply['data'] == []:
            style_supply['display'] = 'none'
            Div_axes_param_supply['display'] = 'none'
            loading_emission_supply = 'hide'
            btn_txt_supply = 'Show Line Display Parameters'
            line_param_supply['display'] = 'none'
        else:
            style_supply['display'] = 'block'
            Div_axes_param_supply['display'] = 'block'
            loading_emission_supply = 'auto'
            x_max, y_max, x_min, y_min = find_min_max(figure_supply)
            if log_supply == 'log':
                x_min, x_max = math.log(x_min, 10), math.log(x_max, 10)
            figure_supply['layout']['xaxis']['range'] = (x_min, x_max)
            figure_supply['layout']['yaxis']['autorange'] = True
            figure_supply = set_color(figure_supply)

        figure_ground['layout']['xaxis']['type'] = log_ground
        figure_supply['layout']['xaxis']['type'] = log_supply
        if selectedRows and selectedRows[0]['Type'] == 'Conducted Voltage Emissions':
            test_tab = 'emission-conducted-voltage-tab'

        rowData_limit_ground, rowData_line_ground, selectedRows_ground = fill_line_table(figure_ground)
        rowData_limit_supply, rowData_line_supply, selectedRows_supply = fill_line_table(figure_supply)

    else:
        figure_ground['data'], figure_supply['data'] = [], []
        figure_ground['layout']['shapes'], figure_supply['layout']['shapes'] = [], []
        figure_ground['layout']['annotations'], figure_supply['layout']['annotations'] = [], []

    if figure_ground['data'] == [] and figure_supply['data'] == []:
        emission_tab = True
        conducted_btn = True
    else:
        emission_tab = False
        conducted_btn = False
    return figure_ground, figure_supply, {'autosize': True}, {'autosize': True}, style_ground, style_supply, loading_emission_ground, loading_emission_supply, cursor_options_ground, cursor_value_ground, cursor_options_supply, cursor_value_supply, activate_cursor_ground, activate_cursor_supply, cursor_data, emission_tab, test_tab, markers_ground, markers_supply, cursor_output, cursor_output, Div_axes_param_ground, Div_axes_param_supply, rowData_limit_ground, rowData_line_ground, rowData_limit_supply, rowData_line_supply, selectedRows_ground, selectedRows_supply, line_param_ground, btn_txt_ground, line_param_supply, btn_txt_supply, conducted_btn

def plot_suspect(row, figure):
    meta = []
    if row['Data'][1]:
        suspects = pd.read_json(row['Data'][1])
        for index, suspect in suspects.iterrows():
            dectector = suspect["Detector"]
            if dectector == 'CAVG':
                dectector = 'AVG'
            Frequency = suspect["Frequency (MHz)"]
            if Frequency.split(' ')[1] == 'kHz':
                Frequency = (float(Frequency.split(' ')[0])) / (10 ** 3)
            else:
                Frequency = float(Frequency.split(' ')[0])
            meta_suspect = {'Name': '', 'Type': ''}
            meta_suspect['Name'] = 'Suspect ' + row["Test Name"] + '-' + dectector + '-' + str(
                suspect['Scan']) + '-' + suspect['Band']
            meta_suspect['Type'] = 'Suspect'
            Suspect = dict(
                name='Suspect ' + row["Test Name"] + '-' + dectector + '-' + str(suspect['Scan']) + '-' +
                     suspect['Band'],
                x=[Frequency], y=[suspect["Meas.Value (dBµV/m)"]],
                mode='markers', showlegend=False, visible=True, meta=meta_suspect,
                marker=dict(color='orange', size=10, symbol="x"),
                hovertemplate=f'<b>Suspect {row["Test Name"]}</b><br>' + '<b>Frequency (MHz):</b> %{x:.2f}<br>' + '<b>Level (dBµV/m):</b> %{y:.2f} <extra></extra>')
            figure['data'].append(Suspect)
            meta.append('Suspect ' + row["Test Name"] + '-' + dectector + '-' + str(suspect['Scan']) + '-' +suspect["Band"])
    return figure, meta


# @app.callback(Input('emission_conducted_ground', 'figure'),
#     prevent_initial_call=True)
#
# def debug_figure(figure):
#     print('DEBUG FIGURE IMPORTANT')
#     print(figure)

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Input('limits-table-ground', 'selectedRows'),
    State('emission_conducted_ground', 'figure'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def display_limit_emission_conducted_ground(selectedRows, figure):

    return display_limit_tab(selectedRows, figure)

@app.callback(Output('emission_conducted_supply', 'figure', allow_duplicate = True),
    Input('limits-table-supply', 'selectedRows'),
    State('emission_conducted_supply', 'figure'),
    prevent_initial_call=True)

def display_limit_emission_conducted_supply(selectedRows, figure):
    return display_limit_tab (selectedRows, figure)

def display_limit_tab(selectedRows, figure):
    if selectedRows:
        limit_names = []
        for row in selectedRows:
            limit_names.append(row['meta']['Limits'])
        for trace in figure['data']:
            if trace['meta']['Type'] == 'Limit':
                if trace['name'] in limit_names:
                    trace['visible'] = True
                else:
                    trace['visible'] = False
        return figure
    else:
        raise PreventUpdate

@app.callback(Output('selected-data-conducted', "data"),
    Output('selected-data-radiated', "data"),
    Input("Test-table", "selectedRows"),
    Input('Remove-project', 'n_clicks'),
    State('selected-data-conducted', "data"),
    State('selected-data-radiated', "data"),
    State('rowData_tests', 'data'),
    State('rowData_scans', 'data'),
    State("Test-table", "columnDefs"),
    State("Test-table", "cellRendererData"),
    State('Project-list', 'value'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def selected_data(selectedRows, remove_project, selected_data_conducted, selected_data_radiated, rowData_tests, rowData_scans, columnDefs, btn_clicked, selected_project):
    triggered_id = ctx.triggered_id
    if triggered_id == 'Test-table' and rowData_scans and columnDefs != columnDefs_tests:
        if selectedRows == []:
            if list(rowData_scans[selected_project].values())[0][0]['Type'] == 'Conducted Voltage Emissions' and list(rowData_scans[selected_project].values())[btn_clicked['rowIndex']][0]['Test Name'] in [data['Test Name'] for data in list(selected_data_conducted)]:
                return add_selected_data(selectedRows, selected_data_conducted, 'Conducted Voltage Emissions'), no_update
            elif list(rowData_scans[selected_project].values())[0][0]['Type'] == 'Radiated Electric Emissions' and list(rowData_scans[selected_project].values())[btn_clicked['rowIndex']][0]['Test Name'] in [data['Test Name'] for data in list(selected_data_radiated)]:
                return no_update, add_selected_data(selectedRows, selected_data_radiated, 'Radiated Electric Emissions')
            else:
                raise PreventUpdate

        elif selectedRows == selected_data_conducted and list(rowData_scans[selected_project].values())[0][0]['Type'] == 'Conducted Voltage Emissions' or selectedRows == selected_data_radiated and list(rowData_scans[selected_project].values())[0][0]['Type'] == 'Radiated Electric Emissions':
            raise PreventUpdate
        else:
            if selectedRows and selectedRows[0]['Type'] == 'Conducted Voltage Emissions':
                return add_selected_data(selectedRows, selected_data_conducted, 'Conducted Voltage Emissions'), no_update
            elif selectedRows and selectedRows[0]['Type'] == 'Radiated Electric Emissions':
                return no_update, add_selected_data(selectedRows, selected_data_radiated, 'Radiated Electric Emissions')
            else:
                raise PreventUpdate
    elif triggered_id == 'Remove-project':
        names_test = [test['Test Name'] for test in rowData_tests[selected_project]]
        index_selected_data_conducted = [index for index, data in enumerate(selected_data_conducted) if data['Test Name'] in names_test and data['Type'] == 'Conducted Voltage Emissions']
        index_selected_data_radiated = [index for index, data in enumerate(selected_data_radiated) if data['Test Name'] in names_test and data['Type'] == 'Radiated Electric Emissions']
        if index_selected_data_conducted != []:
            selected_data_conducted = [i for j, i in enumerate(selected_data_conducted) if j not in index_selected_data_conducted]
        if index_selected_data_radiated != []:
            selected_data_radiated = [i for j, i in enumerate(selected_data_radiated) if j not in index_selected_data_radiated]
        if index_selected_data_conducted != [] and index_selected_data_radiated != []:
            return selected_data_conducted, selected_data_radiated
        elif index_selected_data_conducted != selected_data_conducted and index_selected_data_radiated == []:
            return selected_data_conducted, no_update
        elif index_selected_data_conducted == [] and index_selected_data_radiated != []:
            return no_update, selected_data_radiated
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate

def add_selected_data(selectedRows, selected_data, type):
    if selectedRows != []:
        test_name = selectedRows[0]['Test Name']
        for row in selectedRows:
            if row not in selected_data and row['Type'] == type:
                selected_data.append(row)
        for data in selected_data:
            if data not in selectedRows and data['Test Name'] == test_name and data['Type'] == type:
                selected_data.remove(data)
    else:
        selected_data =[]
    return selected_data

@app.callback(Output("Test-table", "columnDefs", allow_duplicate=True),
    Output("Test-table", "rowData", allow_duplicate=True),
    Output("Test-table", "selectedRows", allow_duplicate=True),
    Input("Test-table", "cellRendererData"),
    Input('hide-button', "data"),
    Input('Project-list', 'value'),
    State('rowData_tests', 'data'),
    State('rowData_scans', 'data'),
    State('selected-data-conducted', "data"),
    State('selected-data-radiated', "data"),
    prevent_initial_call=True)

def showChange(show_btn, hide_btn, selected_project, rowData_tests, rowData_scans, selected_data_conducted, selected_data_radiated):
    triggered_id = ctx.triggered_id
    if selected_project:
        if triggered_id == "Test-table":
            columnDefs, rowData = columnDefs_scans, rowData_scans[selected_project][rowData_tests[selected_project][show_btn['rowIndex']]['Test Name']]
            selectedRows = selected_data_conducted + selected_data_radiated
            return columnDefs, rowData, selectedRows
        elif triggered_id == 'hide-button' or triggered_id == 'Project-list':
            columnDefs, rowData = columnDefs_tests, rowData_tests[selected_project]
            selectedRows = []
            return columnDefs, rowData, selectedRows
    else:
        raise PreventUpdate

@app.callback(Output('project-loading-screen', 'children', allow_duplicate=True),
    Output('project-loading-screen', 'style', allow_duplicate=True),
    Input('load-project', 'contents'),
    Input('Remove-project', 'n_clicks'),
    State('project-loading-screen', 'style'),
    State('rowData_tests', 'data'),
    State('Project-list', 'value'),
    prevent_initial_call=True)

def toggle_loading(content_project, n_clicks, style, rowData_tests, value):
    triggered_id = ctx.triggered_id
    if triggered_id == 'load-project':
        style['backgroundColor'] = '#119DFF'
        children = [dbc.Spinner(size="sm"), "  Loading a new project"]
    elif triggered_id == 'Remove-project' and value is not None and len(rowData_tests) == 1:
        style['backgroundColor'] = '#119DFF'
        children = ['No loaded project']
    else:
        style['backgroundColor'] = 'red'
        children = [cross, '  Project update failed']
    return children, style

@app.callback(Output('Project-list', 'options'),
    Output('rowData_tests', 'data'),
    Output('rowData_scans', 'data'),
    Output('load-project', 'filename'),
    Output('project-loading-screen', 'children',allow_duplicate = True),
    Output('project-loading-screen', 'style',allow_duplicate = True),
    Input('load-project', 'filename'),
    Input('Remove-project', 'n_clicks'),
    State('load-project', 'contents'),
    State('Project-list', 'value'),
    State('Project-list', 'options'),
    State('rowData_tests', 'data'),
    State('rowData_scans', 'data'),
    State('project-loading-screen', 'style'),
    prevent_initial_call=True)

def update_Project_list(Project_path, remove_click, Project_content, value, options, rowData_tests, rowData_scans, style):
    try:
        triggered_id=ctx.triggered_id
        if triggered_id == 'load-project':
            return add_project(options,Project_path, Project_content, rowData_tests, rowData_scans, style)
        elif triggered_id == 'Remove-project' and value is not None:
            return remove_Project_list(value, options, rowData_tests, rowData_scans, style)
    except:
        style['backgroundColor'] = 'red'
        return options, rowData_tests, rowData_scans, None, [cross, '  Project update failed'], style

def add_project(options,Project_path, Project_content, rowData_tests, rowData_scans, style):
    if Project_path:
        Project_name = os.path.basename(Project_path).split('/')[-1]
        Project_name = '.'.join(Project_name.split('.')[:-1])
        if Project_name in options:
            style['backgroundColor'] = 'green'
            return options, rowData_tests, rowData_scans, None, [check, '  Project already loaded'], style
        Project_content = base64.b64decode(Project_content.split(',')[1])
        Project_content = zipfile.ZipFile(io.BytesIO(Project_content))
        rowdata_tests = []
        rowdata_scans_list_test = {}
        with tempfile.TemporaryDirectory() as upload_directory:
            Project_content.extractall(upload_directory)
            for root, dirs, files in os.walk(upload_directory):
                for file in files:
                    if file.endswith('xlsx') or file.endswith('xls') or file.endswith('csv'):
                        df = pd.read_excel(os.path.join(root, file), sheet_name = None)
                        test_name = file.split('.')[0]
                        test_type = df['Test Infos'].iloc[0]['Type']
                        limit = df['Test Infos'].iloc[0]['Limits']
                        freq_range = df['Scan Settings'].iloc[0]['Frequency Range'].replace('[', '').replace(']', '')
                        operation_mode = df['Test Infos'].iloc[0]['Operation Mode']
                        modification = df['Test Infos'].iloc[0]['Modification']
                        test_date = df['Test Infos'].iloc[0]['Date']
                        test_pass = df['Test Infos'].iloc[0]['Passed/Failed']
                        rowdata_tests.append({
                            "Show": ">>",
                            "Test Name": test_name,
                            "Type": test_type,
                            "Limits": limit,
                            "Frequency Range": freq_range,
                            "Operation Mode": operation_mode,
                            "Modification": modification,
                            "Date": test_date,
                            "Test_Pass": test_pass})
                        rowdata_scans_list = []
                        for i in range ((len(df['Scan Settings']))):
                            scan = int(df['Scan Settings'].iloc[i]['Scan'])
                            bands = df['Scan Settings'].iloc[i]['Bands']
                            freq_range = df['Scan Settings'].iloc[i]['Frequency Range'].replace('[','').replace(']','')
                            freq_step = df['Scan Settings'].iloc[i]['Frequency Step']
                            polarization = df['Scan Settings'].iloc[i]['Polarization']
                            bandwidth = df['Scan Settings'].iloc[i]['RBW']
                            meas_time = df['Scan Settings'].iloc[i]['Sweep Time']
                            detectors = df['Scan Settings'].iloc[i]['Detectors']
                            for detector in detectors.split(','):
                                if detector == 'Peak':
                                    col = 2
                                elif detector == 'QPeak':
                                    col = 4
                                elif detector == 'CAVG' or 'Average':
                                    col = 3
                                Data = [df['Data'][df['Data']['Scan'] == i + 1].iloc[:, [1, col]].to_json(),df['Suspects Table'][(df['Suspects Table']['Scan'] == scan) & (df['Suspects Table']['Band'].isin(bands.split(','))) & (df['Suspects Table']['Detector'] == detector) & (df['Suspects Table']['Polarization'] == polarization)].to_json()]
                                scan_pass = Scan_pass(pd.read_json(Data[1]))
                                if detector == 'CAVG' or detector == 'Average':
                                    detector = 'AVG'
                                rowdata_scans_list.append({
                                    "Hide": "Hide",
                                    "Selected": False,
                                    "Scan": scan,
                                    "Bands": bands,
                                    "Frequency Range": freq_range,
                                    "Frequency Step": freq_step,
                                    "Polarization": polarization,
                                    "RBW": bandwidth,
                                    "Meas Time": meas_time,
                                    "Detector": detector,
                                    "Test_Pass": scan_pass,
                                    "Test Name": test_name,
                                    "Type": test_type,
                                    "Limits": limit,
                                    "Data": Data})
                        rowdata_scans_list_test[test_name] = rowdata_scans_list
                    else:
                        style['backgroundColor'] = 'red'
                        return options, rowData_tests, rowData_scans, None, [cross,'  Project update failed'], style
        rowData_tests[Project_name] = rowdata_tests
        rowData_scans[Project_name] = rowdata_scans_list_test
        options.append(Project_name)
        style['backgroundColor'] = 'green'
    return options, rowData_tests, rowData_scans, None, [check, '  Project successfully loaded'], style

def remove_Project_list(value, options, rowData_tests, rowData_scans, style):
    new_options=[option for option in options if option != value]
    rowData_scans.pop(value)
    rowData_tests.pop(value)
    style['backgroundColor'] = 'green'
    return new_options, rowData_tests, rowData_scans, None, [check, '  Project successfully removed'], style

def Scan_pass(Data):
    Pass = 'Pass'
    for suspect in Data.iterrows():
        if suspect[1]['Pass/Fail'] == 'Fail':
            Pass = 'Fail'
            break
        elif suspect[1]['Pass/Fail'] == 'Inconclusive':
            Pass = 'Inconclusive'
    if Pass == 'Pass':
        Pass = 'PASSED'
    elif Pass == 'Fail':
        Pass = 'FAILED'
    elif Pass == 'Inconclusive':
        Pass = 'INCONCLUSIVE'
    return Pass

@app.callback(Output('limit_database', 'data'),
    Output('limit-list', 'options'),
    Output('limits-loading-screen', 'children'),
    Output('limits-loading-screen', 'style'),
    Output('load-limits', 'contents'),
    Input('load-limits', 'filename'),
    Input('load-limits', 'contents'),
    State('limit_database', 'data'),
    State('limit-list', 'options'),
    State('limits-loading-screen', 'style'),
    prevent_initial_call=True)

def load_limit(filename, content, limit_database, limit_list, style):
    try:
        style['backgroundColor'] = 'green'
        filename = filename.split('.')[0]
        for key in limit_list:
            if key == filename:
                return limit_database, limit_list, [check, '  Limits already loaded'], style, None
        content = content.split(',')[1]
        content = base64.b64decode(content)
        content = pd.read_csv(io.BytesIO(content), sep="\t")
        limit_list.append(filename)
        limit_database[filename] = content.to_json()
        return limit_database, limit_list, [check, '  Limits successfully loaded'], style, None
    except:
        style['backgroundColor'] = 'red'
        return limit_database, limit_list, [cross, '  Limits update failed'], style, None

@app.callback(Output('limit-list', 'value'),
    Output('limits-loading-screen', 'children', allow_duplicate = True),
    Output('limits-loading-screen', 'style', allow_duplicate = True),
    Input('Project-list', 'value'),
    State('limit-list', 'options'),
    State('limits-loading-screen', 'style'),
    State('rowData_tests', 'data'),
    prevent_initial_call=True)

def update_limit(project, limit_options, style, rowData_tests):
    if project is not None:
        for test in rowData_tests[project]:
            if test['Limits'] not in limit_options:
                style['backgroundColor'] = 'red'
                children = [cross, '  Limits not found']
                return None, children, style
        style['backgroundColor'] = 'green'
        children = [check, '  Limits successfully found']
        return rowData_tests[project][-1]['Limits'], children, style
    else:
        style['backgroundColor'] = '#119DFF'
        children = ['No limits selected']
        return None, children, style

@app.callback(Output('limit-list', 'value', allow_duplicate = True),
    Output('limits-loading-screen', 'children', allow_duplicate = True),
    Output('limits-loading-screen', 'style', allow_duplicate = True),
    Input('limit-list', 'value'),
    State('rowData_tests', 'data'),
    State('limits-loading-screen', 'children'),
    State('limits-loading-screen', 'style'),
    State('Project-list', 'value'),
    prevent_initial_call=True)

def check_limit(limit, rowData_tests, children, style, selected_project):
    if limit:
        if rowData_tests[selected_project][0]['Limits'] not in Limit_database.keys():
            style['backgroundColor'] = 'red'
            children = [cross, '  Not corresponding limits']
            return None, children, style
        else:
            return limit, children, style
    else:
        style['backgroundColor'] = '#119DFF'
        children = ['No limits selected']
        return limit, children, style

@app.callback(Output("Test-table", "columnDefs", allow_duplicate = True),
    Output('Test-table', 'rowData', allow_duplicate = True),
    Input('Project-list', 'value'),
    State('rowData_tests', 'data'),
    State("Test-table", "columnDefs"),
    prevent_initial_call=True)

def update_Test_table(project, test_data, columnDefs):
    if project:
        columnDefs, rowData = columnDefs_tests, test_data[project]
    else:
        columnDefs, rowData = columnDefs_tests, []
    return columnDefs, rowData

@app.callback(Output('emission_conducted_ground', 'figure',allow_duplicate = True),
    Output('emission_conducted_supply', 'figure',allow_duplicate = True),
    Input('suspectsTable-conducted', 'selectedRows'),

    State('suspectsTable-conducted', 'rowData'),
    State('emission_conducted_ground', 'figure'),
    State('emission_conducted_supply', 'figure'),
    prevent_initial_call=True)

def select_suspect_conducted(selectedRows, rowData, figure_ground, figure_supply):
    return select_suspect(selectedRows, rowData, figure_ground, figure_supply)

@app.callback(Output('emission_radiated_horizontal', 'figure',allow_duplicate = True),
    Output('emission_radiated_vertical', 'figure',allow_duplicate = True),
    Input('suspectsTable-radiated', 'selectedRows'),
    State('suspectsTable-radiated', 'rowData'),
    State('emission_radiated_horizontal', 'figure'),
    State('emission_radiated_vertical', 'figure'),
    prevent_initial_call=True)

def select_suspect_radiated(selectedRows, rowData, figure_horizontal, figure_vertical):
    return select_suspect(selectedRows, rowData, figure_horizontal, figure_vertical)

def select_suspect(selectedRows, rowData, figure_1, figure_2):
    if rowData:
        names_1 = []
        names_2 = []
        for suspect in selectedRows:
            if suspect["Polarization"] == 'Horizontal' or suspect["Polarization"] == 'Ground':
                names_1.append('Suspect ' + suspect["Test Name"] + '-' + suspect["Detector"]+ '-'+ str(suspect['Scan']) + '-'+ suspect['Band'])
            else:
                names_2.append('Suspect ' + suspect["Test Name"] + '-' + suspect["Detector"] + '-' + str(suspect['Scan']) + '-'+ suspect['Band'])
        figure = [figure_1, figure_2]
        names = [names_1, names_2]
        for i in range(2):
            if figure[i]['data'] != []:
                for trace in figure[i]['data']:
                    if trace['meta']['Type'] == 'Suspect':
                        if trace['name'] in names[i]:
                            trace['visible'] = True
                        else:
                            trace['visible'] = False
        return figure_1, figure_2
    else:
        raise PreventUpdate

@app.callback(Output('emission_radiated_horizontal', 'figure',allow_duplicate = True),
    Output('emission_radiated_vertical', 'figure',allow_duplicate = True),
    Output('emission_radiated_horizontal', 'style'),
    Output('emission_radiated_vertical', 'style'),
    Output('loading-emission_horizontal', 'display'),
    Output('loading-emission_vertical', 'display'),
    Output('cursor-list-h','options'),
    Output('cursor-list-h','value'),
    Output('cursor-list-v','options'),
    Output('cursor-list-v','value'),
    Output('activate-cursor-h','on'),
    Output('activate-cursor-v','on'),
    Output('left-cursor-h', 'data',allow_duplicate = True),
    Output('right-cursor-h', 'data',allow_duplicate = True),
    Output('left-cursor-v', 'data',allow_duplicate = True),
    Output('right-cursor-v', 'data',allow_duplicate = True),
    Output('emission-radiated-electric-tab','disabled'),
    Output('test-tabs','value'),
    Output('markers-h', 'data',allow_duplicate = True),
    Output('markers-v','data', allow_duplicate = True),
    Output('cursor-output-h', 'children', allow_duplicate = True),
    Output('cursor-output-v', 'children', allow_duplicate = True),
    Output('Div_axes_param_h', 'style'),
    Output('Div_axes_param_v', 'style'),
    Output('limits-table-h', 'rowData'),
    Output('line-table-h', 'rowData'),
    Output('limits-table-v', 'rowData'),
    Output('line-table-v', 'rowData'),
    Output('limits-table-h', 'selectedRows'),
    Output('limits-table-v', 'selectedRows'),
    Output('line-table-container-h', 'style', allow_duplicate=True),
    Output('line-table-btn-h', 'children', allow_duplicate=True),
    Output('line-table-container-v', 'style', allow_duplicate=True),
    Output('line-table-btn-v', 'children', allow_duplicate=True),
    Output("radiated-btn",'disabled'),
    Input('suspectsTable-radiated', 'rowData'),
    State('selected-data-radiated', "data"),
    State('Test-table', 'selectedRows'),
    State('emission_radiated_horizontal', 'figure'),
    State('emission_radiated_vertical', 'figure'),
    State('emission_radiated_horizontal', 'style'),
    State('emission_radiated_vertical', 'style'),
    State('loading-emission_horizontal', 'display'),
    State('loading-emission_vertical', 'display'),
    State('xaxis-emission_h', 'value'),
    State('xaxis-emission_v', 'value'),
    State('colors', 'data'),
    State('cursor-list-h','options'),
    State('cursor-list-h','value'),
    State('cursor-list-v', 'options'),
    State('cursor-list-v', 'value'),
    State('emission-radiated-electric-tab','disabled'),
    State('test-tabs','value'),
    State('cursor-output-h', 'children'),
    State('limit-list','value'),
    State('Div_axes_param_h', 'style'),
    State('Div_axes_param_v', 'style'),
    State('markers-h', 'data'),
    State('markers-v', 'data'),
    State('rowData_tests', 'data'),
    State('limits-table-h', 'rowData'),
    State('line-table-h', 'rowData'),
    State('limits-table-v', 'rowData'),
    State('line-table-v', 'rowData'),
    State('line-table-container-h', 'style'),
    State('line-table-btn-h', 'children'),
    State('line-table-container-v', 'style'),
    State('line-table-btn-v', 'children'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def emission_charts(suspectsTable, data, selectedRows, figure_horizontal, figure_vertical, style_horizontal, style_vertical, loading_emission_horizontal, loading_emission_vertical, log_h, log_v, colors, cursor_options_h, cursor_value_h, cursor_options_v, cursor_value_v, emission_tab, test_tab, cursor_output, limit, Div_axes_param_h, Div_axes_param_v, markers_h, markers_v, rowData_tests, rowData_limit_h, rowData_line_h, rowData_limit_v, rowData_line_v, line_param_h, btn_txt_h, line_param_v, btn_txt_v):
    selectedRows_h, selectedRows_v = [], []
    if data != []:
        figure_horizontal['data'], figure_vertical['data'] = [], []
        figure_horizontal['layout']['shapes'], figure_vertical['layout']['shapes'] = [], []
        figure_horizontal['layout']['annotations'], figure_vertical['layout']['annotations'] = [], []
        options = []
        cursor_output = f'ΔFrequency (MHz) = - \n ΔLevel (dBμV/m) = -'
        if suspectsTable != []:
            for suspect in suspectsTable:
                meta_suspect = {'Name': '', 'Type': ''}
                meta_suspect['Name'] = 'Suspect ' + suspect["Test Name"] + '-' + suspect["Detector"]+ '-'+ str(suspect['Scan']) + '-'+ suspect['Band']
                meta_suspect['Type'] = 'Suspect'
                Suspect = dict(name='Suspect ' + suspect["Test Name"] + '-' + suspect["Detector"]+ '-'+ str(suspect['Scan']) + '-'+ suspect['Band'],
                               x=[suspect["Frequency"]], y=[suspect["MeasValue"]],
                               mode='markers', showlegend=False, visible = True,
                               marker=dict(color='orange', size=10, symbol="x"), meta = meta_suspect,
                               hovertemplate=f'<b>Suspect {suspect["Test Name"]}</b><br>' + '<b>Frequency (MHz):</b> %{x:.2f}<br>' + '<b>Level (dBµV/m):</b> %{y:.2f} <extra></extra>')
                if suspect['Polarization'] == 'Horizontal':
                    figure_horizontal['data'].append(Suspect)
                if suspect['Polarization'] == 'Vertical':
                    figure_vertical['data'].append(Suspect)
        names_h = []
        names_v = []
        for row in data:
            if row['Polarization'] == 'Horizontal':
                figure = figure_horizontal
                cursor_options = cursor_options_h
                cursor_value = cursor_value_h
            else:
                figure = figure_vertical
                cursor_options = cursor_options_v
                cursor_value = cursor_value_v
            meta = {'Name': '', 'Type': '', 'Detector': '', 'Bands': [], 'RBW': '', 'Color': '', 'Suspects': [], 'Limits': [], 'Cursors': []}
            meta['Name'] = row["Test Name"] + '-' + row["Bands"] + '-' + row["RBW"] + '-' + row['Detector'].replace('Meas.','').replace(' (dBµV/m)','')
            meta['Type'] = 'Line'
            meta['Detector'] = row["Detector"]
            meta['Bands'] = row["Bands"].split(',')
            meta['RBW'] = row["RBW"]
            meta['Color'] = [detector_to_color_gradient[row['Detector']][row['RBW']], 'Blue' if row['Detector'] == 'Peak' else 'Red' if row['Detector'] == 'QPeak' else 'Green' if row['Detector'] == 'AVG' else None]
            df = pd.read_json(row['Data'][0])
            if row['Data'][1] != []:
                suspects = pd.read_json(row['Data'][1])
                for index, suspect in suspects.iterrows():
                    meta['Suspects'].append(
                        'Suspect ' + row["Test Name"] + '-' + suspect["Detector"] + '-' + str(suspect['Scan']) + '-' +
                        suspect["Band"])
            color = detector_to_color_gradient[row['Detector']][row['RBW']]
            figure, meta = plot_limit(row, row['Limits'], meta, figure, row['Detector'], color, 'Level Start(dBµV/m)')
            figure['data'].append(dict(x=df.iloc[:, 0], y=df.iloc[:, 1], mode="lines",
                                       name=row["Test Name"] + '-' + row["RBW"] + '-' + row['Detector'].replace('Meas.', '').replace(' (dBµV/m)', ''),
                                       hoverinfo='none', showlegend=True, meta=meta, visible=True,
                                       line=dict(color=color, dash='solid', width=1),
                                       hovertemplate=f'<b>{row["Test Name"]} - {row["RBW"]} - {row["Detector"].replace("Meas.", "").replace(" (dBµV/m)", "")}</b><br>' + '<b>Frequency (MHz):</b> %{x:.2f}<br>' + '<b>Level (dBµV/m):</b> %{y:.2f} <extra></extra>'))
            cursor_options, cursor_value = set_cursor_list(figure)
            if row['Polarization'] == 'Horizontal':
                cursor_options_h = cursor_options
                cursor_value_h = cursor_value
            else:
                cursor_options_v = cursor_options
                cursor_value_v = cursor_value

        if markers_h != []:
            name = []
            for trace in figure_horizontal['data']:
                name.append(trace['name'])
            new = []
            for marker in markers_h:
                if marker['chart_name'] in name:
                    figure_horizontal['data'].append(marker['trace'])
                    figure_horizontal['layout']['annotations'].append(marker['annotation'])
                    new.append(marker)
            markers_h = new
        if markers_v != []:
            name = []
            for trace in figure_vertical['data']:
                name.append(trace['name'])
            new = []
            for marker in markers_v:
                if marker['chart_name'] in name:
                    figure_vertical['data'].append(marker['trace'])
                    figure_vertical['layout']['annotations'].append(marker['annotation'])
                    new.append(marker)
            markers_v = new

        if figure_horizontal['data'] == []:
            style_horizontal['display'] = 'none'
            Div_axes_param_h['display'] = 'none'
            loading_emission_horizontal = 'hide'
            btn_txt_h = 'Show Line Display Parameters'
            line_param_h['display'] = 'none'
        else:
            style_horizontal['display'] = 'block'
            Div_axes_param_h['display'] = 'block'
            loading_emission_horizontal = 'auto'
            x_max, y_max, x_min, y_min = find_min_max(figure_horizontal)
            if log_h == 'log':
                x_min, x_max = math.log(x_min, 10), math.log(x_max, 10)
            figure_horizontal['layout']['xaxis']['range'] = (x_min, x_max)
            figure_horizontal['layout']['yaxis']['autorange'] = True
            figure_horizontal = set_color(figure_horizontal)
        if figure_vertical['data'] == []:
            style_vertical['display'] = 'none'
            Div_axes_param_v['display'] = 'none'
            loading_emission_vertical = 'hide'
            btn_txt_v = 'Show Line Display Parameters'
            line_param_v['display'] = 'none'
        else:
            style_vertical['display'] = 'block'
            Div_axes_param_v['display'] = 'block'
            loading_emission_vertical = 'auto'
            x_max, y_max, x_min, y_min = find_min_max(figure_vertical)
            if log_v == 'log':
                x_min, x_max = math.log(x_min, 10), math.log(x_max, 10)
            figure_vertical['layout']['xaxis']['range'] = (x_min, x_max)
            figure_vertical['layout']['yaxis']['autorange'] = True
            figure_vertical = set_color(figure_vertical)

        figure_horizontal['layout']['xaxis']['type'] = log_h
        figure_vertical['layout']['xaxis']['type'] = log_v
        if selectedRows and selectedRows[0]['Type'] == 'Radiated Electric Emissions':
            test_tab = 'emission-radiated-electric-tab'

        rowData_limit_h, rowData_line_h, selectedRows_h = fill_line_table(figure_horizontal)
        rowData_limit_v, rowData_line_v, selectedRows_v = fill_line_table(figure_vertical)

    else:
        figure_horizontal['data'], figure_vertical['data'] = [], []
        figure_horizontal['layout']['shapes'], figure_vertical['layout']['shapes'] = [], []
        figure_horizontal['layout']['annotations'], figure_vertical['layout']['annotations'] = [], []

    if figure_horizontal['data'] == [] and figure_vertical['data'] == []:
        emission_tab = True
        radiated_btn = True
    else:
        emission_tab = False
        radiated_btn = False

    return figure_horizontal, figure_vertical, style_horizontal, style_vertical, loading_emission_horizontal, loading_emission_vertical, cursor_options_h, cursor_value_h, cursor_options_v, cursor_value_v, False, False, None, None, None, None, emission_tab, test_tab, markers_h, markers_v, cursor_output, cursor_output, Div_axes_param_h, Div_axes_param_v, rowData_limit_h, rowData_line_h, rowData_limit_v, rowData_line_v, selectedRows_h, selectedRows_v, line_param_h, btn_txt_h, line_param_v, btn_txt_v, radiated_btn
def plot_limit(row, limit_name, meta, figure, detector, color, level_name):
    band_index = []
    limit = Limit_database[limit_name]
    if detector == 'Peak':
        L_detector = ['Peak']
    elif detector == 'QPeak':
        L_detector = ['QPeak']
    else:
        L_detector = ['CISPR_Avg', 'Average']
    for band in row['Bands'].split(','):
        band_index.append([i for i, n in enumerate(limit['BandName']) if n == band])
    for i in band_index:
        for j in i:
            if limit['Detector'][j] in L_detector:
                freq_start = float(limit['F Start(MHz)'][j])
                freq_stop = float(limit['F Stop(MHz)'][j])
                level_start = float(limit[level_name][j])
                level_stop = float(limit[level_name.replace('Start', 'Stop')][j])
                meta_lim = {'Name': '', 'Type': ''}
                meta_lim['Name'] = 'Limit ' + limit_name + '-' + row["Test Name"] + '-'+ limit['BandName'][j] + '-' + detector.replace('Meas.','').replace(' (dBµV/m)','')
                meta_lim['Type'] = 'Limit'
                figure['data'].append(go.Scatter(x=[freq_start, freq_start, freq_stop, freq_stop], y=[level_start-0.15, level_start+0.15, level_stop+0.15, level_stop-0.15], name='Limit ' + limit_name + '-' + row["Test Name"] + '-'+ limit['BandName'][j] + '-'+ detector.replace('Meas.','').replace(' (dBµV/m)',''), showlegend=False, visible=True,  fill="toself", mode='text', fillcolor=color,
                                                 hovertemplate='', hoverinfo='text', text=None, meta = meta_lim))
                meta['Limits'].append('Limit ' + limit_name + '-' + row["Test Name"] + '-'+ limit['BandName'][j] + '-' + detector.replace('Meas.','').replace(' (dBµV/m)',''))
                break
    return figure, meta

def set_cursor_list(figure):
    cursor_options = []
    cursor_value = None
    for trace in figure['data']:
        if 'Suspect' not in trace['name'] and 'Limit' not in trace['name'] and 'Marker' not in trace['name']:
            cursor_options.append(trace['meta']['Name'])
    if cursor_options != []:
        cursor_value = cursor_options[0]
    return cursor_options, cursor_value

def set_color(figure):
    color_to_color_gradient = {'Blue': {}, 'Orange': {}, 'Green': {}, 'Red': {}, 'Purple': {}, 'Brown': {}, 'Pink': {},
                               'Gray': {}, 'Light green': {}, 'Light blue': {}}
    for index, trace in enumerate(figure['data']):
        if 'Limit' not in trace['name'] and 'Suspect' not in trace['name']:
            if trace['meta']['Color'][0] in color_to_color_gradient[trace['meta']['Color'][1]]:
                color_to_color_gradient[trace['meta']['Color'][1]][trace['meta']['Color'][0]].append(index)
            else:
                color_to_color_gradient[trace['meta']['Color'][1]][trace['meta']['Color'][0]] = [index]

    key_index = []
    for color, list_color in color_to_color_gradient.items():
        val = returnSum(list_color)
        if len(val) > 1:
            for item_init in val:
                for item in val:
                    if item_init != item:
                        if len(set(figure['data'][item_init]['x']) & set(figure['data'][item]['x'])) > 1:
                            key_index.append(item_init)
                            key_index.append(item)
                            break

            if key_index != []:
                key_index = list(dict.fromkeys(key_index))
                color_codes = generate_gradient(len(key_index), Gradient[color])
                for index, key in enumerate(key_index):
                    figure['data'][key]['line']['color'] = color_codes[index]
                    figure['data'][key]['meta']['Color'][0] = color_codes[index]
                    for trace in figure['data']:
                        if trace['name'] in figure['data'][key]['meta']['Limits']:
                            trace['fillcolor'] = color_codes[index]
    return figure

def generate_gradient(n, color):
    from matplotlib import cm
    color = cm.get_cmap(color)
    return [f'rgb({r*255:.0f},{g*255:.0f},{b*255:.0f})' for r, g, b, a in color(np.linspace(0.5, 0.9, n))]

def fill_line_table(figure):
    rowData_limit = []
    rowData_line = []
    selectedRows = {"ids":[]}
    if figure:
        for trace in figure['data']:
            name = trace['meta']['Name']
            if trace['meta']['Type'] == 'Limit':
                rowData_limit.append({
                            'Name': name,
                            'disabled': 'False'})
            elif trace['meta']['Type'] == 'Line':
                color = 'Blue' if trace['meta']['Detector'] == 'Peak' else 'Red' if trace['meta']['Detector'] == 'QPeak' else 'Green' if trace['meta']['Detector'] == 'AVG' else None
                rowData_line.append({
                            'Name':name,
                            'Color':color,
                            'Width':1,
                            'Type':'solid'})
        for i in range(len(rowData_limit)):
            selectedRows['ids'].append(str(i))
    return rowData_limit, rowData_line, selectedRows

@app.callback(Output('emission_radiated_horizontal', 'figure', allow_duplicate = True),
    Input('limits-table-h', 'selectedRows'),
    State('emission_radiated_horizontal', 'figure'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def display_limit_h(selectedRows, figure):
    return display_limit_tab (selectedRows, figure)

@app.callback(Output('emission_radiated_vertical', 'figure', allow_duplicate = True),
    Input('limits-table-v', 'selectedRows'),
    State('emission_radiated_vertical', 'figure'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def display_limit_v(selectedRows, figure):
    return display_limit_tab (selectedRows, figure)

def display_limit_tab(selectedRows, figure):
    if 'ids' not in selectedRows:
        names = []
        for row in selectedRows:
            names.append(row['Name'])
        for trace in figure['data']:
            if trace['meta']['Type'] == 'Limit':
                if trace['name'] in names:
                    trace['visible'] = True
                else:
                    trace['visible'] = False
    return figure

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Input('line-table-ground', 'cellValueChanged'),
    State('emission_conducted_ground', 'figure'),
    State('line-table-ground', 'virtualRowData'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def update_line_ground(cell, figure, line_table):
    return update_line(cell, figure, line_table)

@app.callback(Output('emission_conducted_supply', 'figure', allow_duplicate = True),
    Input('line-table-supply', 'cellValueChanged'),
    State('emission_conducted_supply', 'figure'),
    State('line-table-supply', 'virtualRowData'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def update_line_supply(cell, figure, line_table):
    return update_line(cell, figure, line_table)

@app.callback(Output('emission_radiated_horizontal', 'figure', allow_duplicate = True),
    Input('line-table-h', 'cellValueChanged'),
    State('emission_radiated_horizontal', 'figure'),
    State('line-table-h', 'virtualRowData'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def update_line_h(cell, figure, line_table):
    return update_line(cell, figure, line_table)

@app.callback(Output('emission_radiated_vertical', 'figure', allow_duplicate = True),
    Input('line-table-v', 'cellValueChanged'),
    State('emission_radiated_vertical', 'figure'),
    State('line-table-v', 'virtualRowData'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def update_line_v(cell, figure, line_table):
    return update_line(cell, figure, line_table)

def update_line(cell, figure, line_table):
    row = cell[0]['data']
    for trace in figure['data']:
        if trace['meta']['Name'] == row['Name']:
            Color = trace['line']['color']
            color_list = generate_gradient(3, Gradient[row['Color']])
            trace['line']['color'] = color_list[0] if trace['meta']['RBW'] == '9 kHz' else color_list[1] if trace['meta']['RBW'] == '120 kHz' or  trace['meta']['RBW'] == '200 kHz' else color_list[2] if trace['meta']['RBW'] == '1 MHz' else None
            trace['meta']['Color'] = [trace['line']['color'], row['Color']]
            trace['line']['width'] = row['Width']
            trace['line']['dash'] = row['Type']
            for trace_2 in figure['data']:
                if trace_2['name'] in trace['meta']['Limits']:
                    trace_2['fillcolor'] = trace['line']['color']
            set_color(figure)
            if 'shapes' in figure['layout'] and 'annotations' in figure['layout']:
                for i in range(len(figure['layout']['shapes'])):
                    if figure['layout']['shapes'][i]['line']['color'] == Color:
                        figure['layout']['shapes'][i]['line']['color'] = trace['line']['color']
                        for j in range(len(figure['layout']['annotations'])):
                            if figure['layout']['shapes'][i]['name'] == figure['layout']['annotations'][j]['name']:
                                figure['layout']['annotations'][j]['bgcolor'] = trace['line']['color']
            figure['data'][figure['data'].index(trace)] = trace
            emphasize_chart(line_table, figure)

    return figure

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Input('xaxis-emission_ground', 'value'),
    State('emission_conducted_ground', 'figure'),
    State('Test-table', 'selectedRows'),
    State('input_x_min-emission_ground', 'value'),
    State('input_x_max-emission_ground', 'value'),
    prevent_initial_call=True)

def figure_ground_param(option, figure, value, input_x_min, input_x_max):
    if value and figure['data'] != []:
        figure = figure_param(option, figure, input_x_min, input_x_max)
        return figure
    else:
        raise PreventUpdate

@app.callback(Output('emission_conducted_supply', 'figure',allow_duplicate = True),
    Input('xaxis-emission_supply', 'value'),
    State('emission_conducted_supply', 'figure'),
    State('Test-table', 'selectedRows'),
    State('input_x_min-emission_supply', 'value'),
    State('input_x_max-emission_supply', 'value'),
    prevent_initial_call=True)

def figure_supply_param(option, figure, value, input_x_min, input_x_max):
    if value:
        if figure['data'] != []:
            figure = figure_param(option, figure, input_x_min, input_x_max)
    return figure

@app.callback(Output('emission_radiated_horizontal', 'figure',allow_duplicate = True),
    Input('xaxis-emission_h', 'value'),
    State('emission_radiated_horizontal', 'figure'),
    State('Test-table', 'selectedRows'),
    State('input_x_min-emission_h', 'value'),
    State('input_x_max-emission_h', 'value'),
    prevent_initial_call=True)

def figure_horizontal_param(option, figure, value, input_x_min, input_x_max):
    if value:
        if figure['data'] != []:
            figure = figure_param(option, figure, input_x_min, input_x_max)
    return figure

@app.callback(Output('emission_radiated_vertical', 'figure',allow_duplicate = True),
    Input('xaxis-emission_v', 'value'),
    State('emission_radiated_vertical', 'figure'),
    State('Test-table', 'selectedRows'),
    State('input_x_min-emission_v', 'value'),
    State('input_x_max-emission_v', 'value'),
    prevent_initial_call=True)

def figure_vertical_param(option, figure, value, input_x_min, input_x_max):
    if value:
        if figure['data'] != []:
            figure = figure_param(option, figure, input_x_min, input_x_max)
    return figure

def figure_param(option, figure, input_x_min, input_x_max):
    if option == 'linear':
        figure['layout']['xaxis']['type'] = option
        figure['layout']['xaxis']['range'] = (input_x_min, input_x_max)
        if 'annotations' in figure['layout']:
            for i in range(len(figure['layout']['annotations'])):
                figure['layout']['annotations'][i]['x'] = 10 ** figure['layout']['annotations'][i]['x']
    else:
        figure['layout']['xaxis']['range'] = math.log(input_x_min, 10), math.log(input_x_max, 10)
        figure['layout']['xaxis']['type'] = option
        if 'annotations' in figure['layout']:
            for i in range(len(figure['layout']['annotations'])):
                figure['layout']['annotations'][i]['x']=math.log(figure['layout']['annotations'][i]['x'], 10)
    return figure

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Output('emission_conducted_ground', 'relayoutData', allow_duplicate = True),
    Output('input_x_min-emission_ground', 'value', allow_duplicate = True),
    Output('input_x_max-emission_ground', 'value', allow_duplicate = True),
    Output('input_y_min-emission_ground', 'value', allow_duplicate = True),
    Output('input_y_max-emission_ground', 'value', allow_duplicate = True),
    Input('emission_conducted_ground', 'relayoutData'),
    Input('input_x_min-emission_ground', 'n_blur'),
    Input('input_x_max-emission_ground', 'n_blur'),
    Input('input_y_min-emission_ground', 'n_blur'),
    Input('input_y_max-emission_ground', 'n_blur'),
    Input('input_x_min-emission_ground', 'n_submit'),
    Input('input_x_max-emission_ground', 'n_submit'),
    Input('input_y_min-emission_ground', 'n_submit'),
    Input('input_y_max-emission_ground', 'n_submit'),
    State('input_x_min-emission_ground', 'value'),
    State('input_x_max-emission_ground', 'value'),
    State('input_y_min-emission_ground', 'value'),
    State('input_y_max-emission_ground', 'value'),
    State('emission_conducted_ground', 'figure'),
    State('xaxis-emission_ground', 'value'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def ground_axes_param (relayoutData, n_blur_x_min, n_blur_x_max, n_blur_y_min, n_blur_y_max, n_submit_x_min, n_submit_x_max, n_submit_y_min, n_submit_y_max, x_min, x_max, y_min, y_max, figure, log):
    return axes_param (relayoutData, x_min, x_max, y_min, y_max, figure, log)

@app.callback(Output('emission_conducted_supply', 'figure', allow_duplicate = True),
    Output('emission_conducted_supply', 'relayoutData', allow_duplicate = True),
    Output('input_x_min-emission_supply', 'value', allow_duplicate = True),
    Output('input_x_max-emission_supply', 'value', allow_duplicate = True),
    Output('input_y_min-emission_supply', 'value', allow_duplicate = True),
    Output('input_y_max-emission_supply', 'value', allow_duplicate = True),
    Input('emission_conducted_supply', 'relayoutData'),
    Input('input_x_min-emission_supply', 'n_blur'),
    Input('input_x_max-emission_supply', 'n_blur'),
    Input('input_y_min-emission_supply', 'n_blur'),
    Input('input_y_max-emission_supply', 'n_blur'),
    Input('input_x_min-emission_supply', 'n_submit'),
    Input('input_x_max-emission_supply', 'n_submit'),
    Input('input_y_min-emission_supply', 'n_submit'),
    Input('input_y_max-emission_supply', 'n_submit'),
    State('input_x_min-emission_supply', 'value'),
    State('input_x_max-emission_supply', 'value'),
    State('input_y_min-emission_supply', 'value'),
    State('input_y_max-emission_supply', 'value'),
    State('emission_conducted_supply', 'figure'),
    State('xaxis-emission_supply', 'value'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def supply_axes_param (relayoutData, n_blur_x_min, n_blur_x_max, n_blur_y_min, n_blur_y_max, n_submit_x_min, n_submit_x_max, n_submit_y_min, n_submit_y_max, x_min, x_max, y_min, y_max, figure, log):
    return axes_param(relayoutData, x_min, x_max, y_min, y_max, figure, log)

@app.callback(Output('emission_radiated_horizontal', 'figure', allow_duplicate = True),
    Output('emission_radiated_horizontal', 'relayoutData', allow_duplicate = True),
    Output('input_x_min-emission_h', 'value', allow_duplicate = True),
    Output('input_x_max-emission_h', 'value', allow_duplicate = True),
    Output('input_y_min-emission_h', 'value', allow_duplicate = True),
    Output('input_y_max-emission_h', 'value', allow_duplicate = True),
    Input('emission_radiated_horizontal', 'relayoutData'),
    Input('input_x_min-emission_h', 'n_blur'),
    Input('input_x_max-emission_h', 'n_blur'),
    Input('input_y_min-emission_h', 'n_blur'),
    Input('input_y_max-emission_h', 'n_blur'),
    Input('input_x_min-emission_h', 'n_submit'),
    Input('input_x_max-emission_h', 'n_submit'),
    Input('input_y_min-emission_h', 'n_submit'),
    Input('input_y_max-emission_h', 'n_submit'),
    State('input_x_min-emission_h', 'value'),
    State('input_x_max-emission_h', 'value'),
    State('input_y_min-emission_h', 'value'),
    State('input_y_max-emission_h', 'value'),
    State('emission_radiated_horizontal', 'figure'),
    State('xaxis-emission_h', 'value'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def horizontal_axes_param (relayoutData, n_blur_x_min, n_blur_x_max, n_blur_y_min, n_blur_y_max, n_submit_x_min, n_submit_x_max, n_submit_y_min, n_submit_y_max, x_min, x_max, y_min, y_max, figure, log):
    return axes_param(relayoutData, x_min, x_max, y_min, y_max, figure, log)

@app.callback(Output('emission_radiated_vertical', 'figure', allow_duplicate = True),
    Output('emission_radiated_vertical', 'relayoutData', allow_duplicate = True),
    Output('input_x_min-emission_v', 'value', allow_duplicate = True),
    Output('input_x_max-emission_v', 'value', allow_duplicate = True),
    Output('input_y_min-emission_v', 'value', allow_duplicate = True),
    Output('input_y_max-emission_v', 'value', allow_duplicate = True),
    Input('emission_radiated_vertical', 'relayoutData'),
    Input('input_x_min-emission_v', 'n_blur'),
    Input('input_x_max-emission_v', 'n_blur'),
    Input('input_y_min-emission_v', 'n_blur'),
    Input('input_y_max-emission_v', 'n_blur'),
    Input('input_x_min-emission_v', 'n_submit'),
    Input('input_x_max-emission_v', 'n_submit'),
    Input('input_y_min-emission_v', 'n_submit'),
    Input('input_y_max-emission_v', 'n_submit'),
    Input('input_x_min-emission_v', 'value'),
    Input('input_x_max-emission_v', 'value'),
    Input('input_y_min-emission_v', 'value'),
    Input('input_y_max-emission_v', 'value'),
    State('emission_radiated_vertical', 'figure'),
    State('xaxis-emission_v', 'value'),
    prevent_initial_call=True,
    cancel=[Input("Test-table", "selectedRows")])

def vertical_axes_param (relayoutData, n_blur_x_min, n_blur_x_max, n_blur_y_min, n_blur_y_max, n_submit_x_min, n_submit_x_max, n_submit_y_min, n_submit_y_max, x_min, x_max, y_min, y_max, figure, log):
    return axes_param(relayoutData, x_min, x_max, y_min, y_max, figure, log)

def axes_param (relayoutData, x_min, x_max, y_min, y_max, figure, log):
    triggered_id = ctx.triggered_id
    if figure['data'] != [] and triggered_id == 'input_x_min-emission_h' or triggered_id == 'input_x_max-emission_h' or triggered_id == 'input_y_min-emission_h' or triggered_id == 'input_y_max-emission_h' or triggered_id == 'input_x_min-emission_v' or triggered_id == 'input_x_max-emission_v' or triggered_id == 'input_y_min-emission_v' or triggered_id == 'input_y_max-emission_v' or triggered_id == 'input_x_min-emission_ground' or triggered_id == 'input_x_max-emission_ground' or triggered_id == 'input_y_min-emission_ground' or triggered_id == 'input_y_max-emission_ground' or triggered_id == 'input_x_min-emission_supply' or triggered_id == 'input_x_max-emission_supply' or triggered_id == 'input_y_min-emission_supply' or triggered_id == 'input_y_max-emission_supply' or relayoutData and 'annotations' not in list(relayoutData.keys())[0]:
        if relayoutData and 'yaxis.autorange' in list(relayoutData.keys()) or relayoutData and 'autosize' in list(relayoutData.keys())[0]:
            x_max, y_max, x_min, y_min = find_min_max(figure)
            if log == 'log':
                x_min, x_max = math.log(x_min,10), math.log(x_max,10)
            figure['layout']['xaxis']['range'] = (x_min, x_max)
            if log == 'log':
                x_min = 10 ** x_min
                x_max = 10 ** x_max
            y_min, y_max = figure['layout']['yaxis']['range']
            x_min, x_max, y_min, y_max = round(x_min, 2), round(x_max, 2), round(y_min, 2), round(y_max, 2)

        elif triggered_id == 'emission_radiated_horizontal' or triggered_id == 'emission_radiated_vertical' or triggered_id == 'emission_conducted_ground' or triggered_id == 'emission_conducted_supply':
            figure, x_min, x_max, y_min, y_max = get_axes_range(figure, log, relayoutData)

        elif triggered_id == 'input_x_min-emission_h' or triggered_id == 'input_x_max-emission_h' or triggered_id == 'input_y_min-emission_h' or triggered_id == 'input_y_max-emission_h' or triggered_id == 'input_x_min-emission_v' or triggered_id == 'input_x_max-emission_v' or triggered_id == 'input_y_min-emission_v' or triggered_id == 'input_y_max-emission_v' or triggered_id == 'input_x_min-emission_ground' or triggered_id == 'input_x_max-emission_ground' or triggered_id == 'input_y_min-emission_ground' or triggered_id == 'input_y_max-emission_ground' or triggered_id == 'input_x_min-emission_supply' or triggered_id == 'input_x_max-emission_supply' or triggered_id == 'input_y_min-emission_supply' or triggered_id == 'input_y_max-emission_supply':
            figure, x_min, x_max, y_min, y_max = Set_axes_range(x_min, x_max, y_min, y_max, figure, log)

        figure['layout']['xaxis']['autorange'] = False
        figure['layout']['yaxis']['autorange'] = False
        return figure, None, x_min, x_max, y_min, y_max
    else:
        raise PreventUpdate
def get_axes_range(figure, log, relayoutData):
    x_min, x_max = figure['layout']['xaxis']['range']
    y_min, y_max = figure['layout']['yaxis']['range']
    if log == 'log':
        x_min = 10 ** x_min
        x_max = 10 ** x_max
    if log == 'linear' and 'yaxis.autorange' in list(relayoutData.keys()):
        figure['layout']['xaxis']['range'] = [x_min, x_max]
    x_min, x_max, y_min, y_max = round(x_min, 2), round(x_max, 2), round(y_min, 2), round(y_max, 2)
    return figure, x_min, x_max, y_min, y_max
def Set_axes_range(x_min, x_max, y_min, y_max, figure, log):
    if log == 'log':
        input_x_min = math.log(x_min,10)
        input_x_max = math.log(x_max,10)
    else:
        input_x_min, input_x_max = x_min, x_max
    figure['layout']['xaxis']['range'] = [input_x_min, input_x_max]
    figure['layout']['yaxis']['range'] = [y_min, y_max]
    return figure, x_min, x_max, y_min, y_max

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Output('emission_conducted_ground', 'restyleData', allow_duplicate=True),
    Output('input_x_min-emission_ground', 'value', allow_duplicate=True),
    Output('input_x_max-emission_ground', 'value', allow_duplicate=True),
    Output('suspectsTable-conducted', 'rowData', allow_duplicate=True),
    Output('suspectsTable-conducted', 'selectedRows', allow_duplicate=True),
    Output('limits-table-ground', 'rowData', allow_duplicate=True),
    Output('limits-table-ground', 'selectedRows', allow_duplicate=True),
    Input('emission_conducted_ground', 'restyleData'),
    State('emission_conducted_ground', 'figure'),
    State('markers-ground', 'data'),
    State('activate-marker-conducted', 'on'),
    State('suspectsTable-conducted', 'rowData'),
    State('limits-table-ground', 'rowData'),
    prevent_initial_call=True)

def update_ground(legend, figure, markers, activate_markers, suspectsTable_rowData, limitsTable_rowData):
    return update(legend, figure, markers, activate_markers, suspectsTable_rowData, limitsTable_rowData, 'Ground')

@app.callback(Output('emission_conducted_supply', 'figure',allow_duplicate = True),
    Output('emission_conducted_supply', 'restyleData', allow_duplicate=True),
    Output('input_x_min-emission_supply', 'value', allow_duplicate=True),
    Output('input_x_max-emission_supply', 'value', allow_duplicate=True),
    Output('suspectsTable-conducted', 'rowData', allow_duplicate=True),
    Output('suspectsTable-conducted', 'selectedRows', allow_duplicate=True),
    Output('limits-table-supply', 'rowData', allow_duplicate=True),
    Output('limits-table-supply', 'selectedRows', allow_duplicate=True),
    Input('emission_conducted_supply', 'restyleData'),
    State('emission_conducted_supply', 'figure'),
    State('markers-supply', 'data'),
    State('activate-marker-conducted', 'on'),
    State('suspectsTable-conducted', 'rowData'),
    State('limits-table-supply', 'rowData'),
    prevent_initial_call=True)

def update_supply(legend, figure, markers, activate_markers, suspectsTable_rowData, limitsTable_rowData):
    return update(legend, figure, markers, activate_markers, suspectsTable_rowData, limitsTable_rowData, 'Supply')

@app.callback(Output('emission_radiated_horizontal', 'figure', allow_duplicate = True),
    Output('emission_radiated_horizontal', 'restyleData', allow_duplicate=True),
    Output('input_x_min-emission_h', 'value', allow_duplicate=True),
    Output('input_x_max-emission_h', 'value', allow_duplicate=True),
    Output('suspectsTable-radiated', 'rowData', allow_duplicate=True),
    Output('suspectsTable-radiated', 'selectedRows', allow_duplicate=True),
    Output('limits-table-h', 'rowData', allow_duplicate=True),
    Output('limits-table-h', 'selectedRows', allow_duplicate=True),
    Input('emission_radiated_horizontal', 'restyleData'),
    State('emission_radiated_horizontal', 'figure'),
    State('markers-h', 'data'),
    State('activate-marker', 'on'),
    State('suspectsTable-radiated', 'rowData'),
    State('limits-table-h', 'rowData'),
    prevent_initial_call=True)

def update_horizontal(legend, figure, markers, activate_markers, suspectsTable_rowData, limitsTable_rowData):
    return update(legend, figure, markers, activate_markers, suspectsTable_rowData, limitsTable_rowData, 'Horizontal')

@app.callback(Output('emission_radiated_vertical', 'figure',allow_duplicate = True),
    Output('emission_radiated_vertical', 'restyleData', allow_duplicate=True),
    Output('input_x_min-emission_v', 'value', allow_duplicate=True),
    Output('input_x_max-emission_v', 'value', allow_duplicate=True),
    Output('suspectsTable-radiated', 'rowData', allow_duplicate=True),
    Output('suspectsTable-radiated', 'selectedRows', allow_duplicate=True),
    Output('limits-table-v', 'rowData', allow_duplicate=True),
    Output('limits-table-v', 'selectedRows', allow_duplicate=True),
    Input('emission_radiated_vertical', 'restyleData'),
    State('emission_radiated_vertical', 'figure'),
    State('markers-v', 'data'),
    State('activate-marker', 'on'),
    State('suspectsTable-radiated', 'rowData'),
    State('limits-table-v', 'rowData'),
    prevent_initial_call=True)

def update_vertical(legend, figure, markers, activate_markers, suspectsTable_rowData, limitsTable_rowData):
    return update(legend, figure, markers, activate_markers, suspectsTable_rowData, limitsTable_rowData, 'Vertical')

def update(legend, figure, markers, activate_markers, suspectsTable_rowData, limitsTable_rowData, type):
    if legend != []:
        legend_index = legend[1][0]
        meta = figure['data'][legend_index]['meta']
        visible = legend[0]['visible'][0]

        for trace in figure['data']:
            if trace['name'] in meta['Suspects'] or trace['name'] in meta['Limits']:
                trace['visible'] = visible

        select_suspect = []
        for suspect in suspectsTable_rowData:
            if suspect["Test Name"] == figure['data'][legend_index]['name'].split('-')[0] and suspect["Polarization"] == type and suspect["Band"] in meta["Bands"] and suspect['Detector'] == meta['Detector'] and suspect['RBW'] == meta['RBW']:
                if suspect['disabled'] == 'False':
                    suspect['disabled'] = 'True'
                else:
                    suspect['disabled'] = 'False'
                    select_suspect.append(suspect)
            else:
                select_suspect.append(suspect)

        select_limit = []
        for limit in limitsTable_rowData:
            if limit['Name'] in meta['Limits']:
                if limit['disabled'] == 'False':
                    limit['disabled'] = 'True'
                else:
                    limit['disabled'] = 'False'
                    select_limit.append(limit)
            else:
                select_limit.append(limit)

        if markers != []:
            for marker in markers:
                if marker['line_index'] == legend_index:
                    for trace in figure['data']:
                        if marker['name'] == trace['name'] and activate_markers == True:
                            trace['visible'] = visible
                            break
                    for annotation in figure['layout']['annotations']:
                        if marker['name'] == annotation['name'] and activate_markers == True:
                            if visible == 'legendonly':
                                annotation['visible'] = False
                            else:
                                annotation['visible'] = True
                            break

        x_min, x_max = no_update, no_update
        for trace in figure['data']:
            if trace['visible'] == True and trace['meta']['Type'] == 'Line':
                x_max_data, y_max, x_min_data, y_min = find_min_max(figure)
                if figure['layout']['xaxis']['type'] == 'log':
                    x_min, x_max = math.log10(x_min_data), math.log10(x_max_data)
                else:
                    x_min, x_max = x_min_data, x_max_data
                figure['layout']['xaxis']['range'] = [x_min, x_max]
                figure['layout']['yaxis']['autorange'] = True
                x_min, x_max = round(x_min_data, 2), round(x_max_data, 2)
                break
        return figure, None, x_min, x_max, suspectsTable_rowData, select_suspect, limitsTable_rowData, select_limit
    else:
        raise PreventUpdate

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Output('cursor-list-ground', 'style'),
    Output('cursor-output-ground','style'),
    Input('activate-cursor-ground', 'on'),
    State('emission_conducted_ground', 'figure'),
    State('cursor-list-ground', 'style'),
    State('cursor-output-ground','style'),
    prevent_initial_call=True)

def activate_cursors_ground(on,figure,cursor_list,cursor_output):
    return activate_cursors(on,figure,cursor_list,cursor_output)

@app.callback(Output('emission_conducted_supply', 'figure', allow_duplicate = True),
    Output('cursor-list-supply', 'style', allow_duplicate = True),
    Output('cursor-output-supply','style', allow_duplicate = True),
    Input('activate-cursor-supply', 'on'),
    State('emission_conducted_supply', 'figure'),
    State('cursor-list-supply', 'style'),
    State('cursor-output-supply','style'),
    prevent_initial_call=True)

def activate_cursors_supply(on,figure,cursor_list,cursor_output):
    return activate_cursors(on,figure,cursor_list,cursor_output)

@app.callback(Output('emission_radiated_horizontal', 'figure', allow_duplicate = True),
    Output('cursor-list-h', 'style'),
    Output('cursor-output-h','style'),
    Input('activate-cursor-h', 'on'),
    State('emission_radiated_horizontal', 'figure'),
    State('cursor-list-h', 'style'),
    State('cursor-output-h','style'),
    prevent_initial_call=True)

def activate_cursors_horizontal(on,figure,cursor_list,cursor_output):
    return activate_cursors(on,figure,cursor_list,cursor_output)

@app.callback(Output('emission_radiated_vertical', 'figure', allow_duplicate = True),
    Output('cursor-list-v', 'style', allow_duplicate = True),
    Output('cursor-output-v','style', allow_duplicate = True),
    Input('activate-cursor-v', 'on'),
    State('emission_radiated_vertical', 'figure'),
    State('cursor-list-v', 'style'),
    State('cursor-output-v','style'),
    prevent_initial_call=True)

def activate_cursors_vertical(on,figure,cursor_list,cursor_output):
    return activate_cursors(on,figure,cursor_list,cursor_output)

def activate_cursors(on,figure,cursor_list,cursor_output):
    if figure:
        if on is True:
            cursor_list['display'] = 'block'
            cursor_output['display'] = 'block'
            figure['layout']['hovermode']='x unified'
            if 'shapes' in figure['layout']:
                for i in range(len(figure['layout']['shapes'])):
                    if figure['layout']['shapes'][i]['name']=='Cursor 1' or figure['layout']['shapes'][i]['name']=='Cursor 2':
                        figure['layout']['shapes'][i]['visible'] = True
                for i in range(len(figure['layout']['annotations'])):
                    if figure['layout']['annotations'][i]['name'] == 'Cursor 1' or figure['layout']['annotations'][i]['name'] == 'Cursor 2':
                        figure['layout']['annotations'][i]['visible'] = True
        if on is False:
            cursor_list['display'] = 'none'
            cursor_output['display'] = 'none'
            figure['layout']['hovermode']='closest'
            if 'shapes' in figure['layout']:
                for i in range(len(figure['layout']['shapes'])):
                    if figure['layout']['shapes'][i]['name']=='Cursor 1' or figure['layout']['shapes'][i]['name']=='Cursor 2':
                        figure['layout']['shapes'][i]['visible'] = 'legendonly'
                for i in range(len(figure['layout']['annotations'])):
                    if figure['layout']['annotations'][i]['name'] == 'Cursor 1' or figure['layout']['annotations'][i]['name'] == 'Cursor 2':
                        figure['layout']['annotations'][i]['visible'] = False
    return figure,cursor_list,cursor_output

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Output('cursor-output-ground', 'children', allow_duplicate = True),
    Output('markers-ground', 'data', allow_duplicate = True),
    Output('cursor_data', 'data', allow_duplicate=True),
    Input('emission_conducted_ground', 'clickData'),
    State('cursor_data','data'),
    State('emission_conducted_ground', 'figure'),
    State('cursor-list-ground', 'value'),
    State('cursor-list-ground', 'options'),
    State('xaxis-emission_ground', 'value'),
    State('markers-ground', 'data'),
    State('cursor-output-ground', 'children'),
    State('activate-marker-conducted', 'on'),
    prevent_initial_call=True)

def cusors_ground (click_data, cursor_data, figure, value, options, log, markers, cursor_output, activate_marker):
    return cusors(click_data, cursor_data, figure, value, options, log, markers, cursor_output, activate_marker)

@app.callback(Output('emission_conducted_supply', 'figure', allow_duplicate = True),
    Output('cursor-output-supply', 'children', allow_duplicate = True),
    Output('markers-supply', 'data', allow_duplicate = True),
    Output('cursor_data','data', allow_duplicate = True),
    Input('emission_conducted_supply', 'clickData'),
    State('cursor_data','data'),
    State('emission_conducted_supply', 'figure'),
    State('cursor-list-supply', 'value'),
    State('cursor-list-supply', 'options'),
    State('xaxis-emission_supply', 'value'),
    State('markers-supply', 'data'),
    State('cursor-output-supply', 'children'),
    State('activate-marker-conducted', 'on'),
    prevent_initial_call=True)

def cusors_supply (click_data, cursor_data, figure, value, options, log, markers, cursor_output, activate_marker):
    return cusors(click_data, cursor_data, figure, value, options, log, markers, cursor_output, activate_marker)

@app.callback(Output('emission_radiated_horizontal', 'figure', allow_duplicate = True),
    Output('cursor-output-h', 'children', allow_duplicate = True),
    Output('markers-h', 'data', allow_duplicate = True),
    Output('cursor_data', 'data', allow_duplicate=True),
    Input('emission_radiated_horizontal', 'clickData'),
    State('cursor_data','data'),
    State('emission_radiated_horizontal', 'figure'),
    State('cursor-list-h', 'value'),
    State('cursor-list-h', 'options'),
    State('xaxis-emission_h', 'value'),
    State('markers-h', 'data'),
    State('cursor-output-h', 'children'),
    State('activate-marker', 'on'),
    prevent_initial_call=True)

def cusors_horizontal (click_data, cursor_data, figure,value,options,log,markers, cursor_output, activate_marker):
    return cusors(click_data, cursor_data, figure, value, options, log, markers, cursor_output, activate_marker)

@app.callback(Output('emission_radiated_vertical', 'figure', allow_duplicate = True),
    Output('cursor-output-v', 'children', allow_duplicate = True),
    Output('markers-v', 'data', allow_duplicate = True),
    Output('cursor_data', 'data', allow_duplicate=True),
    Input('emission_radiated_vertical', 'clickData'),
    State('cursor_data','data'),
    State('emission_radiated_vertical', 'figure'),
    State('cursor-list-v', 'value'),
    State('cursor-list-v', 'options'),
    State('xaxis-emission_v', 'value'),
    State('markers-v', 'data'),
    State('cursor-output-v', 'children'),
    State('activate-marker', 'on'),
    prevent_initial_call=True)

def cusors_vertical (click_data, cursor_data, figure, value, options, log, markers, cursor_output, activate_marker):
    return cusors(click_data, cursor_data, figure, value, options, log, markers, cursor_output, activate_marker)

def cusors(click_data, cursor_data, figure, value,options, log, markers, cursor_calculation, activate_marker):
    if figure['layout']['hovermode'] == 'closest' and figure['data'] != [] and click_data is not None and activate_marker is True:
        figure, markers = add_marker(click_data, figure, markers, log)


    elif click_data and figure and figure['layout']['hovermode'] == 'x unified':
        triggered_id = ctx.triggered_id
        graph_name = triggered_id.split('_')[1] + '_' + triggered_id.split('_')[2]

        chart_name = ''
        for item in click_data['points']:
            chart_index = item['curveNumber']
            if figure['data'][chart_index]['meta']['Name'] == value:
                chart_name = figure['data'][chart_index]['meta']['Name']
                break
        if chart_name == value:
            x = click_data['points'][0]['x']
            y = click_data['points'][0]['y']
            if log == 'log':
                x_log = math.log(x, 10)
            else:
                x_log = x
            x_max, y_max, x_min, y_min = find_min_max(figure)

            if graph_name not in list(cursor_data['left'].keys()):
                cursor_data['left'] = {graph_name: {'chart_index': chart_index, 'x': x, 'y': y}}
                shape = dict(type='line', name='Cursor 1', x0=x, x1 = x, y0=y_min - 4, y1=y_max + 4,
                             line=dict(color=figure['data'][chart_index]['line']['color'], dash='dash'), visible=True)
                annotation = dict(name='Cursor 1', x=x_log, y=1, xref="x", yref="paper",
                                  text=f"<b> {figure['data'][chart_index]['name']}<br> Frequency (MHz):</b> {x:.2f}<br> <b>Level (dBµV/m):</b> {y:.2f}",
                                  xanchor='left', yanchor='top', showarrow=False, bordercolor="#c7c7c7",
                                  bgcolor=figure['data'][chart_index]['line']['color'], font=dict(color="#ffffff"),
                                  visible=True, align='left')

            elif graph_name not in list(cursor_data['right'].keys()) and x > cursor_data['left'][graph_name]['x']:
                cursor_data['right'] = {graph_name: {'chart_index': chart_index, 'x': x, 'y': y}}
                shape = dict(type='line', name='Cursor 2', x0=x, x1 = x, y0=y_min - 4, y1=y_max + 4,
                             line=dict(color=figure['data'][chart_index]['line']['color'], dash='dash'), visible=True)
                annotation = dict(name='Cursor 2', x=x_log, y=1, xref="x", yref="paper",
                                  text=f"<b> {figure['data'][chart_index]['name']}<br> Frequency (MHz):</b> {x:.2f}<br> <b>Level (dBµV/m):</b> {y:.2f}",
                                  xanchor='left', yanchor='top', showarrow=False, bordercolor="#c7c7c7",
                                  bgcolor=figure['data'][chart_index]['line']['color'], font=dict(color="#ffffff"),
                                  visible=True, align='left')

            else:
                new_shapes = figure['layout']['shapes']
                for shape in figure['layout']['shapes'].copy():
                    if shape['name'] == 'Cursor 1':
                        new_shapes.remove(shape)
                    elif shape['name'] == 'Cursor 2':
                        new_shapes.remove(shape)
                        break
                figure['layout']['shapes'] = new_shapes
                new_annotations = figure['layout']['annotations']
                for annotation in figure['layout']['annotations'].copy():
                    if annotation['name'] == 'Cursor 1':
                        new_annotations.remove(annotation)
                    elif annotation['name'] == 'Cursor 2':
                        new_annotations.remove(annotation)
                        break
                figure['layout']['annotations'] = new_annotations

                figure['data'][cursor_data['left'][graph_name]['chart_index']]['meta']['Cursors'].remove('Cursor 1')
                cursor_data['left'] = {graph_name: {'chart_index': chart_index, 'x': x, 'y': y}}
                if graph_name in list(cursor_data['right'].keys()):
                    figure['data'][cursor_data['right'][graph_name]['chart_index']]['meta']['Cursors'].remove('Cursor 2')
                    cursor_data['right'].pop(graph_name)
                shape = dict(type='line', name='Cursor 1', x0=x, x1=x, y0=y_min - 4, y1=y_max + 4,
                             line=dict(color=figure['data'][chart_index]['line']['color'], dash='dash'), visible=True)
                annotation = dict(name='Cursor 1', x=x_log, y=1, xref="x", yref="paper",
                                  text=f"<b> {figure['data'][chart_index]['name']}<br> Frequency (MHz):</b> {x:.2f}<br> <b>Level (dBµV/m):</b> {y:.2f}",
                                  xanchor='left', yanchor='top', showarrow=False, bordercolor="#c7c7c7",
                                  bgcolor=figure['data'][chart_index]['line']['color'], font=dict(color="#ffffff"),
                                  visible=True, align='left')

            figure['layout']['shapes'].append(shape)
            figure['layout']['annotations'].append(annotation)
            figure['data'][chart_index]['meta']['Cursors'].append(shape['name'])

            if graph_name in cursor_data['left'] and graph_name in cursor_data['right']:
                diff_x = cursor_data['right'][graph_name]['x'] - cursor_data['left'][graph_name]['x']
                diff_y = cursor_data['right'][graph_name]['y'] - cursor_data['left'][graph_name]['y']
                cursor_calculation = f'ΔFrequency (MHz) = {diff_x:.2f} \n ΔLevel (dBμV/m) = {diff_y:.2f}'
            else:
                cursor_calculation = f'ΔFrequency (MHz) = - \n ΔLevel (dBμV/m) = -'

    else:
        raise PreventUpdate

    return figure, cursor_calculation, markers, cursor_data

@app.callback(Output('left-cursor-h', 'data'),
    Output('right-cursor-h', 'data'),
    Input('emission_radiated_horizontal', 'clickData'),
    State('left-cursor-h','data'),
    State('right-cursor-h','data'),
    State('activate-cursor-h', 'on'),
    State('cursor-list-h', 'value'),
    prevent_initial_call=True)

def save_cursors_horizontal(click_data, left_cursor, right_cursor, on, value):
    if click_data and on is True:
        left_cursor, right_cursor = save_cursors(click_data, left_cursor, right_cursor, on, value)
    return left_cursor, right_cursor

@app.callback(Output('left-cursor-v', 'data'),
    Output('right-cursor-v', 'data'),
    Input('emission_radiated_vertical', 'clickData'),
    State('left-cursor-v','data'),
    State('right-cursor-v','data'),
    State('activate-cursor-v', 'on'),
    State('cursor-list-v', 'value'),
    prevent_initial_call=True)

def save_cursors_vertical(click_data, left_cursor, right_cursor, on, value):
    if click_data and on is True:
        left_cursor, right_cursor = save_cursors(click_data, left_cursor, right_cursor, on, value)
    return left_cursor, right_cursor

def save_cursors(click_data, left_cursor, right_cursor, on, value):
    click_x = click_data['points'][0]['x']
    if left_cursor is None:
        return [click_x,value], right_cursor
    elif right_cursor is None:
        if click_x < left_cursor[0]:
            return [click_x, value], right_cursor
        else:
            return left_cursor, [click_x, value]
    return [click_x, value], None

@app.callback(
    Output("sidebar", "style"),
    Output("toggle-button", "style"),
    Output('toggle-button', 'disabled'),
    Output('line-table-container-ground', 'style', allow_duplicate=True),
    Output('line-table-btn-ground', 'children', allow_duplicate=True),
    Output('line-table-container-supply', 'style', allow_duplicate=True),
    Output('line-table-btn-supply', 'children', allow_duplicate=True),
    Output('line-table-container-h', 'style', allow_duplicate = True),
    Output('line-table-btn-h', 'children', allow_duplicate = True),
    Output('line-table-container-v', 'style', allow_duplicate = True),
    Output('line-table-btn-v', 'children', allow_duplicate = True),
    Input('selected-data-conducted', "data"),
    Input('selected-data-radiated', "data"),
    Input("toggle-button", "n_clicks"),
    State("sidebar", "style"),
    State("toggle-button", "style"),
    State('toggle-button', 'disabled'),
    State('line-table-container-ground', 'style'),
    State('line-table-btn-ground', 'children'),
    State('line-table-container-supply', 'style'),
    State('line-table-btn-supply', 'children'),
    State('line-table-container-h', 'style'),
    State('line-table-btn-h', 'children'),
    State('line-table-container-v', 'style'),
    State('line-table-btn-v', 'children'),
    prevent_initial_call=True)

def toggle_sidebar(data_conducted, data_radiated, n_clicks, style_sidebar, style_toggle_button, sidebar_btn, line_param_ground, btn_txt_ground, line_param_supply, btn_txt_supply, line_param_h, btn_txt_h, line_param_v, btn_txt_v):
    triggered_id = ctx.triggered_id
    if triggered_id == 'selected-data-conducted' or triggered_id == 'selected-data-radiated':
        if data_conducted + data_radiated == []:
            sidebar_btn = True
            style_sidebar["transform"] = "translateX(100%)"
            style_toggle_button["transform"] = "translateX(0%)"
            btn_txt_ground, btn_txt_supply, btn_txt_h, btn_txt_v = 'Show Line Display Parameters', 'Show Line Display Parameters', 'Show Line Display Parameters', 'Show Line Display Parameters'
            line_param_ground['display'], line_param_supply['display'], line_param_h['display'], line_param_v['display'] = 'none', 'none', 'none', 'none'
        else:
            sidebar_btn = False
    elif triggered_id == "toggle-button":
        if n_clicks % 2 == 1:  # Show the sidebar
            style_sidebar["transform"] = "translateX(0)"
            style_toggle_button["transform"] = "translateX(-175%)"
        else:
            style_sidebar["transform"] = "translateX(100%)"
            style_toggle_button["transform"] = "translateX(0%)"
            btn_txt_ground, btn_txt_supply, btn_txt_h, btn_txt_v = 'Show Line Display Parameters', 'Show Line Display Parameters', 'Show Line Display Parameters', 'Show Line Display Parameters'
            line_param_ground['display'], line_param_supply['display'], line_param_h['display'], line_param_v['display'] = 'none', 'none', 'none', 'none'
    return style_sidebar, style_toggle_button, sidebar_btn, line_param_ground, btn_txt_ground, line_param_supply, btn_txt_supply, line_param_h, btn_txt_h, line_param_v, btn_txt_v

# Callback to show/hide the emission submenu
@app.callback(Output("radiated-electric-submenu", "style"),
    Output("conducted-voltage-submenu", "style"),
    Output("radiated-btn", "n_clicks"),
    Output("conducted-btn", "n_clicks"),
    Output('line-table-container-h', 'style', allow_duplicate = True),
    Output('line-table-btn-h', 'children', allow_duplicate = True),
    Output('line-table-container-v', 'style', allow_duplicate = True),
    Output('line-table-btn-v', 'children', allow_duplicate = True),
    Input("radiated-btn", "n_clicks"),
    Input("conducted-btn", "n_clicks"),
    State('line-table-container-h', 'style'),
    State('line-table-btn-h', 'children'),
    State('line-table-container-v', 'style'),
    State('line-table-btn-v', 'children'),
    prevent_initial_call=True
)
def toggle_submenus(emission_clicks, immunity_clicks, line_param_h, btn_txt_h, line_param_v, btn_txt_v):
    ctx = dash.callback_context

    # Check which button was clicked
    if ctx.triggered:
        clicked_button = ctx.triggered[0]["prop_id"].split(".")[0]  # get the button ID

        # Initially set both submenus to hidden
        emission_style = submenu_style
        immunity_style = submenu_style

        # Logic to show/hide the appropriate submenu
        if clicked_button == "radiated-btn":
            if emission_clicks % 2 == 1:  # Emission button clicked an odd number of times
                emission_style = submenu_active_style
                immunity_clicks = 0
            else:  # Emission button clicked an even number of times
                emission_style = submenu_style
                immunity_style = submenu_style  # Hide Immunity submenu

        elif clicked_button == "conducted-btn":
            if immunity_clicks % 2 == 1:  # Immunity button clicked an odd number of times
                immunity_style = submenu_active_style
                emission_clicks = 0
            else:  # Immunity button clicked an even number of times
                immunity_style = submenu_style
                emission_style = submenu_style  # Hide Emission submenu
                btn_txt_h, btn_txt_v = 'Show Line Display Parameters', 'Show Line Display Parameters'
                line_param_h['display'], line_param_v['display'] = 'none', 'none'

        return emission_style, immunity_style, emission_clicks, immunity_clicks, line_param_h, btn_txt_h, line_param_v, btn_txt_v
    return submenu_style, submenu_style, 0, 0, line_param_h, btn_txt_h, line_param_v, btn_txt_v

@app.callback(Output('clear_markers_btn_conducted', 'n_clicks'),
    Output('emission_conducted_ground', 'figure',allow_duplicate = True),
    Output('emission_conducted_supply', 'figure',allow_duplicate = True),
    Output('markers-ground', 'data',allow_duplicate = True),
    Output('markers-supply', 'data',allow_duplicate = True),
    Input('clear_markers_btn_conducted', 'n_clicks'),
    State('markers-ground', 'data'),
    State('markers-supply', 'data'),
    State('emission_conducted_ground', 'figure'),
    State('emission_conducted_supply', 'figure'),
    State('activate-marker-conducted', 'on'),
    prevent_initial_call=True)

def clear_markers_conducted(n_clicks, markers_ground, markers_supply, figure_conducted_ground, figure_conducted_supply, on):
    return clear_markers(n_clicks, markers_ground, markers_supply, figure_conducted_ground, figure_conducted_supply, on)

@app.callback(Output('clear_markers_btn', 'n_clicks'),
    Output('emission_radiated_horizontal', 'figure',allow_duplicate = True),
    Output('emission_radiated_vertical', 'figure',allow_duplicate = True),
    Output('markers-h', 'data',allow_duplicate = True),
    Output('markers-v', 'data',allow_duplicate = True),
    Input('clear_markers_btn', 'n_clicks'),
    State('markers-h', 'data'),
    State('markers-v', 'data'),
    State('emission_radiated_horizontal', 'figure'),
    State('emission_radiated_vertical', 'figure'),
    State('activate-marker', 'on'),
    prevent_initial_call=True)

def clear_markers_radiated(n_clicks, markers_h, markers_v, figure_radiated_horizontal, figure_radiated_vertical, on):
    return clear_markers(n_clicks, markers_h, markers_v, figure_radiated_horizontal, figure_radiated_vertical, on)

def clear_markers(n_clicks, markers_1, markers_2, figure_1, figure_2, on):
    if on is True:
        if n_clicks == 1:
            markers = [markers_1, markers_2]
            figures = [figure_1, figure_2]
            for i in range(2):
                if markers[i] != []:
                    for marker in markers[i]:
                        if figures[i]['data'] != []:
                            for j in range (len(figures[i]['data'])):
                                if marker['name'] == figures[i]['data'][j]['name']:
                                    figures[i]['data'].pop(j)
                                    break
                            for j in range (len(figures[i]['layout']['annotations'])):
                                if marker['name'] == figures[i]['layout']['annotations'][j]['name']:
                                    figures[i]['layout']['annotations'].pop(j)
                                    break
            markers_1, markers_2 = [], []
    return 0, figure_1, figure_2, markers_1, markers_2

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Output('emission_conducted_supply', 'figure', allow_duplicate = True),
    Input('activate-marker-conducted', 'on'),
    State('emission_conducted_ground', 'figure'),
    State('emission_conducted_supply', 'figure'),
    State('markers-ground', 'data'),
    State('markers-supply', 'data'),
    prevent_initial_call=True)

def toggle_marker_conducted (on, figure_conducted_ground, figure_conducted_supply, markers_ground, markers_supply):
    return toggle_marker(on, figure_conducted_ground, figure_conducted_supply, markers_ground, markers_supply)

@app.callback(Output('emission_radiated_horizontal', 'figure',allow_duplicate = True),
    Output('emission_radiated_vertical', 'figure',allow_duplicate = True),
    Input('activate-marker', 'on'),
    State('emission_radiated_horizontal', 'figure'),
    State('emission_radiated_vertical', 'figure'),
    prevent_initial_call=True)

def toggle_marker_radiated (on, figure_radiated_horizontal, figure_radiated_vertical):
    return toggle_marker(on, figure_radiated_horizontal, figure_radiated_vertical)

def toggle_marker(on, figure_1, figure_2, markers_1, markers_2):
    figures = [figure_1, figure_2]
    markers = [markers_1, markers_2]
    for i in range(2):
        for trace in figures[i]['data']:
            if trace['meta']['Type'] == 'Marker':
                marker = next((marker for marker in markers[i] if marker['name'] == trace['name']), None)
                if figures[i]['data'][marker['line_index']]['visible'] == True:
                    trace['visible'] = on
                    pass
        for annotation in figures[i]['layout']['annotations']:
            if annotation['name'].split(' ')[0] == 'Marker':
                marker = next((marker for marker in markers[i] if marker['name'] == annotation['name']), None)
                if figures[i]['data'][marker['line_index']]['visible'] == True:
                    annotation['visible'] = on
                    pass
    return figure_1, figure_2

def add_marker(clickData, figure, markers, log):
    if figure['data'][clickData['points'][0]['curveNumber']]['name'].split(' ')[0] == 'Limit':
        return figure, markers
    add_marker = True
    if 'annotations' not in figure['layout']:
        figure['layout']['annotations'] = []
    name = figure['data'][clickData['points'][0]['curveNumber']]['name']
    x_point = clickData['points'][0]['x']
    y_point = clickData['points'][0]['y']
    if log == 'log':
        x_point_log = math.log(x_point, 10)
    else:
        x_point_log = x_point
    for i in range (len(markers)):
        if x_point == markers[i]['x'] and y_point == markers[i]['y']:
            for j in range(len(figure['data'])):
                if figure['data'][j]['name'] == markers[i]['name']:
                    figure['data'].pop(j)
                    break
            for j in range(len(figure['layout']['annotations'])):
                if figure['layout']['annotations'][j]['name'] == markers[i]['name']:
                    figure['layout']['annotations'].pop(j)
                    break
            markers.pop(i)
            add_marker = False
            break
    if add_marker == False:
        index = 1
        for i in range (len(figure['layout']['annotations'])):
            if figure['layout']['annotations'][i]['name'].split(' ')[0] == 'Marker':
                figure['layout']['annotations'][i]['text'] = figure['layout']['annotations'][i]['text'].replace(figure['layout']['annotations'][i]['text'].split('<br>')[0], '<b> Marker ' + str(index))
                figure['layout']['annotations'][i]['name'] = 'Marker ' + str(index)
                markers[index-1]['name'] = 'Marker ' + str(index)
                index += 1
        index = 1
        for i in range (len(figure['data'])):
            if figure['data'][i]['name'].split(' ')[0] == 'Marker':
                figure['data'][i]['name'] = 'Marker ' + str(index)
                index += 1
    if add_marker is True:
        meta = {'Name' : 'Marker ' + str(len(markers) + 1), 'Type': 'Marker'}
        trace = dict(name='Marker ' + str(len(markers) + 1), x=[x_point], y=[y_point], mode='markers',
                                   marker=dict(color='red', size=10), showlegend=False, hoverinfo="none", meta = meta)
        annotation = dict(name='Marker ' + str(len(markers) + 1), x=x_point_log, y=y_point, xref="x", yref="y",
                 text=f"<b> {'Marker ' + str(len(markers) + 1)}:<br> {name.split('#')[0]} <br> Frequency (MHz):</b> {x_point:.2f} <b> <br> Level (dBµV/m):</b> {y_point:.2f}",
                 xanchor='left', yanchor='top', showarrow=False, ax=0,
                 bordercolor="#c7c7c7",
                 bgcolor='red',
                 font=dict(color="#ffffff"), visible=True, align='left', meta = meta, captureevents= True, editable= True,)
        figure['data'].append(trace)
        figure['layout']['annotations'].append(annotation)
        markers.append({'line_index':clickData['points'][0]['curveNumber'], 'name': 'Marker ' + str(len(markers) + 1), 'x': clickData['points'][0]['x'], 'y': clickData['points'][0]['y'], 'chart_name': name, 'trace': trace, 'annotation': annotation})
    return figure, markers

@app.callback(Output('emission_conducted_ground', 'figure', allow_duplicate = True),
    Input('emission_conducted_ground', 'relayoutData'),
    State('emission_conducted_ground', 'figure'),
    State('markers-ground', 'data'),
    prevent_initial_call=True)

def remove_marker_ground(relayoutData, figure, markers):
    return remove_marker(relayoutData, figure, markers)

@app.callback(Output('emission_conducted_supply', 'figure', allow_duplicate = True),
    Input('emission_conducted_supply', 'relayoutData'),
    State('emission_conducted_supply', 'figure'),
    State('markers-supply', 'data'),
    prevent_initial_call=True)

def remove_marker_supply(relayoutData, figure, markers):
    return remove_marker(relayoutData, figure, markers)

@app.callback(Output('emission_radiated_horizontal', 'figure', allow_duplicate = True),
    Input('emission_radiated_horizontal', 'relayoutData'),
    State('emission_radiated_horizontal', 'figure'),
    State('markers-h', 'data'),
    prevent_initial_call=True)

def remove_marker_horizontal(relayoutData, figure, markers):
    return remove_marker(relayoutData, figure, markers)

@app.callback(Output('emission_radiated_vertical', 'figure', allow_duplicate = True),
    Input('emission_radiated_vertical', 'relayoutData'),
    State('emission_radiated_vertical', 'figure'),
    State('markers-v', 'data'),
    prevent_initial_call=True)

def remove_marker_vertical(relayoutData, figure, markers):
    return remove_marker(relayoutData, figure, markers)

def remove_marker(relayoutData, figure, markers):
    if relayoutData and 'annotations' in list(relayoutData.keys())[0] and 'Marker' in str(list(relayoutData.values())[0]):
        name = list(relayoutData.values())[0][4:12]
        for trace in figure['data']:
            if trace['name'] == name:
                figure['data'].remove(trace)
                break
        for annotation in figure['layout']['annotations']:
            if annotation['name'] == name:
                figure['layout']['annotations'].remove(annotation)
                break
        for marker in markers:
            if marker['name'] == name:
                markers.remove(marker)
                break
        return figure
    else:
        raise PreventUpdate

@app.callback(Output('line-table-container-ground', 'style', allow_duplicate = True),
    Output('line-table-container-supply', 'style', allow_duplicate = True),
    Output('line-table-btn-ground', 'children', allow_duplicate = True),
    Output('line-table-btn-supply', 'children', allow_duplicate = True),
    Input('line-table-btn-ground', 'n_clicks'),
    State('line-table-container-ground', 'style'),
    State('line-table-container-supply', 'style'),
    State('line-table-btn-supply', 'children'),
    prevent_initial_call=True)

def toggle_line_param_ground (btn_click, line_param_ground, line_param_supply, btn_txt_2):
    return toggle_line_param (line_param_ground, line_param_supply, btn_txt_2)

@app.callback(Output('line-table-container-supply', 'style', allow_duplicate = True),
    Output('line-table-container-ground', 'style', allow_duplicate = True),
    Output('line-table-btn-supply', 'children', allow_duplicate = True),
    Output('line-table-btn-ground', 'children', allow_duplicate = True),
    Input('line-table-btn-supply', 'n_clicks'),
    State('line-table-container-ground', 'style'),
    State('line-table-container-supply', 'style'),
    State('line-table-btn-ground', 'children'),
    prevent_initial_call=True)

def toggle_line_param_supply (btn_click, line_param_ground, line_param_supply, btn_txt_2):
    return toggle_line_param (line_param_supply, line_param_ground, btn_txt_2)

@app.callback(Output('line-table-container-h', 'style', allow_duplicate = True),
    Output('line-table-container-v', 'style', allow_duplicate = True),
    Output('line-table-btn-h', 'children', allow_duplicate = True),
    Output('line-table-btn-v', 'children', allow_duplicate = True),
    Input('line-table-btn-h', 'n_clicks'),
    State('line-table-container-h', 'style'),
    State('line-table-container-v', 'style'),
    State('line-table-btn-v', 'children'),
    prevent_initial_call=True)

def toggle_line_param_h (btn_click, line_param_horizontal, line_param_vertical, btn_txt_2):
    return toggle_line_param (line_param_horizontal, line_param_vertical, btn_txt_2)

@app.callback(Output('line-table-container-v', 'style', allow_duplicate = True),
    Output('line-table-container-h', 'style', allow_duplicate = True),
    Output('line-table-btn-v', 'children', allow_duplicate = True),
    Output('line-table-btn-h', 'children', allow_duplicate = True),
    Input('line-table-btn-v', 'n_clicks'),
    State('line-table-container-h', 'style'),
    State('line-table-container-v', 'style'),
    State('line-table-btn-h', 'children'),
    prevent_initial_call=True)

def toggle_line_param_v (btn_click, line_param_horizontal, line_param_vertical, btn_txt_2):
    return toggle_line_param (line_param_vertical, line_param_horizontal, btn_txt_2)

def toggle_line_param (line_param_1, line_param_2, btn_txt_2):
    btn_txt_1 = 'Show Line Display Parameters'
    if line_param_1['display'] == 'none':
        line_param_1['display'] = 'flex'
        btn_txt_1 = 'Hide Line Display Parameters'
        if line_param_2['display'] == 'flex':
            line_param_2['display'] = 'none'
            btn_txt_2 = 'Show Line Display Parameters'
    else:
        line_param_1['display'] = 'none'
    return line_param_1, line_param_2, btn_txt_1, btn_txt_2

if __name__ == "__main__":
    app.run_server(debug=True)