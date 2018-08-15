from qiime2.plugin import Plugin
import qiime2.plugin
from q2_types.feature_table import FeatureTable, Frequency
import q2_metabolomicsgnps

plugin = Plugin(
    name='metabolomicsgnps',
    version=q2_metabolomicsgnps.__version__,
    website='https://gnps.ucsd.edu',
    user_support_text='https://gnps.ucsd.edu',
    package='q2_metabolomicsgnps'
)

plugin.methods.register_function(
    function=q2_metabolomicsgnps.gnps_clustering,
    inputs={},
    parameters={'manifest': qiime2.plugin.Str, 'username': qiime2.plugin.Str, 'password': qiime2.plugin.Str},
    input_descriptions={},
    outputs=[('feature_table', FeatureTable[Frequency])],
    parameter_descriptions={
        'manifest': 'Manifest file for describing information about each file. Headers of sample name and path to file'
    },
    output_descriptions={'feature_table': 'Resulting feature table'},
    name='GNPS Metabolomics BioM Creation',
    description=("Computes feature biom for metabolomics using GNPS"),
    citations=[]
)

plugin.methods.register_function(
    function=q2_metabolomicsgnps.mzmine2_clustering,
    inputs={},
    parameters={'manifest': qiime2.plugin.Str, 'quantificationtable': qiime2.plugin.Str},
    input_descriptions={},
    outputs=[('feature_table', FeatureTable[Frequency])],
    parameter_descriptions={
        'manifest': 'Manifest file for describing information about each file. Headers of sample name and path to file',
        'quantificationtable': 'Quantification Table output from MZMine2'
    },
    output_descriptions={'feature_table': 'Resulting feature table'},
    name='GNPS MZMine2 Quantitification Metabolomics BioM Creation',
    description=("Computes feature biom for metabolomics using MZMine2 and GNPS"),
    citations=[]
)
