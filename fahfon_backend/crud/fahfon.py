import os
import requests
import json
import pandas as pd
import csv
from io import StringIO
from datetime import datetime, timedelta
from google.cloud import bigquery
current_directory = os.getcwd()

service_account_key_file = os.path.join(current_directory, "depa-smartcity-thailand.json")
client = bigquery.Client.from_service_account_json(service_account_key_file)
job_config = bigquery.LoadJobConfig()
job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
project_name = "depa-smartcity-thailand"
database_name = "fahfon"
device_table_name = "device_table"
response_table_name = "response_table"

def getLastest():
    query = f"SELECT * FROM {project_name}.{database_name}.{response_table_name} where response_id in (SELECT MAX(response_id) as response_id FROM {project_name}.{database_name}.{response_table_name} GROUP BY serial) ORDER BY serial ASC;"
    results = client.query(query)
    ret = []
    for result in results:
        ret.append(dict(result))
    query = f"SELECT * FROM {project_name}.{database_name}.{device_table_name} ORDER BY serial ASC;"
    results = client.query(query)
    i=0
    for result, ret_row in zip(results, ret):
        ret_row.update(result)
        ret[i] = ret_row
        i+=1
        
    return ret

def insertData():
    serials = ["S1-0000898008","S1-0000898009", "S1-862798061963860" ,"S1-862798061947996" ,"S1-862798061921397" ,"S1-862798061909343" ,"S1-862798061954638" ,"S1-862798061913972" ,"S1-862798061948093" ,"S1-862798061952459" ,"S1-862798061917775" ,"S1-862798061948119" ,"S1-862798061934663" ,"S1-862798061945255" ,"S1-862798061952848" ,"S1-862798061929218" ,"S1-862798061934507" ,"S1-862798061901845"  ,"S1-862798061948036" ,"S1-862798061940975" ,"S1-862798061937104" ,"S1-862798061930315" ,"S1-862798061940900" ,"S1-862798061925000" ,"S1-862798061960437" ,"S1-862798061922841" ,"S1-862798061936395" ,"S1-862798061958019" ,"S1-862798061948028" ,"S1-862798061952640" ,"S1-862798061948259" ,"S1-862798061911323" ,"S1-862798061952715" ,"S1-862798061916611" ,"S1-862798061948051" ,"S1-862798061948218" ,"S1-862798061911141"  ,"S1-862798061952681" ,"S1-862798061963563" ,"S1-862798061901878" ,"S1-862798061948010" ,"S1-862798061963688" ,"S1-862798061963738"  ,"S1-862798061913121" ,"S1-862798061951576" ]
    url =  'http://www.regis.fahfon.info:8180/uAtTestListInfoBySerial.php'
    payload = {   
        'requestType': 'application/json',
        'uid': 'dapaPayak1',
        'stringKEY': 'p1g@g11',
        'siteName': 'depa-payak',
        'lastNdays': '1',
        'maxResult': '288',
        "serial": 'S1-862798061940975'
        }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded' 
    }
    query = f"SELECT MAX(response_id) AS max_response_id FROM {project_name}.{database_name}.{response_table_name}"
    results = client.query(query)
    
    try:
        for row in results:
            id = int(row["max_response_id"])
    except Exception:
            id=0

    for serial in serials:
        payload["serial"] = serial
        response = requests.post(url, data=payload,headers=headers)
        response_json = response.json()
        print(response_json)
        if response_json: 
            data = dict(response_json)
            insert_data = []
            for i in range(288, 0, -1):
                response = data[f"Entry{i}"]
                row = dict()
                row["serial"] = response["serial"]
                row["localTimeOnSite"] = response["localTimeOnSite"]
                parameters = response["parameters"].keys()
                for parameter in parameters:
                    row[parameter] = response["parameters"][parameter]
                id +=1
                row["response_id"] = id
                insert_data.append(row)
    
            df = pd.DataFrame(insert_data)
            df["localTimeOnSite"] = pd.to_datetime(df["localTimeOnSite"])
            columns = df.columns[2:]
            df[columns] = df[columns].astype(float).round(2)
            job = client.load_table_from_dataframe(df, f"{project_name}.{database_name}.{response_table_name}", job_config=job_config)
        else:
            print("response_json is empty")


