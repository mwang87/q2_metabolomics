# QIIME 2 Metabolomics GNPS plugin

This is a QIIME 2 plugin to analyze metabolomics data that utilizes GNPS. 

## Installation

Install Qiime2 and activate environment by following the steps described [here] (https://docs.qiime2.org/2018.6/install/native/).

Test if the Qiime2 installation was successful by typing the following command:

`qiime`

If Qiime2 was succesfully installed, options will appear.

Then do the following command to clone the plugin scripts:
`git clone https://github.com/mwang87/q2_metabolomicsgnps`

Finally, move into the just cloned q2_metabolomicsgnps folder and install plugin by executing the command:

`pip install -e`

Or 

`python setup.py install`

Test if the plugin was installed correctly by repeating the following command:

`qiime`

If successful, the metabolomicsgnps plugin is now listed in the options.

## Plugin Commands Listing

`qiime metabolomicsgnps` # Will list out all the commands

`qiime metabolomicsgnps`  gnps-clustering* # MS2 GNPS command

`qiime metabolomicsgnps  mzmine2-clustering` # MZmine2 Feature Import Command

## Example of job GNPS-clustering job:

`qiime metabolomicsgnps gnps-clustering --p-manifest data/manifest.tsv --p-username seedworkshop --p-password seedworkshop --o-feature-table outputfolder`

## Example of MZmine2-CLUSTERING job:

`qiime metabolomicsgnps mzmine2-clustering --p-manifest tests/data/mzminemanifest.csv --p-quantificationtable tests/data/mzminefeatures.csv --o-feature-table feature`

## Input Data Description/Download

### Qiime2 - MZmine export - documentation

A detailed tutorial for feature finding with MZmine2 can be found [here] (https://ccms-ucsd.github.io/GNPSDocumentation/featurebasedmolecularnetworking/).

Download the latest version of [MZmine2] (http://mzmine.github.io/download.html).

Download the default #Bruker Maxis HD qTof# batch file from the section named as #MZMine Batch Steps# from [here] (https://ccms-ucsd.github.io/GNPSDocumentation/featurebasedmolecularnetworking/).

Open the MZmine batch file in MZmine.

Modify the loaded batch file and specify .mzxml file location (raw data import) and signal thresholds.

Modify the export function for the feature table as follows:

1. Specify .csv file name and location
2. Check “Export row ID”, “Export row m/z” and “Export row retention time”
3. Check “Peak area” 
4. Hit OK
5. Run batch

*Screenshot MZmine PNG to be added here*

6. The generated .csv file can now be used directly for further processing in Qiime2.

### Manifest File Format

#### Documentation for manifest file

The manifest file specifies the location of the files that will be processed by the metabolomicsgnps plugin. It is a .CSV formatted table that contains two columns (See Figure X below). The first column indicates the ‘sample-id’ for each file, while the second column indicates its corresponding relative file path (relative to where qiime commands are called). The gnps-clustering and the mzmine2-clustering tools are using both the same manifest file.

Figure X. View of the manifest file (.CSV format). The first column indicates the ‘sample-id’ for each file, while the second column indicates its corresponding relative file path. The example file can be [downloaded here](https://github.com/mwang87/q2_metabolomicsgnps/raw/master/q2_metabolomicsgnps/tests/data/manifest.tsv).


<img src="img/manifest_file.png"/>

## Spectrum Count Qualitative Analysis

### Food Cross Sectional Study

### Longitudinal Study

## Feature Based Quantification Analysis

### Food Cross Sectional Study

### Longitudinal Study

