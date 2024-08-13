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
project_name = "test"
database_name = "test"
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
    serials = ["S1-0000000017", "S1-0000000032", "S1-0000000036","S1-0000000042"]
    url = 'http://www.regis.fahfon.info:8180/uAtTestListInfoBySerial.php'
    payload = {   
        'requestType': 'application/json',
        'uid': 'dapaUAT2',
        'stringKEY': 'val@d0v!n',
        'siteName': 'BANCHANG',
        'lastNdays': '1',
        'maxResult': '288',
        "serial": 'S1-0000000042'
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
        response = requests.post(url, data=payload)
        response_json = response.json()
        print(response_json)
        data = dict(response_json)
        insert_data = []
    
        for i in range(288, 0, -1):
            try:
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
            except Exception:
                pass
        
        df = pd.DataFrame(insert_data)
        df["localTimeOnSite"] = pd.to_datetime(df["localTimeOnSite"])
        columns = df.columns[2:]
        df[columns] = df[columns].astype(float).round(2)
        job = client.load_table_from_dataframe(df, f"{project_name}.{database_name}.{response_table_name}", job_config=job_config)


def updateActive():
    query = f"SELECT serial, localTimeOnSite FROM `depa-smartcity-thailand.fahfon.response_table` where response_id in (SELECT MAX(response_id) as response_id FROM `depa-smartcity-thailand.fahfon.response_table` GROUP BY serial);"
    results = client.query(query)
    active = []
    inactive = []
    for result in results:
        if result["localTimeOnSite"] > datetime.now() - timedelta(days=7):
            active.append(result["serial"])
        else:
            inactive.append(result["serial"])

    active_ids = ",".join("'"+str(id)+"'" for id in active)
    inactive_ids = ",".join("'"+str(id)+"'" for id in inactive)
    query = f"UPDATE {project_name}.{database_name}.{device_table_name} SET active = True WHERE serial in ({active_ids})"
    res  = client.query(query)
    query = f"UPDATE {project_name}.{database_name}.{device_table_name} SET active = False WHERE serial in ({inactive_ids})"
    client.query(query)

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
        "display": "Wind Diraction"
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