def updateActive():
    updateFalse = f"UPDATE {project_name}.{database_name}.{device_table_name} SET active = false WHERE true;"
    client.query(updateFalse)
    query = f"SELECT t.* FROM depa-smartcity-thailand.fahfon.response_table t JOIN (SELECT serial, MAX(localTimeOnSite) as latestLocalTimeOnSite, MAX(response_id) as maxresponse_id FROM depa-smartcity-thailand.fahfon.response_table GROUP BY serial) maxTimes ON t.serial = maxTimes.serial AND t.localTimeOnSite = maxTimes.latestLocalTimeOnSite AND t.response_id = maxTimes.maxresponse_id INNER JOIN depa-smartcity-thailand.fahfon.device_table d ON t.serial = d.serial;"
    results = client.query(query)
    active = []
    for result in results:
        if result["localTimeOnSite"] > datetime.now() - timedelta(days=1):
            active.append(result["serial"])


def downloadData(serial):
    query = f"SELECT * FROM {project_name}.{database_name}.{response_table_name} WHERE serial = '{serial}' ORDER BY localTimeOnSite ASC;"
    data = client.query(query)
    csv_content = StringIO()
    dropped_key= ["serial", "response_id"]
    writer = csv.DictWriter(csv_content, fieldnames=["localTimeOnSite","temp","relativeHumidity","barometricPressure","rainfall","windSpeed","windDirection","redLightIntensity","greenLightIntensity","blueLightIntensity","nearInfraredLightIntensity","lightIntensity","UVIndex","PM1dot0","PM2dot5","PM4","PM10","CO2"])
    writer.writeheader()
    for row in data:
        row = dict(row)
        del row["serial"]
        del row["response_id"]
        writer.writerow(row)
    return csv_content.getvalue()

def getGraph(serial):
    query = f"SELECT * FROM {project_name}.{database_name}.{response_table_name} WHERE serial = '{serial}' ORDER BY localTimeOnSite DESC limit 288;"
    results = list(client.query(query))
    ret = {
        "labels": [],
        "xscale": [],
        "fields":[],
        "data": dict() # Dictionary of list
    }
    keys = list(dict(results[0]).keys())
    keys.remove("serial")
    keys.remove("localTimeOnSite")
    ret["fields"] =[
        {
        "option":"temp",
        "img": None,
        "display": "Temperature"
        },
        {
        "option":"relativeHumidity",
        "img": None,
        "display": "Humidity"
        },
        {
        "option":"barometricPressure",
        "img": None,
        "display": "Pressure"
        },
        {
        "option":"rainfall",
        "img": None,
        "display": "Rainfall"
        },
        {
        "option":"windSpeed",
        "img": None,
        "display": "Wind Speed"
        },
        {
        "option":"windDirection",
        "img": None,
        "display": "Wind Direction"
        },
        {
        "option":"redLightIntensity",
        "img": None,
        "display": "Red Light Intensity"
        },
        {
        "option":"greenLightIntensity",
        "img": None,
        "display": "Green Light Intensity"
        },
        {
        "option":"blueLightIntensity",
        "img": None,
        "display": "Blue Light Intensity"
        },
        {
        "option":"nearInfraredLightIntensity",
        "img": None,
        "display": "Near Infrared"
        },
        {
        "option":"lightIntensity",
        "img": None,
        "display": "Light Intensity"
        },
        {
        "option":"UVIndex",
        "img": None,
        "display": "UV Index"
        },
        {
        "option":"PM1dot0",
        "img": None,
        "display": "PM 1.0"
        },
        {
        "option":"PM2dot5",
        "img": None,
        "display": "PM 2.5"
        },
        {
        "option":"PM4",
        "img": None,
        "display": "PM 4"
        },
        {
        "option":"PM10",
        "img": None,
        "display": "PM 10"
        },
        {
        "option":"CO2",
        "img": None,
        "display": "Carbon dioxide"
        }
    ]
    for result in reversed(results):
        for key in keys:
            if key not in ret["data"]:
                ret["data"][key] = []
            ret["data"][key].append(result[key])
        ret["labels"].append(result["localTimeOnSite"])
    xscale = ["" for label in ret["labels"]]
    xscale = [item if (i) % 12 == 0 else "" for i, item in enumerate(ret["labels"])]
    ret["xscale"] = xscale
    return ret
