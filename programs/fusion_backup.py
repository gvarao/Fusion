import requests
import json
import csv

#Input file
text = '/Users/gvenkata/Documents/ide/python/ai/data/text/sample.txt'
scripts = []
with open(text, 'r') as file:
    for line in file:
       scripts.append(line.strip())
file.close()

#Output file
csv_file = "sample.csv"
header = ["script_name", "script_profile_name", "execution_id", "created_at", "exec_duration", "dut_type",
          "os_version", "script_result", "tests_passed", "tests_failed", "untested", "total_tests",
          "retry_count", "num_cores_found", "is_memleak_detected", "log_path", "geo"]
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
        exec_resp = requests.get(f"https://inception.juniper.net/fusion/v2/core/get_script_exec_results?ltr=2000&_dc=1739867250053&script_profile_name={profile_name}&image_name_operator=%7C&router_model_operator=%7C&interval=&ltr=10000&limit=300&page=1")
        exec_results = exec_resp.json()
        no_of_execs = exec_results.get("num_results", 0)
        if no_of_execs > 0:
            for exec_result in exec_results["results"]:
                if exec_result["current_state"] == "COMPLETED":
                    script_name = script
                    script_profile_name = profile_name
                    execution_id = exec_result.get("id", None)
                    created_at = exec_result.get("created_at", None)
                    exec_duration = exec_result.get("exec_duration", None)
                    dut_type = exec_result.get("model", None)
                    os_version = exec_result.get("version", None)
                    script_result = exec_result.get("script_result", None)
                    tests_passed = exec_result.get("testcase_metrics", {}).get("PASS", None)
                    tests_failed = exec_result.get("testcase_metrics", {}).get("FAIL", None)
                    untested = exec_result.get("testcase_metrics", {}).get("UNTESTED", None)
                    total_tests = exec_result.get("testcase_metrics", {}).get("TOTAL", None)
                    retry_count = exec_result.get("retry_count", None)
                    num_cores_found = exec_result.get("num_cores_found", None)
                    is_memleak_detected = exec_result.get("is_memleak_detected", None)                    
                    log_path = exec_result.get("data", {}).get("logpath_details", {}).get("log_path", None)
                    geo = exec_result.get("data", {}).get("logpath_details", {}).get("geo", None)
                    new_row = [script_name, script_profile_name, execution_id, created_at, exec_duration, 
                               dut_type, os_version, script_result, tests_passed, tests_failed, untested, total_tests,
                               retry_count, num_cores_found, is_memleak_detected, log_path, geo,]
                    with open(csv_file, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(new_row)
                        print("Row added")
