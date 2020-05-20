from influxdb import InfluxDBClient
import sys
import dataformatter as df
import plotter as plot
import table as tab
import pandas as pd

def printQueryResult(qr):
    print(qr)
    print("\n\n\n\n\n\n")

def execQuery(db, query):
    queryResult = db.query(query)
    #printQueryResult(queryResult)
    dt, value = df.processQueryResult(queryResult)
    #df.plot(dt,value)
    return dt, value

def query(client):
    start_time = "1589972865000ms"
    end_time = "1589975333000ms"
    image = "/fig*/"
    tableData = {}
    cpuDT, cpuSec = execQuery(client['prometheus'], "SELECT mean(value) FROM container_cpu_user_seconds_total WHERE time >= " + start_time + " and time <= " + end_time + " and image =~ " + image + " group by time(1m) fill(0);")
    cpuDict = df.listsToDict(cpuDT, cpuSec)
    results = df.newCalculateDifferenceBetweenDatapoints(cpuDict)
    cpuDT_modified, cpuSec_modified = df.transformDicToArrays(results)
    print(cpuDT_modified, cpuSec_modified)
    memDT, memUsage = execQuery(client['prometheus'], "SELECT mean(value) FROM container_memory_usage_bytes WHERE time >= " + start_time + " and time <= " + end_time + " and image =~ " + image + " group by time(1m) fill(0);")
    reqDT, reqCount = execQuery(client['myk6db'], "SELECT sum(value) FROM http_reqs WHERE time >= " + start_time + " and time <= " + end_time + " GROUP BY time(1m) fill(0);")
    res200DT, res200Count = execQuery(client['prometheus'], "SELECT max(value) FROM gateway_function_invocation_total WHERE time >= " + start_time + " and time <= " + end_time + " and code = '200' GROUP BY time(1m) fill(0);")
    res502DT, res502Count = execQuery(client['prometheus'], "SELECT max(value) FROM gateway_function_invocation_total WHERE time >= " + start_time + " and time <= " + end_time + " and code = '502' GROUP BY time(1m) fill(0);")
    
    res200Dict = df.listsToDict(res200DT, res200Count)
    results = df.newCalculateDifferenceBetweenDatapoints(res200Dict)
    res200DT_modified, res200Count_modified = df.transformDicToArrays(results)

    res502Dict = df.listsToDict(res502DT, res502Count)
    results = df.newCalculateDifferenceBetweenDatapoints(res502Dict)
    res502DT_modified, res502Count_modified = df.transformDicToArrays(results)

    resDT, resTime = execQuery(client['myk6db'], "SELECT mean(value)/60000 FROM http_req_duration WHERE time >= " + start_time + " and time <= " + end_time + " and value > 0 GROUP BY time(1m) fill(0)")
    replicaDT, replicas = execQuery(client['prometheus'],"SELECT mean(value) FROM gateway_service_count WHERE time >= " + start_time + " and time <= " + end_time + " and value > 0 GROUP BY time(1m) fill(0)")
    memUsage_modified = [value/(1024*1024*1024*8) for value in memUsage]
    # datalength = {'cpuDT': len(cpuDT), 'cpuSec': len(cpuSec), 'memDT': len(memDT), 'memUsage_modified': len(memUsage_modified),
    #                 'reqDT': len(reqDT), 'reqCount': len(reqCount), 'res200DT': len(res200DT), 'res200Count': len(res200Count), 'res502DT': len(res502DT), 
    #                    'res502Count': len(res502Count), 'resDT': len(resDT), 'resTime': len(resTime)}
    # print(datalength)
    tableData = {'cpuDT': pd.Series(cpuDT), 'cpuSec': pd.Series(cpuSec), 'memDT': pd.Series(memDT), 'memUsage_modified': pd.Series(memUsage_modified),
                    'reqDT': pd.Series(reqDT), 'reqCount': pd.Series(reqCount), 'res200DT': pd.Series(res200DT), 'res200Count': pd.Series(res200Count), 'res502DT': pd.Series(res502DT), 
                       'res502Count': pd.Series(res502Count), 'resDT': pd.Series(resDT), 'resTime': pd.Series(resTime)}
    tableData = {'Time': pd.Series(memDT), 'Memory': pd.Series(memUsage_modified)}
    tableData1 = {'Time': pd.Series(reqDT), 'reqCount': reqCount}
    tab.toTable(tableData, tableData1)
    plot.multiplot(cpuDT_modified, cpuSec_modified, memDT, memUsage_modified, reqDT, reqCount, res200DT_modified, res200Count_modified, res502DT_modified, res502Count_modified, resDT, resTime, replicaDT, replicas)

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