from datetime import datetime, timedelta
import os

def getCreateFolderFromDate(date_time = datetime.now() + timedelta(hours=12)):
    """ gibt den Ordner zum Datum zurück, erstellt ihn, falls nötig"""
    folder = date_time.strftime("%y%m_%d")
    os.makedirs(folder, exist_ok=True)
    return folder
