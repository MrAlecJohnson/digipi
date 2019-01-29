# Pulls data from Analytics API and uploads it to BigQuery.

#TODO if no arguments are passed, then request an input from the user

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials #depreciated
from google.oauth2 import service_account
import httplib2
import json
import pandas as pd
import pandas_gbq
from pathlib import Path
import os
import sys
import logging

def get_report():

    path1 = os.path.dirname(os.path.realpath(__file__))
    parentPath = os.path.dirname(path1)

    SPREADSHEET_ID = '1MUehUq5LVN3WjaT84Mve3zGG6sbn6x_citXygPclcK0'
    clear_RANGE_NAME = 'data!A2:E'

    SCOPES = ["https://www.googleapis.com/auth/tagmanager.readonly","https://www.googleapis.com/auth/spreadsheets"]
    KEY_FILE_LOCATION = os.path.join(parentPath,"creds","backlogger_bq.json")

    credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, scopes=SCOPES)

    http = httplib2.Http()
    http = credentials.authorize(http)

    paths = {"Mouseflow pages - All":"accounts/1090055821/containers/6311504/workspaces/208/variables/57",
             "Mouseflow pages - public":"accounts/1090055821/containers/6311504/workspaces/208/variables/21",
             "Mouseflow pages - adviser":"accounts/1090055821/containers/6311504/workspaces/208/variables/56"}

    gtm_service = build('tagmanager', 'v2', http=http)
    sheets_service = build('sheets', 'v4', http=http)
    sheet = sheets_service.spreadsheets()

    sheet.values().clear(spreadsheetId=SPREADSHEET_ID,
                                range=clear_RANGE_NAME).execute()

    for path, value in paths.items():
        response = gtm_service.accounts().containers().workspaces().variables().get(path=value).execute()
        clean = json.dumps(response)
        parsed_json = json.loads(clean)
        j_list = parsed_json['parameter'][6]['list']

        for x in j_list:
            name = x['map'][0]['value']
            val = x['map'][1]['value']
            body = {"range": "data!A2:E",
                    "majorDimension": "ROWS",
                    "values": [
                    [path, name, val],
                    ],}
            sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=clear_RANGE_NAME, body=body, valueInputOption='USER_ENTERED').execute()


if __name__ == '__main__':
    get_report()
