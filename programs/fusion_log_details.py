from helper_functions import *
import requests
import json
import csv

#Input file
text = '/Users/gvenkata/Documents/ide/python/ai/data/text/yamuna.txt'
scripts = []
with open(text, 'r') as file:
    for line in file:
       scripts.append(line.strip())
file.close()

#Output file
csv_file = "yamuna.csv"
header = ["script_name", "script_profile_name", "execution_id", "created_at", "dut_type", "os_version", "geo", "log_path", "result" ]
try:
    with open(csv_file, 'x', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
except FileExistsError:
    pass

#Get script profiles
for script in scripts:
    prof_resp = requests.get(f"https://inception.juniper.net/fusion/v2/core/get_script_profile_results?_dc=173977832005&script_name={script}")
    prof_results = prof_resp.json()
    print(f"Processing script: {script}")
    for profile in prof_results["results"]:
        profile_name = profile["name"]
        print(f"Processing profile: {profile_name}")
        #Get script execution results of each profile
        exec_resp = requests.get(f"https://inception.juniper.net/fusion/v2/core/get_script_exec_results?ltr=2000&_dc=1739945968897&script_profile_name={profile_name}&image_name_operator=%7C&router_model_operator=%7C&from_date=Sat%2C%2018%20Jan%202025%2018%3A30%3A00%20GMT&to_date=Tue%2C%2018%20Feb%202025%2018%3A00%3A00%20GMT&ltr=10000&page=1")
        exec_results = exec_resp.json()
        no_of_execs = exec_results["num_results"]
        if no_of_execs > 0:
            for exec_result in exec_results["results"]:
                if exec_result["current_state"] == "COMPLETED":
                    script_name = script
                    script_profile_name = profile_name
                    execution_id = exec_result.get("id", None)
                    dut_type = exec_result.get("model", "NA")
                    created_at = exec_result.get("created_at", "NA")
                    os_version = exec_result.get("version", "NA")
                    geo = exec_result.get("data", {}).get("logpath_details", {}).get("geo", "NA")
                    log_path = exec_result.get("data", {}).get("logpath_details", {}).get("log_path", "NA")
                    result = exec_result.get("script_result", "NA")
                    new_row = [script_name, script_profile_name, execution_id, created_at, dut_type, os_version, geo, log_path, result]
                    with open(csv_file, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(new_row)
                        #print("Row added")
