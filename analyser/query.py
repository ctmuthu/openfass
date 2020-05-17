from influxdb import InfluxDBClient
import sys
import dataformatter as df
import plotter as plot

def printQueryResult(qr):
    print(qr)
    print("\n\n\n\n\n\n")

def execQuery(db, query):
    queryResult = db.query(query)
    dt, value = df.processQueryResult(queryResult)
    #df.plot(dt,value)
    return dt, value

def query(client):
    cpuDT, cpuSec = execQuery(client['prometheus'], "SELECT sum(value) FROM container_cpu_user_seconds_total WHERE time >= 1589705537000ms and time <= 1589706704000ms and image= 'functions/sentimentanalysis@sha256:9c10a0dc910507ef2d549ca2472e03ddde49d095fa0993f2b5d87e4ee538c6e3' group by time(10s) fill(none);")
    cpuDict = df.listsToDict(cpuDT, cpuSec)
    print(cpuDict)
    results = df.newCalculateDifferenceBetweenDatapoints(cpuDict)
    print(results)
    cpuDT, cpuSec = df.transformDicToArrays(results)
    print(cpuDT, cpuSec)
    memDT, memUsage = execQuery(client['prometheus'], "SELECT sum(value) FROM container_memory_usage_bytes WHERE time >= 1589705537000ms and time <= 1589706704000ms and image= 'functions/sentimentanalysis@sha256:9c10a0dc910507ef2d549ca2472e03ddde49d095fa0993f2b5d87e4ee538c6e3' group by time(10s) fill(none);")
    reqDT, reqCount = execQuery(client['myk6db'], "SELECT sum(value) FROM http_reqs WHERE time >= 1589705537000ms and time <= 1589706704000ms GROUP BY time(10s) fill(none);")
    res200DT, res200Count = execQuery(client['prometheus'], "SELECT max(value) FROM gateway_function_invocation_total WHERE time >= 1589705537000ms and time <= 1589706704000ms and code = '200' GROUP BY time(10s) fill(none);")
    res502DT, res502Count = execQuery(client['prometheus'], "SELECT max(value) FROM gateway_function_invocation_total WHERE time >= 1589705537000ms and time <= 1589706704000ms and code = '502' GROUP BY time(10s) fill(none);")
    resDT, resTime = execQuery(client['myk6db'], "SELECT max(value) FROM http_req_duration WHERE time >= 1589705537000ms and time <= 1589706704000ms and value > 0 GROUP BY time(10s) fill(none)")
    memUsage = [value/4000000000 for value in memUsage]
    plot.multiplot(cpuDT, cpuSec, memDT, memUsage, reqDT, reqCount, res200DT, res200Count, res502DT, res502Count, resDT, resTime)

def main(host, port): 
    clientDictionary = {}
    user = 'admin'
    password = 'admin'
    clientDictionary['prometheus'] = InfluxDBClient(host, port, user, password, 'prometheus')
    clientDictionary['myk6db'] = InfluxDBClient(host, port, user, password, 'myk6db')
    query(clientDictionary)
    # query = "show measurements"
    # measurement = client.query(query)

if __name__ == '__main__':
    main(host='138.246.234.122', port='8086')