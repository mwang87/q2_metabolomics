from qiime2.plugin import Plugin
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
    parameters={'spectra': 'list of spectra'},
    input_descriptions={
    },
    parameter_descriptions={
        'spectra': 'Lorem Ipsum.'
    },
    output_descriptions={},
    name='GNPS Metabolomics BioM Creation',
    description=("Computes stuff for metabolomics"),
    citations=[]
)
