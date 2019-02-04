from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials #depreciated
import httplib2
import json
import os
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

    vars = {"Mouseflow pages - All":"57",
             "Mouseflow pages - public":"21",
             "Mouseflow pages - adviser":"56"}

    gtm_service = build('tagmanager', 'v1', http=http)
    sheets_service = build('sheets', 'v4', http=http)
    sheet = sheets_service.spreadsheets()

    sheet.values().clear(spreadsheetId=SPREADSHEET_ID,
                                range=clear_RANGE_NAME).execute()

    for var, value in vars.items():
        variable = gtm_service.accounts().containers().variables().get(
            accountId='1090055821',
            containerId='6311504',
            variableId=value
        ).execute()
        clean = json.dumps(variable)
        parsed_json = json.loads(clean)
        j_list = parsed_json['parameter'][6]['list']

        for x in j_list:
            name = x['map'][0]['value']
            val = x['map'][1]['value']
            body = {"range": "data!A2:E",
                    "majorDimension": "ROWS",
                    "values": [
                    [var, name, val],
                    ],}
            sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=clear_RANGE_NAME, body=body, valueInputOption='USER_ENTERED').execute()


if __name__ == '__main__':
    get_report()
