import json
import requests

def query(datasource):
    for i in datastore["query"]:
        print(i)
        print(datastore["query"][i]["name"])
        data = "http://"+ str(datastore["prometheus"]["host"])+ ":" + str(datastore["prometheus"]["port"]) + "/" \
            + str(datastore["prometheus"]["api"]) + str(datastore["prometheus"][query]["query"]) + "&start=" \
                + str(datastore["time"]["start"]) \
                    + "&end=" + str(datastore["time"]["end"]) \
                        + "&step=15"
        receive = requests.get(data)
        print(data)

if __name__ == '__main__':
    datafile = open('automation/values.json', "r")
    datastore = json.loads(datafile.read())
    query(datastore)
    datafile.close()