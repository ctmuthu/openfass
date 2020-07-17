import os
import json
import yaml
from subprocess import Popen, PIPE
import datetime as dt
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn import linear_model

class Deployment:

    def __init__(self, values_file):
        self.value = values_file
        self.cwd = os.getcwd()
        self.terraform_dir = os.path.join(self.cwd, "terraform")
        self.automation_dir = os.path.join(self.cwd, "automation")
        self.grafana_dir = os.path.join(self.cwd, "grafana")
        self.k6_dir = os.path.join(self.cwd, "k6")
        #self.df = pd.DataFrame()

        self.datafile = open(os.path.join(self.automation_dir, self.value), "r")
        #self.datastore = json.loads(self.datafile.read())
        self.datastore = yaml.load(self.datafile, Loader=yaml.FullLoader)
        #print(self.datastore)
        for instance in self.datastore["model_functions"]:
            self.instance = self.datastore["model_functions"][instance]
            if (self.instance["pre_test"]["cluster_deployment"] == True):
                self.update_tfvars_file()
                self.cluster_deployment()
            self.master_ip = self.datastore["master_ip"]
            if (self.instance["pre_test"]["function_deployment"] == True):
                self.function_deployment()
                self.k6_run()
                self.delete_function()
            if (self.instance["post_test"]["data_extraction"] == True):
                self.query()
            if (self.instance["post_test"]["plot"] == True):
                self.plot()
            if (self.instance["post_test"]["modeling"] == True):
                self.model()
    
    def update_tfvars_file(self):
        var_file = open(os.path.join(self.terraform_dir, 'var.tfvars'),"r")
        var_file_content = ""
        for line in var_file:
            line = line.split("=")
            line[1] = self.datastore["clusterconfig"][line[0]]
            line = '='.join(str(item) for item in line)
            var_file_content += line + '\n'
        var_file.close()
        var_file = open(os.path.join(self.terraform_dir, 'var.tfvars'),"w+")
        var_file.write(var_file_content)
        var_file.close()

    def cluster_deployment(self):
        os.chdir(self.terraform_dir)
        os.system("terraform destroy -var-file=var_old.tfvars -auto-approve && sleep 20 && terraform apply -var-file=var.tfvars -auto-approve && terraform output -json | jq 'with_entries(.value |= .value)' > config.json")
        os.system("cp var.tfvars var_old.tfvars")
        os.chdir(self.grafana_dir)
        os.system("terraform destroy --auto-approve && terraform apply --auto-approve")
        os.chdir(self.cwd)
        #print(cwd)
        configfile = open(os.path.join(self.terraform_dir, 'config.json'),"r")
        configstore = json.loads(configfile.read())
        self.datastore["master_ip"] = configstore["master_ip"]
        self.write_to_json()
    
    def ssh(self, cmd):
        try:
            ssh = Popen(["ssh", "-i", "~/.ssh/id_rsa", "-o", "StrictHostKeyChecking=no", '{}@{}'.format("ubuntu",self.master_ip), cmd], shell=False,
                            stdout=PIPE,
                            stderr=PIPE)
            result = ssh.stdout.readlines()
            if result == []:
                error = ssh.stderr.readlines()
                print ( "ERROR: %s" % error)
            else:
                print(cmd)
        except Exception as e:
            print(e)


    def function_deployment(self):
        function_deployment = "faas-cli "
        function = self.instance["function"]
        print(function["name"])
        if (function["store"] == True):
            function_deployment += "store deploy " + function["name"]
        else:
            function_deployment += "deploy --image=" + function["image"] + " --name=" + function["name"]
        cmd = "faas-cli login --tls-no-verify --username admin --password $(cat password.txt) --gateway http://127.0.0.1:31112"
        self.ssh(cmd)
        function_deployment += " --gateway http://127.0.0.1:31112"
        cmd = function_deployment
        self.ssh(cmd)

    def delete_function(self):
        function = self.instance["function"]
        cmd = "faas-cli remove " + function["name"] + " --gateway http://127.0.0.1:31112"
        self.ssh(cmd)
        os.system("sleep 10")

    def k6_run(self):
        os.chdir(self.k6_dir)
        #print(instance)
        function = self.instance["function"]["name"]
        payload = self.instance["test"]["function_params"]
        file_name = self.instance["test"]["test_run"]
        k6 ="MASTER_IP=" + self.master_ip + " PAYLOAD=" + payload + " FUNCTION=" + function + " k6 run k6_run_script.js --out influxdb=http://138.246.234.122:8086/myk6db"
        for options in self.instance["test"]["k6"]:
            if(type(self.instance["test"]["k6"][options]) == list):
                for i in self.instance["test"]["k6"][options]:
                    k6 += " --" + options + " " +str(i)
            else:
                k6 += " --" + options + " " +str(self.instance["test"]["k6"][options])
        start_time = dt.datetime.now(tz=dt.timezone.utc)
        start_time = start_time.replace(tzinfo=dt.timezone.utc).timestamp()
        print(k6)
        os.system(k6)
        end_time = dt.datetime.now(tz=dt.timezone.utc)
        end_time = end_time.replace(tzinfo=dt.timezone.utc).timestamp()
        os.chdir(self.cwd)
        self.datastore["time"]["start"]= str(start_time)
        self.datastore["time"]["end"] = str(end_time)
        self.write_to_json()

    def query(self):
        self.df = pd.DataFrame()
        for i in self.datastore["query"]:
            url = "http://"+ str(self.datastore["prometheus"]["host"])+ ":" + str(self.datastore["prometheus"]["port"]) + "/" \
                + str(self.datastore["prometheus"]["api"]) + str(self.datastore["query"][i]["query"]) + "&start=" \
                    + str(self.datastore["time"]["start"]) \
                        + "&end=" + str(self.datastore["time"]["end"]) \
                            + "&step=15"
            #print(url)
            receive = requests.get(url)
            self.data_formatter(receive.json(), self.datastore["query"][i]["name"])
        filename = self.instance["function"]["name"] + ".csv"
        self.df.to_csv(os.path.join(self.automation_dir, filename), index=True)

    def data_formatter(self, result, column):
        #print(result["data"]["result"][0]["values"])
        self.time = []
        data = []
        for value in result["data"]["result"][0]["values"]:
            datetime_object = dt.datetime.fromtimestamp(value[0])
            self.time.append(datetime_object)
            data.append(float(value[1]))
        #print(self.time,data)
        self.toTable(column, data)

    def toTable(self, column, data):
        if self.df.empty:
            tableData = {'Time': pd.Series(self.time), column: pd.Series(data)}
            self.df = pd.DataFrame(tableData)
            self.df.set_index("Time", inplace = True)
            self.length = len(self.df.cpu.values)
        else:
            df2 = pd.DataFrame({'Time': pd.Series(self.time), 'Value': pd.Series(data)})
            df2.set_index("Time", inplace = True)
            if (self.length < len(df2.Value.values)):
                df2.drop(df2.index[:len(df2.Value.values)-self.length], inplace=True)
            self.df[column] = df2.Value.values

    def plot(self):
        ax = []
        fig = plt.subplots()
        #print(self.df.columns)
        if len(self.df.columns) <= 4:
            plot_array = "22"
        else:
            plot_array = "33"
        for col in range(0,len(self.df.columns)):
            plt.subplot(int(plot_array+str(col+1)))
            plt.plot(self.df.index,self.df[self.df.columns[col]])
            plt.xlabel(self.df.columns[col])
        filename = self.instance["function"]["name"] + ".png"
        plt.savefig(os.path.join(self.automation_dir, filename))

    def model(self):
        X = self.df[['cpu','mem']] 
        Y = self.df['responsetime']
        regr = linear_model.LinearRegression()
        regr.fit(X, Y)
        print('Intercept: \n', regr.intercept_)
        print('Coefficients: \n', regr.coef_)
        X = sm.add_constant(X)
        model = sm.OLS(Y, X).fit()
        predictions = model.predict(X) 
        print_model = model.summary()
        print(print_model)
        filename = self.instance["function"]["name"] + "_model.txt"
        file = open(os.path.join(self.automation_dir, filename), "w")
        file.write(str(print_model))
        file.close()

    def write_to_json(self):
        os.remove(os.path.join(self.automation_dir, self.value))
        self.datafile = open(os.path.join(self.automation_dir, self.value), "w")
        yaml.dump(self.datastore, self.datafile, indent=4)
        self.datafile.close()

if __name__ == '__main__':
    Deployment('values.yaml')