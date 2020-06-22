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

def loadData(filename="data.csv"):
    conn=connect()
    cursor=conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS raw_data')
    cursor.execute('CREATE TABLE raw_data(device_id bigint,user_id bigint,time timestamp,location geography(POINTZ,4326),data jsonb);')
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


def getAverageTemperatures():
    ret=dict()
    conn=connect()
    cursor=conn.cursor()
    cursor.execute('SELECT device_id,data FROM raw_data')
    for entry in cursor.fetchall():
        device=entry[0]
        data=entry[1]['temperature']['value']
        unit=entry[1]['temperature']['units']
        if unit=='C':
            #Sometimes, we get the information in Celsius
            data=(data*9/5)+32
        if device not in ret:
            ret[device]=[]
        ret[device].append(data)
    for device in ret:
        data=ret[device]
        average=sum(data)/len(data)
        print("Device number {0} had an average temperature of {1}".format(device,average))
    return None

if __name__ == '__main__':
    fire.Fire({"writeConfig":writeConfig,"loadData":loadData,"getAllData":getAllData,"getAverageTemperatures":getAverageTemperatures})

