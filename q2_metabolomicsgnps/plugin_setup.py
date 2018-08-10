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
    parameters={'spectra': qiime2.plugin.Str},
    input_descriptions={},
    outputs=[('feature_table', FeatureTable[Frequency])],
    parameter_descriptions={
        'spectra': 'Lorem Ipsum.'
    },
    output_descriptions={'feature_table': 'The resulting distance matrix.'},
    name='GNPS Metabolomics BioM Creation',
    description=("Computes stuff for metabolomics"),
    citations=[]
)
