#get the epi pages reports and save as pickle files

from io import StringIO
import pandas as pd
import csv
import requests
from datetime import datetime
import os
from pathlib import Path
import logging

pd.set_option('display.max_colwidth', -1)
username = os.environ.get('epiname')
password = os.environ.get('epipass')
details = "username=" + username + "&password=" + password
edit_login = "https://edit.citizensadvice.org.uk/login/?" + details


def epi_pages_report():
    path1 = os.path.dirname(os.path.abspath(__file__))
    parentPath = os.path.dirname(path1)

    epi_login = edit_login
    public = "https://edit.citizensadvice.org.uk/api/reports/section.csv?root=6_242750"
    advisernet = "https://edit.citizensadvice.org.uk/api/reports/section.csv?root=36473_242727"
    public = makeFrame(public)
    adviser = makeFrame(advisernet)
    public.to_pickle(os.path.join(parentPath,"store","public.pkl"))
    adviser.to_pickle(os.path.join(parentPath,"store","adviser.pkl"))

    return "ran without error"


def makeFrame(link):
    now = datetime.now()
    today = datetime.date(now)
    site = 'https://www.citizensadvice.org.uk'
    country_code = dict([
        ('en-GB',''),
        ('en-SCT','/scotland'),
        ('en-NIR','/nireland'),
        ('en-WLS','/wales'),
        ('cy','/cymraeg')
    ])
    with requests.Session() as login:
        login.get(edit_login)
        getting = login.get(link, stream = True).text
        sheet = StringIO(getting)
        frame = pd.read_csv(sheet)

        frame['ReportDate'] = today
        frame['url'] = frame['Language']
        frame['url'] = frame['url'].replace(country_code)
        frame['url'] = site+frame['url']+frame['Path']
        frame.loc[frame['LastAccuracyReview'] == '01/01/0001 00:00:00','LastAccuracyReview'] = None
        frame.loc[frame['ReviewDate'] == '01/01/0001 00:00:00','ReviewDate'] = None
        frame['ReportDate'] = pd.to_datetime(frame['ReportDate'], errors = 'ignore', yearfirst = True)
        frame['StopPublish'] = pd.to_datetime(frame['StopPublish'], errors = 'ignore')
        frame['StartPublish'] = pd.to_datetime(frame['StartPublish'], errors = 'ignore')
        frame['Changed'] = pd.to_datetime(frame['Changed'], errors = 'ignore')
        frame['ReviewDate'] = pd.to_datetime(frame['ReviewDate'], errors = 'ignore')
        frame['LastAccuracyReview'] = pd.to_datetime(frame['LastAccuracyReview'], errors = 'ignore')
        strCols = frame.select_dtypes(include = ['object'])
        frame[strCols.columns] = strCols.apply(lambda x: x.str.replace('\n|\r', ' '))
        frame[strCols.columns] = strCols.apply(lambda x: x.astype('str'))

        return frame

if __name__ == '__main__':
    epi_pages_report()
