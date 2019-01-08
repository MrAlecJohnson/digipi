import requests
import pandas as pd
import os
from datetime import datetime
from io import StringIO
import sys
import time
from pathlib import Path
from google.oauth2 import service_account
import pandas_gbq

# get file, upload file, delete file

def pages():
    #parentPath = Path(os.getcwd()).parent
    type = sys.argv[1]
    frame = pd.read_pickle("../store/"+type + ".pkl")
    length = frame.shape[0]
    KEY_FILE_LOCATION_BQ = "../creds/backlogger_bq.json"
    credentials = service_account.Credentials.from_service_account_file(KEY_FILE_LOCATION_BQ)

    i = 0
    j = 5000

    while i < length:
        out = frame.iloc[i:j]
        out.to_gbq('AlecTest.PagesReport', 'hardy-album-169409',
                   if_exists = 'append', private_key=KEY_FILE_LOCATION_BQ, chunksize = None)

        time.sleep(60)

        i = j
        j = j+5000

    os.remove("../store/"+type + ".pkl")


    #frame will need cleaning
if __name__ == '__main__':
    pages()
