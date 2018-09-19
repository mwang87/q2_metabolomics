conda-build . \
 -c https://conda.anaconda.org/qiime2/label/r2018.4 \
 -c https://conda.anaconda.org/qiime2 \
 -c https://conda.anaconda.org/conda-forge \
 -c defaults \
 -c https://conda.anaconda.org/bioconda \
 -c https://conda.anaconda.org/biocore \
 --override-channels \
 --python 3.5
