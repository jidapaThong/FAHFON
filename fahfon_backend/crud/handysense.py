import pandas as pd
import os
import csv
from io import StringIO
import requests
import json
import decimal
from datetime import datetime
from google.cloud import bigquery
current_directory = os.getcwd()

service_account_key_file = os.path.join(current_directory, "depa-smartcity-thailand.json")
client = bigquery.Client.from_service_account_json(service_account_key_file)
job_config = bigquery.LoadJobConfig()
job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
project_name = "test"
database_name = "test"
device_table_name = "device"
transaction_table_name = "transaction"
response_table_name = "response"

def queryDeviceIDs():
    query = f"SELECT device_id FROM {project_name}.{database_name}.{device_table_name};"
    results = client.query(query)
    ret = []
    for row in results:
        ret.append(row["device_id"])
    return sorted(ret)

def download(deviceID):
    query = f"SELECT time_stamp, temperature, humidity, soil, lux FROM {project_name}.{database_name}.{response_table_name} WHERE response_id in (SELECT response_id FROM {project_name}.{database_name}.{transaction_table_name} where device_id = {deviceID}) ORDER BY time_stamp ASC;"
    data = client.query(query)
    csv_content = StringIO()
    writer = csv.DictWriter(csv_content, fieldnames=["time_stamp", "temperature", "humidity", "soil", "lux"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return csv_content.getvalue()


def get_data(device_id, device_key):
  url = "https://ds.netpie.io/feed/api/v1/datapoints/query"
  headers={
        'Authorization': f"Device {device_id}:{device_key}",
        'Content-Type': 'application/json'
  }
  #Customize the returned body
  payload = json.dumps({
    "start_relative": {
      "value": 1,
      "unit": "days"
    },
    "metrics": [
      {
        "name": f"{device_id}",
        "tags": {
          "attr": [
            "temperature",
            "humidity",
            "soil",
            "lux",
            "led0"
          ]
        },
        "limit": 150000,
        "group_by": [
          {
            "name": "tag",
            "tags": [
              "attr"
            ]
          } 
          ],
        "aggregators":[
          {
          "name":"avg",
          "sampling": {
          "value":"1",
          "unit":"days"
          }
          }
        ]
      }
    ]
  })
  #Send the API
  data = requests.request("POST", url, headers=headers, data=payload)
  print(data.status_code)
  data = data.json()
  print(data)

  results = data["queries"][0]["results"]
  data = {
      "time_stamp": [],
      "temperature": [],
      "humidity": [],
      "soil": [],
      "lux": []
  }
  for result in results:
      time_stamp = []
      tags = dict(result["tags"])
      if not tags:
        return dict()
      attr = result["tags"]["attr"][0]
      values = result["values"]
      for value in values:
          x,y = value #time_stamp and data
          data[attr].append(y)
          time_stamp.append(x)
      data["time_stamp"] = time_stamp
  #Return the data dictionary that is ready to be converted into the DataFrame
  return data

def insert():
  #Get the last response_id for later insertion
  query = f"SELECT MAX(response_id) as last_id FROM {project_name}.{database_name}.{response_table_name};"
  query_ret = client.query(query)
  rows = query_ret.result()
  for row in rows:
    last_id=int(row["last_id"])
  
  df = pd.DataFrame()
  #Get device_id, device_client_id, and device_secret for all devices
  #The device_client_id and device_scret are used for the API Authentication Header
  #The device_id is for transaction_table insertion
  query = f"SELECT device_id, device_client_id, device_secret  FROM {project_name}.{database_name}.{device_table_name};"
  query_ret = client.query(query)
  rows = query_ret.result()

  #Keep device_id for transaction table insertion
  devices = []

  for row in rows:
    device_id = row["device_client_id"]
    device_key = row["device_secret"]
    #call the API for each device
    res = get_data(device_id,device_key)
    if not res:
      continue
    res = pd.DataFrame(res)
    for i in range(len(res)):
      devices.append(row["device_id"])
    #Merge each device DataFrame
    df = pd.concat([df, res])
  
  #Reduce precision of the data so that it can be stored in the Google BigQuery
  #The original data has is too precise (to big)
  for column in df.columns.to_list()[1:]:
    df[column] = df[column].apply(lambda x: round(x, 9))
    df[column] = df[column].astype(str).map(decimal.Decimal)
  
  df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='ms')
  #Convert time from UTC timezone to Thailand timezone
  df["time_stamp"] =  df["time_stamp"]+pd.Timedelta(hours = 7)
  response_id = [last_id + i + 1 for i in range(len(df))]
  df['response_id'] = response_id
  df['response_id'] = df['response_id'].astype(int)

  #Dataframe for Transaction table insertion
  transaction_df = pd.DataFrame({"device_id": devices,"response_id": response_id, "transaction_id": response_id})
  
  for column in transaction_df.columns.to_list():
    transaction_df[column] = transaction_df[column].astype(int)
  
  #Insert into response table
  job = client.load_table_from_dataframe(df, f"{project_name}.{database_name}.{response_table_name}", job_config=job_config)
  #Insert into transaction table
  job = client.load_table_from_dataframe(transaction_df, f"{project_name}.{database_name}.{transaction_table_name}", job_config=job_config)
  
  #Return the list of inserted response_id
  return {"data": response_id}

def updateActive(request):
    #Get max latest response for each device
    query = f"SELECT device_id, MAX(response_id) AS response_id FROM {project_name}.{database_name}.{transaction_table_name} GROUP BY device_id"
    results = client.query(query)
    df1 = {
        "device_id": [],
        "response_id": []
    }
    for result in results:
        df1["device_id"].append(result["device_id"])
        df1["response_id"].append(result["response_id"])
    response_id = df1["response_id"]
    df1 = pd.DataFrame(df1)
    #String for query : The string is in the following format -> (respone_id1,resond_id2,response_id3)
    id_string = ','.join(str(id) for id in response_id)
    #Query time_stamp for each response id retrieved from the previous query
    query = f"SELECT time_stamp, response_id FROM {project_name}.{database_name}.{response_table_name} WHERE response_id in ({id_string})"
    df2 = {
        "time_stamp": [],
        "response_id": []
      }
    results = client.query(query)
    for result in results:
      df2["time_stamp"].append(result["time_stamp"])
      df2["response_id"].append(result["response_id"])
    df2 = pd.DataFrame(df2)
    df2["time_stamp"] = pd.to_datetime(df2["time_stamp"], unit = "ms")
    df = pd.merge(df1, df2, on='response_id')
    #Variables : Devices with the latest response earlier than this are considered inactive
    relative_day = 15
    relative_hour = 0
    #Get current time in Thailand timezone
    now = datetime.now() + pd.Timedelta(hours = 7)
    #Calculate the relative timne
    relative_time = now - pd.Timedelta(hours = relative_hour)- pd.Timedelta(days = relative_day)
    #A column for devices activeness
    df["active"] = df["time_stamp"] > relative_time
    active = df[df["active"] == True]
    inactive = df[df["active"] == False]
    #String for query : The string is in the following format -> (id1,id2,id3)
    active_id_string = ','.join(str(id) for id in list(active["device_id"]))
    inactive_id_string = ','.join(str(id) for id in list(inactive["device_id"]))
    #set active to True
    query = f"UPDATE {project_name}.{database_name}.{device_table_name} SET device_active = 1 where device_id in ({active_id_string})"
    res = client.query(query)
    #set active to False
    query = f"UPDATE {project_name}.{database_name}.{device_table_name} SET device_active = 0 where device_id in ({inactive_id_string})"
    res = client.query(query)
    #Return active devices and inactive devices as string
    return

def queryProject():
    query = f"SELECT DISTINCT project_id from {project_name}.{database_name}.{device_table_name};"
    results = client.query(query)
    ret = []
    for res in results:
        ret.append(res['project_id'])
    return ret

def queryDevices(projectID):
    query = f"SELECT device_id, device_name, device_latitude, device_longtitude, device_address, device_farm_type, device_type, device_active FROM {project_name}.{database_name}.{device_table_name} WHERE project_id = '{projectID}';"
    results = client.query(query)
    devices = []
    id_string = []
    for result in results:
        device = {
        "device_id": result["device_id"],
        "device_name": result["device_name"],
        "device_latitude": result["device_latitude"],
        "device_longtitude": result["device_longtitude"],
        "device_address": result["device_address"],
        "device_farm_type": result["device_farm_type"],
        "device_active": result["device_active"],
        "device_type": result["device_type"]
        }
        devices.append(device)
        df1 = pd.DataFrame(devices)
        id_string.append(result["device_id"])
    id_string = ','.join(str(id) for id in id_string)
    query = f"SELECT device_id, MAX(response_id) AS response_id FROM {project_name}.{database_name}.{transaction_table_name} WHERE device_id in ({id_string}) GROUP BY device_id"
    results = client.query(query)
    id_string = []
    device_id = []
    df2 = []
    for result in results:
        element = {
        "device_id" : result["device_id"],
        "response_id": result["response_id"]
        }
        df2.append(element)
        id_string.append(result["response_id"])
    df2 = pd.DataFrame(df2)
    id_string = ','.join(str(id) for id in id_string)
    query = f"SELECT time_stamp, response_id, temperature, humidity, soil, lux FROM {project_name}.{database_name}.{response_table_name} WHERE response_id in ({id_string})"
    results = client.query(query)
    df3 = []
    for result in results:
        element = {
        "response_id": result["response_id"],
        "time_stamp": result["time_stamp"],
        "temperature": result["temperature"],
        "humidity": result["humidity"],
        "soil": result["soil"],
        "lux": result["lux"]
        }
        df3.append(element)
    df3 = pd.DataFrame(df3)
    df = pd.merge(df2,df3, on="response_id")
    df = pd.merge(df, df1, on="device_id")
    devices = df.to_dict("records")
    return devices
    