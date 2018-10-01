import unittest
import os
import csv

from q2_metabolomics._method import _create_table_from_task
from q2_metabolomics import import_gnpsnetworkingclustering
from q2_metabolomics import import_gnpsnetworkingclusteringtask
from q2_metabolomics import import_mzmine2


class MetabolomicsTestCase(unittest.TestCase):

    def test_featureloading(self):
        manifest = "q2_metabolomics/tests/data/manifest.tsv"
        sid_map = {}
        with open(manifest) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sid = row["sample_name"]
                filepath = row["filepath"]
                fileidentifier = os.path.basename(os.path.splitext(filepath)[0])
                sid_map[fileidentifier] = sid

        task_id = "cde9c128ec0c48a58e650279f1735dbc"

        _create_table_from_task(task_id, sid_map)

    def test_gnps_import(self):
        import_gnpsnetworkingclusteringtask("q2_metabolomics/tests/data/manifest.tsv", "cde9c128ec0c48a58e650279f1735dbc")

    def test_mzmine2(self):
        import_mzmine2("q2_metabolomics/tests/data/mzminemanifest.csv", "data/mzminefeatures.csv")

    # def test_gnps(self):
    #     gnps_clustering("data/manifest.tsv", "qiime2test", "qiime2test")





if __name__ == '__main__':
    unittest.main()
