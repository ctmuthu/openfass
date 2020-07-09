import os
import json
from subprocess import Popen, PIPE

def ssh(master_ip, cmd):
    try:
        ssh = Popen(["ssh", "-i", "~/.ssh/id_rsa", "-o", "StrictHostKeyChecking=no", '{}@{}'.format("ubuntu",master_ip), cmd], shell=False,
                       stdout=PIPE,
                       stderr=PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            error = ssh.stderr.readlines()
            print >>sys.stderr, "ERROR: %s" % error
        else:
            print(result)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    cwd = os.getcwd()

    terraform_dir = os.path.join(cwd, "terraform")
    automation_dir = os.path.join(cwd, "automation")
    datafile = open(os.path.join(automation_dir, 'values.json'), "r")
    datastore = json.loads(datafile.read())
    master_ip = datastore["master_ip"]
    #print(datastore["model_functions"])
    for instance in datastore["model_functions"]:
        function_deployment = "faas-cli "
        function = datastore["model_functions"][instance]["function"]
        print(function["name"])
        if (function["store"] == True):
            function_deployment += "store deploy " + function["name"]
        else:
            function_deployment += "deploy --image=" + function["image"] + " --name=" + function["name"]
        #cmd = "export OPENFAAS_URL=http://127.0.0.1:31112"
        #ssh(master_ip, cmd)
        cmd = "faas-cli login --tls-no-verify --username admin --password $(cat password.txt) --gateway http://127.0.0.1:31112"
        ssh(master_ip, cmd)
        function_deployment += " --gateway http://127.0.0.1:31112"
        cmd = function_deployment
        ssh(master_ip, cmd)
