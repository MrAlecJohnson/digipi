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

frame = pd.read_pickle("../store/adviser.pkl")
schema = pandas_gbq.gbq.generate_bq_schema(frame, default_type='STRING')

schema
#frame.dtypes()
