import biom
import os
from .credentials import *
import ftputil
import requests

def invoke_workflow(base_url, parameters, login, password):
    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload, verify=False)
    r = s.post('https://' + base_url + '/ProteoSAFe/InvokeTools', data=parameters, verify=False)
    task_id = r.text

    print(r.text)

    if len(task_id) > 4 and len(task_id) < 60:
        print("Launched Task: : " + r.text)
        return task_id
    else:
        print(task_id)
        return None

def upload_to_gnps(input_filename, folder_for_spectra, group_name):
    url = "ccms-ftp01.ucsd.edu"

    with ftputil.FTPHost(url, USERNAME, PASSWORD) as ftp_host:
        names = ftp_host.listdir(ftp_host.curdir)
        try:
            if not folder_for_spectra in names:
                print("MAKING DIR")
                ftp_host.mkdir(folder_for_spectra)
        except:
            print("Cannot Make Folder", folder_for_spectra)

        ftp_host.chdir(folder_for_spectra)
        try:
            if not group_name in ftp_host.listdir(ftp_host.curdir):
                print("MAKING Group DIR")
                ftp_host.mkdir(group_name)
        except:
            print("Cannot Make Folder", group_name)
        ftp_host.chdir(group_name)

        ftp_host.upload(input_filename, os.path.basename(input_filename))

def launch_GNPS_workflow(ftp_path, job_description, username, password, email):
    invokeParameters = {}
    invokeParameters["workflow"] = "METABOLOMICS-SNETS-V2"
    invokeParameters["protocol"] = "None"
    invokeParameters["desc"] = job_description
    invokeParameters["library_on_server"] = "d.speclibs;"
    invokeParameters["spec_on_server"] = "d." + ftp_path + "/G1;"
    invokeParameters["tolerance.PM_tolerance"] = "2.0"
    invokeParameters["tolerance.Ion_tolerance"] = "0.5"
    invokeParameters["PAIRS_MIN_COSINE"] = "0.70"
    invokeParameters["MIN_MATCHED_PEAKS"] = "6"
    invokeParameters["TOPK"] = "10"
    invokeParameters["CLUSTER_MIN_SIZE"] = "2"
    invokeParameters["RUN_MSCLUSTER"] = "on"
    invokeParameters["MAXIMUM_COMPONENT_SIZE"] = "100"
    invokeParameters["MIN_MATCHED_PEAKS_SEARCH"] = "6"
    invokeParameters["SCORE_THRESHOLD"] = "0.7"
    invokeParameters["ANALOG_SEARCH"] = "0"
    invokeParameters["MAX_SHIFT_MASS"] = "100.0"
    invokeParameters["FILTER_STDDEV_PEAK_datasetsINT"] = "0.0"
    invokeParameters["MIN_PEAK_INT"] = "0.0"
    invokeParameters["FILTER_PRECURSOR_WINDOW"] = "1"
    invokeParameters["FILTER_LIBRARY"] = "1"
    invokeParameters["WINDOW_FILTER"] = "1"
    invokeParameters["CREATE_CLUSTER_BUCKETS"] = "1"
    invokeParameters["CREATE_ILI_OUTPUT"] = "0"
    invokeParameters["email"] = email
    invokeParameters["uuid"] = "1DCE40F7-1211-0001-979D-15DAB2D0B500"

    task_id = invoke_workflow("gnps.ucsd.edu", invokeParameters, username, password)

    return task_id

def wait_for_workflow_finish(base_url, task_id):
    url = 'https://' + base_url + '/ProteoSAFe/status_json.jsp?task=' + task_id
    json_obj = json.loads(requests.get(url, verify=False).text)
    while (json_obj["status"] != "FAILED" and json_obj["status"] != "DONE" and json_obj["status"] != "SUSPENDED"):
        print("Waiting for task: " + task_id)
        time.sleep(10)
        try:
            json_obj = json.loads(requests.get(url, verify=False).text)
        except KeyboardInterrupt:
            raise
        except:
            print("Exception In Wait")
            time.sleep(1)

    return json_obj["status"]

#def gnps_clustering(spectra: str)->  biom.Table:
def gnps_clustering(spectra: str)-> biom.Table:
    input_files = spectra.split()
    print(input_files)
    for input_filename in input_files:
        upload_to_gnps(input_filename, "TESTQIIME", "G1")
    
    """Launching GNPS Job"""
    task_id = launch_GNPS_workflow(os.path.join("quickstart_GNPS", "TESTQIIME"), "TEST", USERNAME, PASSWORD, "mwang87@gmail.com") 
    print(task_id)

    """Waiting For Job to Finish"""
    wait_for_workflow_to_finish("gnps.ucsd.edu", task_id)

    """Pulling down BioM"""
    url_to_biom = "http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=biom_output"
    local_filepath = "temp.biom"
    local_file = open(local_filepath, "w")
    local_file.write(requests.get(url_to_biom).text)
    local_file.close()


