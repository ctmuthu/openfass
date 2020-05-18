from datetime import datetime

def listsToDict(x,y):
    resDict = {}
    for i in range(len(x)):
        resDict[x[i]] = y[i]
    return resDict


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
        if firstRound:
            last5thValue = containerSec[item]
            last5thTimeStamp = item
            firstRound = False
        else:
            if every5thItem == 2:
                divider = item - last5thTimeStamp
                value = (containerSec[item] - last5thValue)
                results[item] = (value / divider.total_seconds()) * 100
                last5thValue = containerSec[item]
                last5thTimeStamp = item
                every5thItem = 0
        every5thItem = every5thItem + 1
    return results

def processQueryResult(queryResult):
    dt = []
    value = []
    data = queryResult.get_points()
    for item in data:
        datetime_object = datetime.strptime(item['time'], '%Y-%m-%dT%H:%M:%SZ')
        if(item.get("sum")):
            value.append(item["sum"])
        else:
            value.append(item["max"])
        dt.append(datetime_object)
    return dt, value