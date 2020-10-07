import os
import json
import yaml
import time
from subprocess import Popen, PIPE
import datetime as dt
import requests
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn import linear_model
from pylab import rcParams
import telegram


class Deployment:

    def __init__(self, values_file):
        self.value = values_file
        self.cwd = os.getcwd()
        self.output_dir = os.path.join(self.cwd, "OutputtoTelegram")
        self.terraform_dir = os.path.join(self.cwd, "terraform")
        self.automation_dir = os.path.join(self.cwd, "automation")
        self.grafana_dir = os.path.join(self.cwd, "grafana")
        self.k6_dir = os.path.join(self.cwd, "k6")
        self.k3_dir = os.path.join(self.cwd, "k3s")
        # self.df = pd.DataFrame()

        self.datafile = open(os.path.join(self.automation_dir, self.value), "r")
        # self.datastore = json.loads(self.datafile.read())
        self.datastore = yaml.load(self.datafile, Loader=yaml.FullLoader)
        # print(self.datastore)
        for instance in self.datastore["model_functions"]:
            self.instance_name = instance
            self.instance = self.datastore["model_functions"][instance]
            if (self.instance["pre_test"]["cluster_deployment"]):
                self.update_tfvars_file()
                self.cluster_deployment()
            self.master_ip = self.datastore["master_ip"]
            if (self.instance["pre_test"]["function_deployment"]):
                self.function_deployment()
                self.k6_run()
                self.delete_function()
                pass
            if (self.instance["post_test"]["data_extraction"]):
                self.query()
            if (self.instance["post_test"]["plot"]):
                self.plot()
            #if (self.instance["post_test"]["modeling"]):
            #    self.model()
            if (self.instance["pre_test"]["cluster_deployment"]):
                self.destroy_cluster()
            self.telegram_send()

    def update_tfvars_file(self):
        if (self.instance["k8"]):
            var_file = open(os.path.join(self.terraform_dir, 'var.tfvars'),"r")
        else:
            var_file = open(os.path.join(self.k3_dir, 'var.tfvars'),"r")
        var_file_content = ""
        for line in var_file:
            line = line.split("=")
            line[1] = self.instance["clusterconfig"][line[0]]
            line = '='.join(str(item) for item in line)
            var_file_content += line + '\n'
        var_file.close()
        if (self.instance["k8"]):
            var_file = open(os.path.join(self.terraform_dir, 'var.tfvars'),"w+")
        else:
            var_file = open(os.path.join(self.k3_dir, 'var.tfvars'),"w+")
        var_file.write(var_file_content)
        var_file.close()

    def cluster_deployment(self):
        if (self.instance["k8"]):
            os.chdir(self.terraform_dir)
        else:
            os.chdir(self.k3_dir)
        os.system("rm -rf terraform.* && rm -rf .terraform/")
        os.system("terraform init")
        os.system("terraform apply -var-file=var.tfvars -auto-approve && terraform output -json | jq 'with_entries(.value |= .value)' > ../config.json")
        os.system("cp var.tfvars ../var_old.tfvars")
        os.chdir(self.grafana_dir)
        os.system("rm -rf terraform.* && rm -rf .terraform/")
        os.system("terraform init && terraform apply --auto-approve")
        os.chdir(self.cwd)
        # print(cwd)
        configfile = open(os.path.join(self.cwd, 'config.json'),"r")
        configstore = json.loads(configfile.read())
        self.datastore["master_ip"] = configstore["master_ip"]
        self.write_to_json()

    def destroy_cluster(self):
        time.sleep(300)
        if (self.instance["k8"]):
            os.chdir(self.terraform_dir)
        else:
            os.chdir(self.k3_dir)
        os.system("terraform destroy -var-file=../var_old.tfvars -auto-approve")
        time.sleep(300)
    
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
        if (function["name"] == "mydb"):
            self.ssh("cd mysql-function-openfaas/ && kubectl create secret generic secret-mysql-key --from-file=secret-mysql-key=$HOME/secrets/secret_mysql_key.txt --namespace openfaas-fn && faas-cli template pull")
            function_deployment = "cd mysql-function-openfaas/ && sudo faas deploy"
        function_deployment += " --gateway http://127.0.0.1:31112"
        for label in function["openfaas"]:
            function_deployment += " --label '" + label + "=" + str(function["openfaas"][label]) + "'"
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
        k6 ="MASTER_IP=" + self.master_ip + " PAYLOAD=" + payload + " FUNCTION=" + function +  \
            " k6 run " + file_name + " --out influxdb=http://"  \
            + str(self.datastore["database"]["host"])  \
            + ":" + str(self.datastore["database"]["port"]) +"/" + self.datastore["database"]["name"]
        print(k6)
        for options in self.instance["test"]["k6"]:
            if(options == "customized"):
                for m in range(1, self.instance["test"]["k6"][options]["stage"]+1):
                    if(m > 2):
                        m = 2
                    k6 += " --stage" + " 1m:" + str(m)
            elif(type(self.instance["test"]["k6"][options]) == list):
                for i in self.instance["test"]["k6"][options]:
                    k6 += " --" + options + " " +str(i)
            else:
                k6 += " --" + options + " " +str(self.instance["test"]["k6"][options])
        start_time = dt.datetime.now(tz=dt.timezone.utc)
        start_time = start_time.replace(tzinfo=dt.timezone.utc).timestamp()
        #print(k6)
        os.system(k6)
        end_time = dt.datetime.now(tz=dt.timezone.utc)
        end_time = end_time.replace(tzinfo=dt.timezone.utc).timestamp()
        os.chdir(self.cwd)
        self.instance["time"]["start"]= str(start_time)
        self.instance["time"]["end"] = str(end_time)
        self.write_to_json()

    def query(self):
        self.df = pd.DataFrame()
        #print(self.datastore["query"])
        self.datastore["query"]["cpu"]["formatter"] = self.instance["clusterconfig"]["core"]
        self.datastore["query"]["mem"]["formatter"] = 1024*1024*1024*self.instance["clusterconfig"]["memory"]
        self.write_to_json()
        for i in self.datastore["query"]:
            if self.datastore["query"][i]["query_split"] == False:
                url = "http://"+ str(self.datastore["prometheus"]["host"])+ ":" + str(self.datastore["prometheus"]["port"]) + "/" \
                    + str(self.datastore["prometheus"]["api"]) + str(self.datastore["query"][i]["query"]) + "&start=" \
                        + str(self.instance["time"]["start"]) \
                        + "&end=" + str(self.instance["time"]["end"]) \
                        + "&step=" + str(self.datastore["query"][i]["step"])
            else:
                url = "http://"+ str(self.datastore["prometheus"]["host"])+ ":" + str(self.datastore["prometheus"]["port"]) + "/" \
                    + str(self.datastore["prometheus"]["api"]) + str(self.datastore["query"][i]["query"]) \
                        + self.instance["function"]["name"] + str(self.datastore["query"][i]["query1"]) \
                        + str(self.datastore["query"][i]["formatter"]) + "*100&start=" \
                        + str(self.instance["time"]["start"]) \
                        + "&end=" + str(self.instance["time"]["end"]) \
                        + "&step=" + str(self.datastore["query"][i]["step"])
            print(url)
            receive = requests.get(url)
            # print(receive.json())
            self.data_formatter(receive.json(), self.datastore["query"][i]["name"])
        filename = self.instance["function"]["name"] + self.instance["time"]["start"] + "_" + self.instance["time"]["end"] + ".csv"
        self.df.to_csv(os.path.join(self.output_dir, filename), index=True)

    def data_formatter(self, result, column):
        # print(result["data"]["result"][0]["values"])
        self.time = []
        data = []
        try:
            for value in result["data"]["result"][0]["values"]:
                datetime_object = dt.datetime.fromtimestamp(value[0])
                self.time.append(datetime_object)
                data.append(float(value[1]))
                #print(self.time,data)
            self.toTable(column, data)
        except Exception as e:
            print(e)

    def toTable(self, column, data):
        if self.df.empty:
            tableData = {'Time': pd.Series(self.time), column: pd.Series(data)}
            self.df = pd.DataFrame(tableData)
            self.df.set_index("Time", inplace = True)
            self.length = len(self.df.cpu.values)
        else:
            df2 = pd.DataFrame({'Time': pd.Series(self.time), 'Value': pd.Series(data)})
            df2.set_index("Time", inplace = True)
            #print(df2.Value.values)
            if (self.length < len(df2.Value.values)):
                df2.drop(df2.index[:len(df2.Value.values)-self.length], inplace=True)
            print(len(df2.Value.values),self.length)
            if (len(df2.Value.values) < self.length):
                for i in range(len(df2.Value.values), self.length):
                    df_new = pd.DataFrame({'Time': [dt.datetime.now()], 'Value': [1]})
                    df_new.set_index("Time", inplace = True)
                    df2 = df2.append(df_new, ignore_index = True)
            self.df[column] = df2.Value.values

    def plot(self):
        rcParams['figure.figsize'] = 30, 20
        rcParams["legend.loc"] = 'upper left'
        rcParams['axes.labelsize'] = 16
        rcParams['axes.titlesize'] = 20
        rcParams["font.size"] = 16
        ax = []
        fig = plt.subplots()
        #print(self.df.columns)
        filename = self.instance["function"]["name"] + self.instance["time"]["start"] + "_" + self.instance["time"]["end"] + ".csv"
        self.df = pd.read_csv(os.path.join(self.output_dir, filename))
        #self.df.set_index("Time", inplace = True)
        if len(self.df.columns) <= 4:
            fig, axs = plt.subplots(2, 2)
        elif len(self.df.columns) <= 9:
            fig, axs = plt.subplots(3, 3)
            plot_array = "33"
        else:
            fig, axs = plt.subplots(4, 4)
            plot_array = "44"
        for col, ax in zip(range(1,len(self.df.columns)), axs.flatten()):
            ax.plot(self.df.index,self.df[self.df.columns[col]])
            ax.set_title(self.df.columns[col])
        filename = "updated" + self.instance["function"]["name"] + self.instance["time"]["start"] + "_" + self.instance["time"]["end"] + ".png"
        #plt.show()
        plt.savefig(os.path.join(self.output_dir, filename))

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
        filename = self.instance["function"]["name"] + self.instance["time"]["start"] + "_" + self.instance["time"]["end"] + "_model.txt"
        file = open(os.path.join(self.output_dir, filename), "w")
        file.write(str(print_model))
        file.close()

    def write_to_json(self):
        os.remove(os.path.join(self.automation_dir, self.value))
        self.datafile = open(os.path.join(self.automation_dir, self.value), "w")
        yaml.dump(self.datastore, self.datafile, indent=4)
        self.datafile.close()

    def telegram_send(self, chat_id="749187782", token='1300315664:AAGxGYytlA9Dk1xnZjpF7w_qmk-2gbs_2k4'):
        bot = telegram.Bot(token=token)
        filename = self.instance_name + self.instance["function"]["name"] + self.instance["time"]["start"] + "_" + self.instance["time"]["end"] + ".zip"
        copy = "cp " + os.path.join(self.automation_dir, "values.yaml") + " " +self.output_dir
        os.system(copy)
        compress = "tar -zcvf " + filename + " " +self.output_dir
        os.chdir(self.cwd)
        os.system(compress)
        bot.send_document(chat_id=chat_id, document=open(os.path.join(self.cwd, filename), 'rb'))
        for file in os.listdir(self.output_dir):
            if '.png' in file:
                bot.send_photo(chat_id=chat_id, photo=open(os.path.join(self.output_dir, file), 'rb'))
            else:
                bot.sendDocument(chat_id=chat_id, document=open(os.path.join(self.output_dir, file), 'rb'))
        os.system("rm -rf OutputtoTelegram/*")
        delete_tar = "rm -rf " + filename
        os.system(delete_tar)

if __name__ == '__main__':
    Deployment('values.yaml')
