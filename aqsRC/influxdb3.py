#### achtung, löschen in influx3 geht nicht, nur ändern, daher status 
import influxdb_client_3
from influxdb_client_3 import  InfluxDBClient3, Point
import pandas as pd
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import numpy as np

# ts = datetime(2026, 2, 8, 12, 0, 20, tzinfo=timezone.utc)

start_local = "2026-02-08 13:00:00"
end_local   = "2026-02-08 13:05:00"

# 3. Umwandlung in UTC-Objekte
def to_utc_string(date_str):
    dt_local = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin"))
    return dt_local.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%SZ')

token="apiv3_9VluWnloSdt5Dc15Vsv7tPYSjTziY7gnR7a1dw2kd3eJrpX_ypqgjDo2ox98NsYxJ6vOTGBz2upOE3weSm9-4w"

client = InfluxDBClient3(
    host="http://192.168.178.40:8181",
    token="apiv3_9VluWnloSdt5Dc15Vsv7tPYSjTziY7gnR7a1dw2kd3eJrpX_ypqgjDo2ox98NsYxJ6vOTGBz2upOE3weSm9-4w",
    org="mhlan",
    database="local_system"
)


def recalculate():
    
    query ="""
    SELECT *
    FROM "aqs" 
    WHERE "topic"='aqs6' and "time" >= '2026-02-09T22:15:00Z' AND "time" <= '2026-02-09T22:20:30Z'
    """

    table = client.query(query=query, language="sql")
    # for row in table:
    #     print(row)

    df = table.to_pandas()
    # df.drop('R', axis=1, inplace=True)    
    # df['status'] = 0
    df['R'] = 7.
    
    df.set_index('time', inplace=True)
    
    client.write(
        record=df,
        data_frame_measurement_name="aqs",
        data_frame_tag_columns=["topic", "host"]
    )

# one_minute = timedelta(minutes=1)
one_second = timedelta(seconds=1)

def to_utc(start_local, end_local=None, dts=0, tz=ZoneInfo("Europe/Berlin")):
    if dts==0:
        dt_start_ = datetime.strptime(start_local, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        start_utc = dt_start_.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        dt_start_ = datetime.strptime(start_local, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz) - timedelta(seconds=dts)
        start_utc = dt_start_.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%SZ')
        dt_end_ = datetime.strptime(start_local, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz) + timedelta(seconds=dts)
        end_utc = dt_end_.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%SZ')
        return start_utc, end_utc

    if end_local==None:
        return start_utc
    else:
        dt_end_ = datetime.strptime(end_local, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin"))
        end_utc = dt_end_.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%SZ')
        return start_utc, end_utc

start_local = "2026-02-09 12:42:33.160"
end_local   = "2026-02-08 13:05:00"
field = "R"

def set_measure_ko(dtm, dts=1):
    t1,t2 =to_utc(dtm,dts=dts)
    query =f"""
    SELECT *
    FROM "aqs" 
    WHERE "time" >= '{t1}' AND "time" <= '{t2}'
    """
    # WHERE "topic"='aqs6' and "time" >= '{t1}' AND "time" <= '{t2}'

    table = client.query(query=query, language="sql")
    # for row in table:
    #     print(row)

    df = table.to_pandas()
    df['R'] = 0
    
    df.set_index('time', inplace=True)
    
    client.write(
        record=df,
        data_frame_measurement_name="aqs",
        data_frame_tag_columns=["topic", "host"]
    )

def delete(aqs, start_local, end_local):
    start, stop = to_utc(start_local, end_local)
    predicate=f'_measurement="aqs" AND topic="{aqs}"'
    print(start, stop, predicate)
    client.delete(
    start=start,
    stop=stop,
    predicate=predicate
)
    

    pass

def test_tags():
    # 1. Tags abfragen (Indizierte Metadaten)
    tag_query = "SHOW TAG KEYS FROM aqs"
    tags_table = client.query(query=tag_query, language="influxql")
    print("Tags in aqs:", tags_table.to_pandas())
    
    # 2. Fields abfragen (Eigentliche Messwerte wie R, C, T)
    field_query = "SHOW FIELD KEYS FROM aqs"
    fields_table = client.query(query=field_query, language="influxql")
    print("Fields in aqs:", fields_table.to_pandas())    


def test_delete():
    
    query ="""
    DELETE FROM "aqs" 
    WHERE "time" >= '2026-02-09T09:09:00Z' AND "time" <= '2026-02-09T09:09:05Z'
    """
    r = client.query(query=query, language="sql")
    
    
        # WHERE "topic"='aqs6' and "time" >= '2026-02-09T09:09:00Z' AND "time" <= '2026-02-09T09:09:05Z'

    
    # DELETE FROM aqs WHERE time >= ...
    # start = "2026-02-09 13:00:00"
    # aqs = "aqs6"
    #
    # delete(aqs, start_local, end_local)

import requests
def delete_http():

    url = "http://192.168.178.40:8181/api/v3/delete"
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "database": "local_system",
        "start": "2026-02-09T09:09:00Z",
        "stop":  "2026-02-09T09:09:05Z",
        "predicate": "topic = 'aqs6'"
    }
    
    r = requests.post(url, headers=headers, json=payload, timeout=10)
    
    r.raise_for_status()
    print("delete ok")








if __name__ == '__main__':
    # set_measure_ko('2026-02-09 22:29:58', dts=5)
    # delete_http()
    # test_delete()
    # test()
    recalculate()
    pass







