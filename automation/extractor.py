import json
import requests

def query(datasource):
    for i in datastore["query"]:
        url = "http://"+ str(datastore["prometheus"]["host"])+ ":" + str(datastore["prometheus"]["port"]) + "/" \
            + str(datastore["prometheus"]["api"]) + str(datastore["query"][i]["query"]) + "&start=" \
                + str(datastore["time"]["start"]) \
                    + "&end=" + str(datastore["time"]["end"]) \
                        + "&step=15"
        print(url)
        receive = requests.get(url)
        print(receive.json())
        

if __name__ == '__main__':
    datafile = open('automation/values.json', "r")
    datastore = json.loads(datafile.read())
    query(datastore)
    datafile.close()