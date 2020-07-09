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
            print ( "ERROR: %s" % error)
        else:
            print(cmd)
    except Exception as e:
        print(e)


def function_deployment(master_ip, instance):
    function_deployment = "faas-cli "
    function = instance["function"]
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
    #k6.k6_run(master_ip, instance)

def delete_function(master_ip, instance):
    function = instance["function"]
    cmd = "faas-cli remove " + function["name"] + " --gateway http://127.0.0.1:31112"
    ssh(master_ip, cmd)
