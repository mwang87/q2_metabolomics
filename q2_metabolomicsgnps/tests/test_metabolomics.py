import unittest
import io
import os

from qiime2.plugin.testing import TestPluginBase

from q2_metabolomicsgnps import gnps_clustering


class MetabolomicsGNPSTests(unittest.TestCase):

    def test_gnps(self):
        gnps_clustering("manifest.tsv", "qiime2test", "qiime2test")
