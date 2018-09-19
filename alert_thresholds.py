#!/usr/bin/env python3
import json
import os
import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

"""Application Constants"""
PANEL_DIR = '/var/lib/grafana/dashboards/'
LOG_DIR = '/home/ansibleuser/bin/grafana_panel/logs/'

"""Logging Stuff"""
logger = logging.getLogger('alert_thresholds')
handler = logging.FileHandler(LOG_DIR+'thresholds.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def main():
    for panel_file in os.listdir(PANEL_DIR):
        if panel_file.endswith('_Throughput.json'):
            #print(panel_file)
            #get_panel_thresholds(PANEL_DIR+panel_file)
            compare_thresholds(get_panel_thresholds(PANEL_DIR+panel_file),get_thresholds_from_google())
        else:
            """This needs to be moved out of the loop because it's creating too many logs when it doesn
               match a file."""
            logger.error('No .json files found in %s', PANEL_DIR)


def get_panel_thresholds(filename):
    panel_details = {}
    with open(filename, 'r') as f:
        data = json.load(f)
        panel_details['title'] = data['title']
        panel_details['alert_params'] = data['panels'][0]['alert']['conditions'][0]['evaluator']['params']
        panel_details['threshold_high'] = data['panels'][0]['thresholds'][0]['value']
        panel_details['filename'] = filename
        #print(panel_details)
        return panel_details
         

def get_thresholds_from_google():
    """Returns all the threshols from the google sheet as a list of dictionaries"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('/home/ansibleuser/bin/grafana_panel/client_secret.json', scope)
    client = gspread.authorize(credentials)
    sheet = client.open("test").sheet1
    records = sheet.get_all_records()
    return records

def compare_thresholds(panel, google):
    """We assume that the thresholds in the google sheet have priority"""
    for g in google:
        if g['title'] == panel['title']:
            logger.info("Comparing thresholds for %s", panel['title'])
            if panel['threshold_high'] != g['threshold_high']:
                logger.warning("Thresholds for %s are different. Attempting to set new threshold", g['title'])
                set_new_threshold(panel, g)

def set_new_threshold(panel, g):
    """Do we need to update the ID as well?"""
    filename = panel['filename']
    with open(filename, 'r') as f:
        data = json.load(f)
        data['panels'][0]['alert']['conditions'][0]['evaluator']['params'] = g['alert_params']
        data['panels'][0]['thresholds'][0]['value'] = g['threshold_high']
    os.remove(filename)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        logger.info("Setting new threshold of %s for %s in %s", g['threshold_high'], g['title'], panel['filename'])

if __name__ == "__main__":
   main()
