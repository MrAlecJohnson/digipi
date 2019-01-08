#get the epi pages reports and save as pickle files

from io import StringIO
import pandas as pd
import csv
import requests
from datetime import datetime
import os
pd.set_option('display.max_colwidth', -1)
username = os.environ.get('epiname')
password = os.environ.get('epipass')
details = "username=" + username + "&password=" + password
edit_login = "https://edit.citizensadvice.org.uk/login/?" + details


def epi_pages_report():
    epi_login = edit_login
    public = "https://edit.citizensadvice.org.uk/api/reports/section.csv?root=6_242750"
    advisernet = "https://edit.citizensadvice.org.uk/api/reports/section.csv?root=36473_242727"
    public = makeFrame(public)
    adviser = makeFrame(advisernet)
    public.to_pickle("../store/public.pkl")
    adviser.to_pickle("../store/adviser.pkl")


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

        #schema(frame)

        return frame

def schema (df):
    df['Id'] = df['Id'],
    df['Guid'] = df['Guid'].astype('str'),
    df['Language'] = df['Language'].astype('str'),
    df['IsTranslation'] = df['IsTranslation'].astype('bool'),
    df['Name'] = df['Name'].astype('str'),
    df['Template'] = df['Template'].astype('str'),
    df['MainTitle'] = df['MainTitle'].astype('str'),
    df['NavigationLabel'] = df['NavigationLabel'].astype('str'),
    df['Description'] = df['Description'].astype('str'),
    df['Keywords'] = df['Keywords'].astype('str'),
    df['Status'] = df['Status'].astype('str'),
    df['Changed'] = df['Changed'].astype('datetime64'),
    df['StartPublish'] = df['StartPublish'].astype('datetime64'),
    df['StopPublish'] = df['StopPublish'].astype('datetime64'),
    df['Path'] = df['Path'].astype('str'),
    df['SimpleUrl'] = df['SimpleUrl'].astype('str'),
    df['ExtendCode'] = df['ExtendCode'].astype('str'),
    df['EffectiveExtentCode'] = df['EffectiveExtentCode'].astype('str'),
    df['IsPublic'] = df['IsPublic'].astype('bool'),
    df['Shortcut'] = df['Shortcut'].astype('str'),
    df['EditLink'] = df['EditLink'].astype('str'),
    df['Owner'] = df['Owner'].astype('str'),
    df['Editor'] = df['Editor'].astype('str'),
    df['Creator'] = df['Creator'].astype('str'),
    df['ReviewDate'] = df['ReviewDate'].astype('datetime64'),
    df['Groups'] = df['Groups'].astype('str'),
    df['OwnedByTeam'] = df['OwnedByTeam'].astype('str'),
    df['ReportDate'] = df['ReportDate'].astype('datetime64'),
    df['url'] = df['url'].astype('str'),
    df['LastAccuracyReview'] = df['LastAccuracyReview'].astype('datetime64')

    return df









if __name__ == '__main__':
    epi_pages_report()
