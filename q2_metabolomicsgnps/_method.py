import biom
import os
import ftputil
import tempfile
import requests
import json
import time
import csv
import uuid

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
        return task_id
    else:
        return None

def upload_to_gnps(input_filename, folder_for_spectra, group_name, username, password):
    url = "ccms-ftp01.ucsd.edu"

    with ftputil.FTPHost(url, username, password) as ftp_host:
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
    invokeParameters["spec_on_server"] = "d." + ftp_path + ";"
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

def gnps_clustering(manifest: str, username: str, password: str)-> biom.Table:
    all_rows = []
    sid_map = {}
    with open(manifest) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_rows.append(row)
            sid = row["sample-id"]
            filepath = row["filepath"]
            fileidentifier = os.path.basename(os.path.splitext(filepath)[0])
            sid_map[fileidentifier] = sid

    remote_folder = str(uuid.uuid4())

    for row in all_rows:
        upload_to_gnps(row["filepath"], "Qiime2", remote_folder, username, password)

    """Launching GNPS Job"""
    task_id = launch_GNPS_workflow(os.path.join("quickstart_GNPS", "Qiime2", remote_folder), "Qiime2 Analysis %s" % (remote_folder), username, password, "nobody@ucsd.edu")

    if task_id == None:
        print("Error, task creation failed at GNPS")
        exit(1)

    """Waiting For Job to Finish"""
    wait_for_workflow_finish("gnps.ucsd.edu", task_id)

    return _create_table_from_task(task_id, sid_map)

def _create_table_from_task(task_id, sid_map):
    """Pulling down BioM"""
    #task_id = "4ae62800220148f3a664df28ff2dea1d"
    url_to_biom = "http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=cluster_buckets/" % (task_id)
    f = NamedTemporaryFile(delete=False)
    f.close()
    local_file = open(f.name, "w")
    local_file.write(requests.get(url_to_biom).text)
    local_file.close()

    with open(local_filepath) as fh:
        table = biom.Table.from_tsv(fh, None, None, None)

    table.update_ids(sid_map, axis='sample', inplace=True)

    #Cleanup Tempfile
    os.unlink(f.name)

    return table
