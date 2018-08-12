import unittest
import io
import os
import csv

from qiime2.plugin.testing import TestPluginBase

from q2_metabolomicsgnps._method import _create_table_from_task

class MetabolomicsGNPSTests(unittest.TestCase):
    def test_featureloading(self):
        manifest = "manifest.tsv"
        sid_map = {}
        with open(manifest) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sid = row["sample-id"]
                filepath = row["filepath"]
                fileidentifier = os.path.basename(os.path.splitext(filepath)[0])
                sid_map[fileidentifier] = sid

        task_id = "cde9c128ec0c48a58e650279f1735dbc"

        _create_table_from_task(task_id, sid_map)

    def test_gnps(self):
        gnps_clustering("manifest.tsv", "qiime2test", "qiime2test")
