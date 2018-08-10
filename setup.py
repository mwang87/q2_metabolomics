from setuptools import setup, find_packages

setup(
    name="q2-metabolomicsgnps",
    version="0.0.1",
    packages=find_packages(),
    author="Mingxun Wang",
    author_email="mwang87@gmail.com",
    description="Lorem Ipsum.",
    license='BSD-3-Clause',
    url="https://gnps.ucsd.edu",
    entry_points={
        'qiime2.plugins': ['q2-metabolomicsgnps=q2_metabolomicsgnps.plugin_setup:plugin']
    }
)
