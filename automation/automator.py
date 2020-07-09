import os
import json
from subprocess import Popen, PIPE
import datetime as dt

class Deployment:

    def __init__(self, values_file):
        self.value = values_file
        self.cwd = os.getcwd()
        self.terraform_dir = os.path.join(self.cwd, "terraform")
        self.automation_dir = os.path.join(self.cwd, "automation")
        self.grafana_dir = os.path.join(self.cwd, "grafana")
        self.k6_dir = os.path.join(self.cwd, "k6")

        self.datafile = open(os.path.join(self.automation_dir, self.value), "r")
        self.datastore = json.loads(self.datafile.read())

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
        #k6.k6_run(master_ip, instance)

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
        k6 ="MASTER_IP=" + self.master_ip + " PAYLOAD=" + payload + " FUNCTION=" + function + " k6 run k6_run_script.js"
        for options in self.instance["test"]["k6"]:
            k6 += " --" + options + " " +str(self.instance["test"]["k6"][options])
        start_time = dt.datetime.now()
        start_time = start_time.replace(tzinfo=dt.timezone.utc).timestamp()
        os.system(k6)
        end_time = dt.datetime.now()
        end_time = end_time.replace(tzinfo=dt.timezone.utc).timestamp()
        os.chdir(self.cwd)
        self.datastore["time"]["start"]= str(start_time)
        self.datastore["time"]["end"] = str(end_time)
        self.write_to_json()

    def write_to_json(self):
        os.remove(os.path.join(self.automation_dir, self.value))
        self.datafile = open(os.path.join(self.automation_dir, self.value), "w")
        json.dump(self.datastore, self.datafile, indent=2)
        self.datafile.close()

if __name__ == '__main__':
    Deployment('values.json')