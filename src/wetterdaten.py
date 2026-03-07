# Documentation see: https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data?data-structure=daily-parameters

import csv
import os.path

import myrequests
from datetime import datetime, timedelta
import json
import time

url_toc = "https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-local-forecasting/items"

# Station nehmen wir St.Gallen, da im Meteoschweiz auch die Daten davon genommen werden, wenn man Herisau eingibt.
point_id = 56
point_name = "St. Gallen"  # to be verified in downloaded data

id_map = {
    # daily data
    "id_temp_min": "tre200pn",
    "id_temp_max": "tre200px",
    "id_temp_hourly_mean": "tre200h0",

    # hourly data
    # "id_sunshine_dur": "sre000h0", noch unklar wie zu interpretieren
    "id_niederschlag": "rka150p0",
    "id_symbol": "jp2000d0"
}


def get_toc() -> dict:
    toc_file = "../toc.csv"
    if os.path.isfile(toc_file):
        filectime = os.path.getmtime(toc_file)
    else:
        filectime = 0
    timenow = time.time()
    diff_s = timenow - filectime
    if (diff_s < 3600.0):
        print(f"{toc_file} is {diff_s} s old. Use it")
    else:
        print(f"Downloading {toc_file}")
        response = myrequests.get(url_toc)
        with open(toc_file, "wb") as f:
            f.write(response.content)

def get_latest_url_from_toc(collection_id: str):
    with open('../toc.csv', "r", newline='') as f:
        jsondata = json.load(f)
        # pprint(jsondata)
        items = jsondata.get("features", [])
        # Sortieren nach Zeit: wir nehmen das "datetime"-Feld im Item
        items_sorted = sorted(items, key=lambda it: it["properties"]["datetime"], reverse=True)
        for it in items_sorted:
            assets = it.get("assets", {})
            # Schau, ob der Tre-200px-Asset da ist
            for name, asset in assets.items():
                # Je nachdem wie der Parameter genau heißt (z. B. "tre200px" oder ähnlich)
                if collection_id in name:
                    return asset["href"], it["properties"]["datetime"]


def download_file_if_necessary(url):
    filename = url.split('/')[-1]
    if os.path.exists(filename):
        print(f"File {filename} already exists.")
    else:
        print(f"Downloading {filename}")
        resp = myrequests.get(url)
        with open(filename, "wb") as f:
            f.write(resp.content)
    return filename


def filter_csv_by_value(path, column_name, value):
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row[column_name] == str(value):
                # print(row)      # oder yield row für Generator
                pass


def get_val_of_date(csvfile: str, date: datetime) -> list:
    """
    List of values for our location point_id
    :param csvfile: a data file
    :param date: Date (Day) we want to extract from csvfile
    :return: List of values of the requested date
    """
    with open(csvfile, newline='', encoding="utf-8") as f:
        collection_id = csvfile.split('.')[-2]
        reader = csv.DictReader(f, delimiter=';')
        datestr = date.strftime("%Y%m%d")
        list_of_values = []
        for row in reader:
            if row['point_id'] == str(point_id) and row['Date'].startswith(datestr):
                list_of_values.append(row[collection_id])  # Wert steht zuletzt im dict
        return list_of_values


def get_data_for_day(date: datetime):
    dates = {"Heute": date, "Morgen": date + timedelta(days=1)}
    result = dict()
    get_toc()
    for date in dates:
        result[date] = dict()
        for key in id_map:
            data_url = get_latest_url_from_toc(id_map[key])
            filename = download_file_if_necessary(data_url[0])
            result[date][key] = get_val_of_date(filename, dates[date])
    replace_id_symbol(result)
    return result


def replace_id_symbol(result_data: dict):
    for day in result_data:
        id = result_data[day]["id_symbol"][0]
        with open("wetter_icons.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=("id", "val"), delimiter=';')

            def inner_loop():
                for row in reader:
                    if row["id"] == id:
                        result_data[day]["id_symbol"] = row["val"]
                        return;

            inner_loop()


def getMinMaxTemp(weather: dict) -> tuple[float, float]:
    """
    :param weather: Dict aus Key=Tagen mit Value=Ergebnis von get_data_for_day
    :return:
    """
    minTemp = float("inf")
    maxTemp = float("-inf")
    for dayWeather in weather:
        temp = weather[dayWeather]["id_temp_hourly_mean"]
        tempf = list(map(float, temp))
        minTemp = min(minTemp, min(tempf))
        maxTemp = max(maxTemp, max(tempf))
    return (minTemp, maxTemp)


if __name__ == "__main__":
    today = datetime.now()
    result = get_data_for_day(today)
    print(str(result))
    print(result["Heute"]["id_temp_hourly_mean"])
    print(result)
