import requests
import json
import csv

#Input file
input_file = '/Users/gvenkata/Documents/ide/python/ai/data/text/mgb.txt'

#Output files
#Creates a new CSV file to copy details of each execution
detailed_csv = "mgb_exec_details.csv"
details_header = ["script_name", "script_profile_name", "execution_id", "created_at", "exec_duration", "dut_type",
          "os_version", "script_result", "tests_passed", "tests_failed", "untested", "total_tests",
          "retry_count", "num_cores_found", "is_memleak_detected", "log_path", "geo"]
try:
    with open(detailed_csv, 'x', newline='') as d_csvfile:
        writer = csv.writer(d_csvfile)
        writer.writerow(details_header)
except FileExistsError:
    pass

#Creates a new CSV file to copy summary of all executions of each profile
profiles_exec_summary_csv = "mgb_profile_exec_summary.csv"
profiles_summary_header = ["script_name", "profile_name","total_executions", "pass_count", "fail_count", 
                           "other_fail_count", "absolute_pass_percent", "conditional_pass_percent", "fail_percent"]
try:
    with open(profiles_exec_summary_csv, 'x', newline='') as p_csvfile:
        writer = csv.writer(p_csvfile)
        writer.writerow(profiles_summary_header)
except FileExistsError:
    pass

#Creates a new CSV file to copy summary of all executions of each script
script_exec_summary_csv = "mgb_script_exec_summary.csv"
scripts_summary_header = ["script_name", "total_executions", "pass_count", "fail_count", "other_fail_count", "absolute_pass_percent", "conditional_pass_percent", "fail_percent"]
try:
    with open(script_exec_summary_csv, 'x', newline='') as s_csvfile:
        writer = csv.writer(s_csvfile)
        writer.writerow(scripts_summary_header)
except FileExistsError:
    pass

#Get script profiles of each script
def get_script_profiles(scripts):
    for script in scripts:
        total_executions = 0
        passed = 0
        failed = 0
        other_failures = 0
        prof_resp = requests.get(f"https://inception.juniper.net/fusion/v2/core/get_script_profile_results?_dc=173977832005&script_name={script}")
        prof_results = prof_resp.json()
        print(f"Processing script: {script}")
        if "results" in prof_results and len(prof_results["results"]) > 0:
            for profile in prof_results["results"]:
                profile_name = profile["name"]
                # Get script execution results of each profile
                exec_results = get_profile_execution_results(profile_name)
                no_of_execs = exec_results.get("num_results", 0)
                if no_of_execs > 0:
                    tot, pas, fail, others = process_execution_results(script, profile_name, exec_results)
                    total_executions += tot
                    passed += pas
                    failed += fail
                    other_failures += others
        else:
            print(f"No profiles found for script: {script}")
            continue
        if total_executions == 0:
            absolute_pass_percent = 0
            conditional_pass_percent = 0
            fail_percent = 0
        else:
            absolute_pass_percent = (passed / total_executions) * 100
            conditional_pass_percent = ((passed + other_failures)/ total_executions) * 100
            fail_percent = (failed / total_executions) * 100
        summary_row = [script, total_executions, passed, failed, other_failures,
                       round(absolute_pass_percent, 2), round(conditional_pass_percent, 2),
                       round(fail_percent, 2)]
        with open(script_exec_summary_csv, 'a', newline='') as s_csvfile:
            writer = csv.writer(s_csvfile)
            writer.writerow(summary_row)
        
#Get profile executions results of each script
def get_profile_execution_results(profile_name):
    print(f"\tProcessing profile: {profile_name}")
    exec_resp = requests.get(f"https://inception.juniper.net/fusion/v2/core/get_script_exec_results?ltr=2000&_dc=1739867250053&script_profile_name={profile_name}&image_name_operator=%7C&router_model_operator=%7C&interval=&ltr=10000&limit=300&page=1")
    exec_results = exec_resp.json()
    return exec_results

#Processes test execution results and writes to CSV
def process_execution_results(script, profile_name, exec_results):
    passed = 0
    failed = 0
    other_failures = 0
    total_executions = 0
    for exec_result in exec_results["results"]:
        if exec_result["current_state"] == "COMPLETED":
            total_executions += 1
            print(f"\t \t Processing execution: {total_executions}")
            script_name = script
            script_profile_name = profile_name
            execution_id = exec_result.get("id", None)
            created_at = exec_result.get("created_at", None)
            exec_duration = exec_result.get("exec_duration", None)
            dut_type = exec_result.get("model", None)
            os_version = exec_result.get("version", None)
            script_result = exec_result.get("script_result", None)
            if script_result == "PASS":
                passed += 1
            elif script_result == "FAIL":
                failed += 1
            else:
                other_failures += 1
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
                    retry_count, num_cores_found, is_memleak_detected, log_path, geo]
            with open(detailed_csv, 'a', newline='') as d_csvfile:
                writer = csv.writer(d_csvfile)
                writer.writerow(new_row)
    # derive absolute pass percent and handle division by zero
    if total_executions == 0:
        absolute_pass_percent = 0
        conditional_pass_percent = 0
        fail_percent = 0
    else:
        absolute_pass_percent = (passed / total_executions) * 100
        conditional_pass_percent = ((passed + other_failures)/ total_executions) * 100
        fail_percent = (failed / total_executions) * 100
    summary_row = [script, profile_name, total_executions, passed, failed, other_failures, 
                   round(absolute_pass_percent, 2), round(conditional_pass_percent, 2), 
                   round(fail_percent, 2)]
    with open(profiles_exec_summary_csv, 'a', newline='') as p_csvfile:
        writer = csv.writer(p_csvfile)
        writer.writerow(summary_row)
    return total_executions, passed, failed, other_failures

#Get scripts from input file, fetch data from fusion and process
def mgb_script_executions(input_file):
    scripts = []
    with open(input_file, 'r') as file:
        for line in file:
            scripts.append(line.strip())
    file.close()
    get_script_profiles(scripts)

# Run the script
if __name__ == "__main__":
    # Get script profiles and their execution results
    mgb_script_executions(input_file)
    
# This script fetches script profiles and their execution results from a given API and writes them to a CSV file.
# It handles input and output file operations, including creating a new CSV file if it doesn't exist.
# It also includes error handling for file operations and API requests.
# The script is designed to be run as a standalone program, and it prints progress messages to the console.
# The script is modularized into functions for better readability and maintainability.
# The script uses the requests library to make HTTP GET requests to the API and the csv library to handle CSV file operations.
# The script is designed to be run in a Python environment with the requests library installed.
# The script is intended for use in a data processing or ETL (Extract, Transform, Load) pipeline.
