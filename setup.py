from setuptools import setup, find_packages

setup(
    name="q2-metabolomicsgnps",
    version="0.0.1",
    packages=find_packages(),
    author="Mingxun Wang",
    author_email="mwang87@gmail.com",
    description="This is a Qiime2 plugin that integrates with GNPS to create BioM tables for metabolomics data.",
    license='BSD-3-Clause',
    url="https://gnps.ucsd.edu",
    entry_points={
        'qiime2.plugins': ['q2-metabolomicsgnps=q2_metabolomicsgnps.plugin_setup:plugin']
    },
    install_requires=["ftputil", "requests", "pandas", "uuid", "biom-format"],
)
