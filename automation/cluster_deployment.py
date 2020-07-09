import os
import json
#import shutil

def cluster_deployment():
    cwd = os.getcwd()
    terraform_dir = os.path.join(cwd, "terraform")
    automation_dir = os.path.join(cwd, "automation")
    grafana_dir = os.path.join(cwd, "grafana")
    #shutil.copyfile(os.path.join(terraform_dir, 'var.tfvars'), os.path.join(terraform_dir, 'var_old.tfvars'))
    datafile = open(os.path.join(automation_dir, 'values.json'), "r")
    datastore = json.loads(datafile.read())
    var_file = open(os.path.join(terraform_dir, 'var.tfvars'),"r")
    var_file_content = ""
    for line in var_file:
        line = line.split("=")
        line[1] = datastore["clusterconfig"][line[0]]
        line = '='.join(str(item) for item in line)
        var_file_content += line + '\n'
    var_file.close()
    datafile.close()
    var_file = open(os.path.join(terraform_dir, 'var.tfvars'),"w+")
    var_file.write(var_file_content)
    var_file.close()
    os.chdir(terraform_dir)
    os.system("terraform destroy -var-file=var_old.tfvars -auto-approve && sleep 20 && terraform apply -var-file=var.tfvars -auto-approve && terraform output -json | jq 'with_entries(.value |= .value)' > config.json")
    os.chdir(grafana_dir)
    os.system("terraform destroy --auto-approve && terraform apply --auto-approve")
    os.chdir(cwd)
    #print(cwd)
    configfile = open(os.path.join(terraform_dir, 'config.json'),"r")
    configstore = json.loads(configfile.read())
    datastore["master_ip"] = configstore["master_ip"]
    configfile.close()
    os.remove(os.path.join(automation_dir, 'values.json'))
    datafile = open(os.path.join(automation_dir, 'values.json'), "w")
    json.dump(datastore, datafile, indent=2)