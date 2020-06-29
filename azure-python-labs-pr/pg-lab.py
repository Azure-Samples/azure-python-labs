import fire
import psycopg2
import csv

def writeConfig(conn_string):
    with open(".conninfo","w") as source:
        source.write(conn_string)
        return "Successfully wrote config file"

def connect():
    with open(".conninfo","r") as source:
        connString=source.readline().strip()
        #return connString
        try:
            conn=psycopg2.connect(connString)
            return conn
        except:
            print("Database connection error")
            return None
def populateDevices():
    conn=connect()
    cursor=conn.cursor()
    cursor.execute('INSERT INTO device_list SELECT distinct device_id,location,location_name FROM raw_data')
    conn.commit()
    return None

def loadData(filename="data.csv"):
    conn=connect()
    cursor=conn.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    cursor.execute('DROP TABLE IF EXISTS raw_data')
    cursor.execute('DROP TABLE IF EXISTS device_list')
    cursor.execute('CREATE TABLE raw_data(device_id bigint,time timestamp,location geography(POINT,4326),data jsonb,location_name text);')
    cursor.execute('CREATE TABLE device_list(device_id bigint,location geography(POINT,4326),location_name text);')

    conn.commit()
    with open(filename,'r') as incoming:
        cursor.copy_expert('COPY raw_data FROM stdin CSV',incoming)
        conn.commit()
        return "Data loaded successfully"

def getAllData():
    ret=dict()
    conn=connect()
    cursor=conn.cursor()
    cursor.execute('SELECT device_id,data FROM raw_data')
    for entry in cursor.fetchall():
        device=entry[0]
        data=entry[1]
        if device not in ret:
            ret[device]=[]
        ret[device].append(data)
    return ret

def getNearestDevice(latitude, longitude):
    conn=connect()
    cursor=conn.cursor()
    cursor.execute('SELECT device_id,location_name,ST_DISTANCE(location,ST_SetSRID(ST_MakePoint(%s,%s),4326)) FROM device_list ORDER BY 3 ASC LIMIT 1',(longitude,latitude))
    data=cursor.fetchone()
    print("Device number {0} in {1} is closest. {2} meters away (approx)".format(data[0],data[1]))
    return None
    
def getDeviceAverage(device):
    conn=connect()
    cursor=conn.cursor()
    cursor.execute("select data -> 'temperature' -> 'units',avg((data -> 'temperature' ->> 'value')::float) from raw_data where device_id = %s group by 1",(device,))
    data=cursor.fetchone()
    return data

def runSQL(statement):
    conn=connect()
    cursor=conn.cursor()
    cursor.execute(statement)
    conn.commit()
    return None

def getAverageTemperatures():
    ret=dict()
    conn=connect()
    cursor=conn.cursor()
    cursor.execute('SELECT device_id,location_name,data FROM raw_data')
    for entry in cursor.fetchall():
        location=entry[1]
        data=entry[2]['temperature']['value']
        unit=entry[2]['temperature']['units']
        if location not in ret:
            ret[location]=[]
        ret[location].append(data)
    for location in ret:
        data=ret[location]
        average=sum(data)/len(data)
        print("{0} had an average temperature of {1}".format(location,average))
    return None

if __name__ == '__main__':
    fire.Fire({"writeConfig":writeConfig,"loadData":loadData,"getAllData":getAllData,"getAverageTemperatures":getAverageTemperatures,"populateDevices":populateDevices,"getNearestDevice":getNearestDevice,"getDeviceAverage":getDeviceAverage,"runSQL":runSQL})

