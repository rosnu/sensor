
from influxdb_client import InfluxDBClient
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import numpy as np
import requests

url = "http://192.168.178.40:8086"
token = "7ZwEipayBBRh6HhUQZaGyRfqm5mEe_OPTeb0N4rqu3YEnsGcq5wp7hKcyWMs3Jk5US8ENv924mbaxAAolTSnFw=="
org = "mhlan"
bucket = "aqs"

dtm_local = "2026-02-16 08:57:36" 
topic="aqs1"

def test():
    client=InfluxDBClient(url=url, token=token, org=org) 
    # Erst prüfen, WELCHE Daten gelöscht würden
    query = f'''
    from(bucket: "aqs")
      |> range(start: {start}, stop: {stop})
      |> filter(fn: (r) => r._measurement == "aqs")
      |> filter(fn: (r) => r.topic == "{topic}")  // Gleicher Filter wie beim Löschen
      |> limit(n: 100)
    '''
    # |> range(start: -30d)
    
    result = client.query_api().query(query)
    for table in result:
        for record in table.records:
            print(f"Zeit: {record.get_time()}, Topic: {record.values.get('topic')}, Field: {record.get_field()}, {record.get_value()}")

def del_http(dtm_start, dtm_end=None, dt=1000, topic=None):
    
    start=to_utc_string(dtm_start, 0)

    if dtm_end==None:
        stop=to_utc_string(dtm_start, dt)
    else:
        stop=to_utc_string(dtm_end, 0)
        
    url_ = f"{url}/api/v2/delete?org={org}&bucket={bucket}"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "start": start,
        "stop": stop,
        "predicate": f'topic="{topic}"'
    }
        # "predicate": '_measurement="__SRC__" AND path="A"'
    response = requests.post(url_, json=payload, headers=headers)

    print(response.text)

ts = datetime(2026, 2, 11, 12, 0, 0, tzinfo=timezone.utc)
ts_de = datetime(2026, 2, 11, 12, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))

start = ts.isoformat()
stop  = ts.isoformat()

start_local = "2026-02-12 05:48:37"
end_local   = "2026-02-12 05:48:39"


def to_utc_string(date_str, dt=0):
    dt_local = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo("Europe/Berlin"))
    dt_local += timedelta(milliseconds=dt)
    ret=dt_local.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
   
    return ret

start=to_utc_string(dtm_local, 0)
stop=to_utc_string(dtm_local, 1000)

def get(dtm_start=None, dtm_end=None, dt=-60*1000, topic=None):
    ft = "%Y-%m-%d %H:%M:%S"
    t = datetime.now().strftime(ft)
    now = to_utc_string(t, 0)
    
    
    start=''
    stop=''
    
    if dtm_start==None:
        start=to_utc_string(now, dt)
    else:
        start=to_utc_string(dtm_start, 0)
        

    if dtm_end==None:
        stop=to_utc_string(now, 0)
    else:
        stop=to_utc_string(dtm_end, 0)


    query=f"SELECT \"u1\", \"uf\" FROM \"aqs\" WHERE \"topic\"::tag = 'aqs6' AND time >= '{start}' and time <= '{stop}' ORDER BY time ASC"

    url_ = url+"/query"
    
    params = {
        "db": "aqs",
        "q": query
    }
    
    headers = {
        "Authorization": f"Token {token}",
    }
    
    r = requests.get(url_, params=params, headers=headers)
    jdata=r.json()
    data=jdata['results'][0]['series'][0]['values']
    # print(r.json())
    
    return data
    
    
###################################

    client=InfluxDBClient(url=url, token=token, org=org) 

    # flux_query = f'''
    # from(bucket: "{bucket}")
    #   |> range(start: -1h)  # Query data from the last hour
    #   |> filter(fn: (r) => r._measurement == "ai1")
    #   |> filter(fn: (r) => r._field == "your_field")
    # '''

    
    result = client.query_api().query(query)
    for table in result:
        for record in table.records:
            print(f"Zeit: {record.get_time()}, Topic: {record.values.get('topic')}, Field: {record.get_field()}, {record.get_value()}")


def del_pt ():
    predicate = 'topic="{topic}"'
    with InfluxDBClient(url=url, token=token, org=org) as client:
        delete_api = client.delete_api()
        delete_api.delete(
            start=start,
            stop=stop,
            predicate=predicate,
            bucket=bucket,
            org=org,
        )
    
    print("done")


topic="aqs1"

def calc_accu():
    data=get("2026-02-26 19:18:03", "2026-02-27 00:17:41", topic="aqs6")
    q=0
    r=36
    for i in range (len(data)-1):
        st0=data[i][0][:-4] + 'Z'
        st1=data[i+1][0][:-4] + 'Z'
        
        t0=datetime.strptime(st0, "%Y-%m-%dT%H:%M:%S.%fZ")
        t1=datetime.strptime(st1, "%Y-%m-%dT%H:%M:%S.%fZ")
        dt=(t1-t0).total_seconds()
        q += dt*(data[i][1]+.2)/r

    Q=q/3600*1000 #mAh

    print(Q)
if __name__ == '__main__':
    calc_accu()
    # get("2026-02-23 09:40:53", "2026-02-24 09:39:28", topic="aqs6");
    # test()
    #del_pt()
    # del_http('2026-02-25 21:24:38', topic='aqs1')
    # del_http('2025-02-24 09:05:26', '2026-02-26 19:16:13', topic='aqs6')
    pass




