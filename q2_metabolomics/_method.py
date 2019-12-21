from biom.table import Table
import biom
import os
import ftputil
from tempfile import NamedTemporaryFile
import requests
import json
import time
import csv
import uuid
import errno
import pandas as pd
import numpy as np
from numpy import ndarray, asarray, zeros, newaxis

def invoke_workflow(base_url, parameters, login, password):
    username = login
    password = password

    s = requests.Session()

    payload = {
        'user': username,
        'password': password,
        'login': 'Sign in'
    }

    r = s.post('https://gnps.ucsd.edu/ProteoSAFe/user/login.jsp',
               data=payload, verify=False)
    r = s.post('https://gnps.ucsd.edu/ProteoSAFe/InvokeTools',
               data=parameters, verify=False)
    task_id = r.text

    print(r.text)

    if len(task_id) > 4 and len(task_id) < 60:
        return task_id
    else:
        return None


def upload_to_gnps(input_filename, folder_for_spectra, group_name, username,
                   password):
    url = "ccms-ftp01.ucsd.edu"

    with ftputil.FTPHost(url, username, password) as ftp_host:
        names = ftp_host.listdir(ftp_host.curdir)
        try:
            if not(folder_for_spectra in names):
                ftp_host.mkdir(folder_for_spectra)
        except:
            print("Cannot Make Folder", folder_for_spectra)

        ftp_host.chdir(folder_for_spectra)
        try:
            if not(group_name in ftp_host.listdir(ftp_host.curdir)):
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

    task_id = invoke_workflow(
        "gnps.ucsd.edu", invokeParameters, username, password)

    return task_id


def wait_for_workflow_finish(base_url, task_id):
    url = 'https://gnps.ucsd.edu/ProteoSAFe/status_json.jsp?task=%s' % (
        task_id)
    exit_status = ["FAILED", "DONE", "SUSPENDED"]

    while True:
        try:
            json_obj = requests.get(url, verify=False).json()
            if json_obj["status"] in exit_status:
                break
        except KeyboardInterrupt:
            raise
        except:
            time.sleep(1)

    if json_obj["status"] == "FAILED" or json_obj["status"] == "SUSPENDED":
        raise ValueError("GNPS Job Failed %s" % (task_id))

    return json_obj["status"]


def import_gnpsnetworkingclustering(manifest: str, credentials: str) -> biom.Table:
    all_rows = []
    sid_map = {}
    with open(manifest) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_rows.append(row)
            sid = row["sample_name"]
            filepath = row["filepath"]
            if not os.path.exists(filepath):
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), filepath)

            fileidentifier = os.path.basename(os.path.splitext(filepath)[0])
            sid_map[fileidentifier] = sid

    remote_folder = str(uuid.uuid4())

    """Reading username and password"""
    credentials = json.loads(open(credentials).read())

    for row in all_rows:
        upload_to_gnps(row["filepath"], "Qiime2", remote_folder,
                       credentials["username"], credentials["password"])

    """Launching GNPS Job"""
    task_id = launch_GNPS_workflow(os.path.join(credentials["username"], "Qiime2", remote_folder), "Qiime2 Analysis %s" % (
        remote_folder), credentials["username"], credentials["password"], "nobody@ucsd.edu")

    if task_id is None:
        raise ValueError('Task Creation at GNPS failed')
    if len(task_id) != 32:
        raise ValueError(
            'Task Creation at GNPS failed with error %s' % (task_id))

    """Waiting For Job to Finish"""
    wait_for_workflow_finish("gnps.ucsd.edu", task_id)

    return _create_table_from_task(task_id, sid_map)


def import_gnpsnetworkingclusteringtask(manifest: str, taskid: str) -> biom.Table:
    wait_for_workflow_finish("gnps.ucsd.edu", taskid)
    sid_map = {}
    with open(manifest) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sid = row["sample_name"]
            filepath = row["filepath"]
            fileidentifier = os.path.basename(os.path.splitext(filepath)[0])
            sid_map[fileidentifier] = sid

    return _create_table_from_task(taskid, sid_map)


def import_gnpsnetworkingclusteringbuckettable(manifest: str, buckettable: str) -> biom.Table:
    sid_map = {}
    with open(manifest) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sid = row["sample_name"]
            filepath = row["filepath"]
            fileidentifier = os.path.basename(os.path.splitext(filepath)[0])
            sid_map[fileidentifier] = sid

    return _create_table_from_buckettable(buckettable, sid_map)


def _create_table_from_task(task_id, sid_map):
    """Pulling down BioM"""
    url_to_biom = "http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=cluster_buckets/" % (
        task_id)
    f = NamedTemporaryFile(delete=False)
    f.close()
    local_file = open(f.name, "w")
    local_file.write(requests.get(url_to_biom).text)
    local_file.close()

    table = _create_table_from_buckettable(f.name, sid_map)

    # Cleanup Tempfile
    os.unlink(f.name)

    return table

def _create_table_from_buckettable(buckettable_path, sid_map):
    with open(buckettable_path) as fh:
        table = biom.Table.from_tsv(fh, None, None, None)

    table.update_ids(sid_map, axis='sample', inplace=True)

    return table

def import_mzmine2(manifest: str, quantificationtable: str) -> biom.Table:
   
    """Loading Manifest Mapping"""
    fff=pd.read_csv(quantificationtable)
    keep_col = ["row ID","row m/z", "row retention time"]#, 'row retention time']
    metadata_df = fff[keep_col] #this is the observation metadata dataframe
    metadata_df = metadata_df.rename(index = str, columns = {"row ID": "#OTU ID","row m/z": "row m/z", "row retention time":"row retention time"})
    sample_metadata_input = metadata_df.to_dict('records') #this is the observation metadata in a list of dict form

    sid_mapping = {}
    with open(manifest) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sid = row["sample_name"]
            filepath = row["filepath"]
            sid_mapping[os.path.basename(filepath)] = sid

    output_list = []
    with open(quantificationtable) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            feature_id = row["row ID"]
            feature_mz = row["row m/z"]
            feature_rt = row["row retention time"]
            output_dict = {}
            output_dict["#OTU ID"] = feature_id

            for header in row:
                if header.find("Peak area") != -1:
                    filepath = os.path.basename(header.replace("Peak area", "").rstrip())
                    sid = sid_mapping[filepath]
                    output_dict[sid] = row[header]

            output_list.append(output_dict)

    f = NamedTemporaryFile(delete=False)
    f.close()
    with open(f.name, "w") as csvfile:
        fieldnames = list(output_list[0].keys())
        fieldnames.remove("#OTU ID")
        fieldnames.insert(0, "#OTU ID")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for output_dict in output_list:
            writer.writerow(output_dict)
    """Reading Into"""
    #temp = metadata_df.T.to_dict("row ID")
    the_df = pd.read_csv(f.name, sep = "\t")
    the_df["#OTU ID"] = the_df["#OTU ID"].apply(str) #This converts the first column of df into string so biom can create qza file
    values = np.array(the_df.values.tolist())
    sample_list = list(the_df) #This is the list of sample_ids
    observation_list = list(the_df.iloc[:,0]) #this is the list of observations 
    data = np.arange(40).reshape(10, 4)
    temp = zip(*data)
    table = Table(values, observation_list, sample_list, observation_metadata = sample_metadata_input)
    #print(len(values))
    #print(len(values[0]))
    #print(len(sample_metadata_input))
    #biom_table_condition_tester(values)
    os.unlink(f.name)
    
    return table

