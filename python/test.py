from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials #depreciated
import httplib2
import json
import os
import logging

path1 = os.path.dirname(os.path.realpath(__file__))
parentPath = os.path.dirname(path1)

SCOPES = ["https://www.googleapis.com/auth/tagmanager.readonly","https://www.googleapis.com/auth/spreadsheets"]
KEY_FILE_LOCATION = os.path.join(parentPath,"creds","backlogger_bq.json")

credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, scopes=SCOPES)

http = httplib2.Http()
http = credentials.authorize(http)

gtm_service = build('tagmanager', 'v1', http=http)

vars = {"Mouseflow pages - All":"57",
         "Mouseflow pages - public":"21",
         "Mouseflow pages - adviser":"56"}

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
        print(name + " - " + val)





# try:
#   variable = gtm_service.accounts().containers().variables().get(
#       accountId='1090055821',
#       containerId='6311504',
#       variableId='57'
#   ).execute()
#   print (variable)
#
#
#
# except TypeError as error:
#   # Handle errors in constructing a query.
#   print ('There was an error in constructing your query : %s' % error)
#
# except HttpError as error:
#   # Handle API errors.
#   print ('There was an API error : %s : %s' %
#          (error.resp.status, error.resp.reason))
