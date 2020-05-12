import matplotlib.pyplot as plt
from influxdb import InfluxDBClient
import array as arr
import math
from datetime import datetime
import pandas as pd

def transformDicToArrays(containerSec):
    xresult = []
    yresult = []
    for item in containerSec:
        xresult.append(item)
        yresult.append(containerSec.get(item,1)/2)
    return xresult, yresult

def newCalculateDifferenceBetweenDatapoints(containerSec):
    firstRound = True
    last5thValue = 0
    last5thTimeStamp = 0
    every5thItem = 0
    results = {}
    for item in containerSec:
        # For getting every the rate of 30 seconds
        if firstRound:
            last5thValue = containerSec[item]
            last5thTimeStamp = item
            firstRound = False
        else:
            if every5thItem == 2:
                # Calculation
                # Cut the last 9 numbers away
                divider = item - last5thTimeStamp
                value = (containerSec[item] - last5thValue)
                # Save to the new map
                results[item] = (value / divider.total_seconds()) * 100
                # Reset with th existing values
                last5thValue = containerSec[item]
                last5thTimeStamp = item
                every5thItem = 0
        every5thItem = every5thItem + 1
    return results

def calcSumFromRow(row):
    result = []
    valueCache = 0
    for item in row:
        if math.isnan(item) == False:
            valueCache = valueCache + item
            result.append(valueCache)
    return result

def removeNan(row):
    result = []
    for item in row:
        if math.isnan(item) == False:
            result.append(item)
    return result

def remove0Values(xresults, yresults):
    newx = []
    newy = []
    counter = 0
    for item in yresults:
        if item != 0:
            newy.append(item)
            newx.append(xresults[counter])
        counter += 1
    return newx, newy

def queryCPUUtil(influxclient, query):
    """Querying CPU Utilization for the given query"""
    containerCPUUserSecondsTotal = {}
    print("Querying data: " + query)
    containerResult = influxclient.query(query)
    containerPoints = containerResult.get_points()

    for item in containerPoints:
        datetime_object = datetime.strptime(item['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        containerCPUUserSecondsTotal[datetime_object] = item['value']
        
    results = newCalculateDifferenceBetweenDatapoints(containerCPUUserSecondsTotal)
    xresult, yresult = transformDicToArrays(results)
    return xresult, yresult

def queryMemoryUsage(influxclient, query):
    """Querying Memory Usage for the given query"""
    memYServer = arr.array('d', [])
    memXServer = []
    print("Querying data: " + query)
    result = influxclient.query(query)
    points = result.get_points()
    for item in points:
        datetime_object = datetime.strptime(item['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        memYServer.append(item['value'] / 4000000000)
        memXServer.append(datetime_object)
    return memXServer, memYServer

"""Querying HTTP Requests"""
def getRequestsDf(clientK6, time):
    queryResult = clientK6.query('SELECT count("value") FROM "vus" group by time(' + time + ');')
    vus = pd.DataFrame(queryResult['vus'])
    vus.columns = ['vus', 'time']
    vus = vus.set_index('time')

    queryResultReqs = clientK6.query('SELECT sum("value") FROM "http_reqs" group by time(' + time + ');')
    reqs = pd.DataFrame(queryResultReqs['http_reqs'])
    reqs.columns = ['requests','time']
    reqs = reqs.set_index('time')
    queryResultReqsDuration95 = clientK6.query('SELECT percentile("value", 95) FROM "http_req_duration" group by time(' + time + ');')
    reqs_duration95 = pd.DataFrame(queryResultReqsDuration95['http_req_duration'])
    reqs_duration95.columns = [ 'requests_duration_percentile_95','time']
    reqs_duration95 = reqs_duration95.set_index('time')
    queryResultReqsDuration90 = clientK6.query('SELECT percentile("value", 90) FROM "http_req_duration" group by time(' + time + ');')
    reqs_duration90 = pd.DataFrame(queryResultReqsDuration90['http_req_duration'])
    reqs_duration90.columns = ['requests_duration_percentile_90','time']
    reqs_duration90 = reqs_duration90.set_index('time')

    queryResultMaxDuration = clientK6.query('SELECT max("value") FROM "http_req_duration" group by time(' + time + ');')
    reqs_duration_max = pd.DataFrame(queryResultMaxDuration['http_req_duration'])
    reqs_duration_max.columns = ['requests_duration_max','time']
    reqs_duration_max = reqs_duration_max.set_index('time')

    queryResultMinDuration = clientK6.query('SELECT min("value") FROM "http_req_duration" group by time(' + time + ');')
    reqs_duration_min = pd.DataFrame(queryResultMinDuration['http_req_duration'])
    reqs_duration_min.columns = ['requests_duration_min','time']
    reqs_duration_min = reqs_duration_min.set_index('time')

    queryResultMeanDuration = clientK6.query('SELECT mean("value") FROM "http_req_duration" group by time(' + time + ');')
    reqs_duration_mean = pd.DataFrame(queryResultMeanDuration['http_req_duration'])
    reqs_duration_mean.columns = ['requests_duration_mean','time']
    reqs_duration_mean = reqs_duration_mean.set_index('time')

    queryResultMedianDuration = clientK6.query('SELECT median("value") FROM "http_req_duration" group by time(' + time + ');')
    reqs_duration_median = pd.DataFrame(queryResultMedianDuration['http_req_duration'])
    reqs_duration_median.columns = ['requests_duration_median','time']
    reqs_duration_median = reqs_duration_median.set_index('time')

    try:
        queryResult500 = clientK6.query('SELECT count(value) FROM "http_req_blocked" WHERE "status" != \'200\' group by time(' + time + ');')
        reqs_500_duration = pd.DataFrame(queryResult500['http_req_blocked'])
        reqs_500_duration.columns = ['requests_500_duration','time']
        reqs_500_duration = reqs_500_duration.set_index('time')
    except:
        print("No errors found")

    finalDF = pd.merge(vus, reqs, left_index=True, right_index=True)
    finalDF = pd.merge(finalDF, reqs_duration95, left_index=True, right_index=True)
    finalDF = pd.merge(finalDF, reqs_duration90, left_index=True, right_index=True)
    finalDF = pd.merge(finalDF,reqs_duration_max, left_index=True, right_index=True)
    finalDF = pd.merge(finalDF,reqs_duration_min, left_index=True, right_index=True)
    finalDF = pd.merge(finalDF,reqs_duration_mean, left_index=True, right_index=True)
    try:
        finalDF = pd.merge(finalDF, reqs_500_duration, left_index=True, right_index=True)
    except:
        print("No errors found")

    finalDF = pd.merge(finalDF,reqs_duration_median, left_index=True, right_index=True)
    finalDF.index = pd.to_datetime(finalDF.index)

    return finalDF