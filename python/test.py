import os
from pathlib import Path

path1 = os.path.dirname(os.path.realpath(__file__))
parentPath = Path(path1).parent

KEY_FILE_LOCATION = os.path.join(parentPath,"creds","backlogger_bq.json")

print (KEY_FILE_LOCATION)
