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
    cursor.execute('INSERT INTO device_list SELECT distinct device_id,location FROM raw_data')
    conn.commit()
    return None

def loadData(filename="data.csv"):
    conn=connect()
    cursor=conn.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    cursor.execute('DROP TABLE IF EXISTS raw_data')
    cursor.execute('CREATE TABLE raw_data(device_id bigint,user_id bigint,time timestamp,location geography(POINTZ,4326),data jsonb);')
    cursor.execute('CREATE TABLE device_list(device_id bigint,location geography(POINTZ,4326));')

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
    cursor.execute('SELECT device_id,ST_DISTANCE(location,ST_SetSRID(ST_MakePoint(%s,%s),4326)) FROM device_list ORDER BY 2 ASC LIMIT 1',(longitude,latitude))
    data=cursor.fetchone()
    return data[0]
    
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
    cursor.execute('SELECT device_id,data FROM raw_data')
    for entry in cursor.fetchall():
        device=entry[0]
        data=entry[1]['temperature']['value']
        unit=entry[1]['temperature']['units']
        if device not in ret:
            ret[device]=[]
        ret[device].append(data)
    for device in ret:
        data=ret[device]
        average=sum(data)/len(data)
        print("Device number {0} had an average temperature of {1}".format(device,average))
    return None

if __name__ == '__main__':
    fire.Fire({"writeConfig":writeConfig,"loadData":loadData,"getAllData":getAllData,"getAverageTemperatures":getAverageTemperatures,"populateDevices":populateDevices,"getNearestDevice":getNearestDevice,"getDeviceAverage":getDeviceAverage,"runSQL":runSQL})

