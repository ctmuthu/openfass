import os
import json
import datetime as dt

def k6_run(master_ip, instance):
    cwd = os.getcwd()
    k6_dir = os.path.join(cwd, "k6")
    automation_dir = os.path.join(cwd, "automation")
    os.chdir(k6_dir)
    print(instance)
    function = instance["function"]["name"]
    payload = instance["test"]["function_params"]
    file = instance["test"]["test_run"]
    k6 ="MASTER_IP=" + master_ip + " PAYLOAD=" + payload + " FUNCTION=" + function + " k6 run k6_run_script.js"
    for options in instance["test"]["k6"]:
        k6 += " --" + options + " " +str(instance["test"]["k6"][options])
    start_time = dt.datetime.now()
    start_time = start_time.replace(tzinfo=dt.timezone.utc).timestamp()
    os.system(k6)
    end_time = dt.datetime.now()
    end_time = end_time.replace(tzinfo=dt.timezone.utc).timestamp()
    os.chdir(cwd)
    return start_time, end_time
