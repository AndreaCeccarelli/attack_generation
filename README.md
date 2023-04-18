# attack_generation

Repository of the paper *Build intrusion detectors without attack knowledge: strategies and limitations - PER*.

Anonymous version for submission.

Instructions to reproduce the results of the paper.

**INSTALLATION INSTRUCTIONS**

1- install CTGAN from https://github.com/sdv-dev/CTGAN

2- install TGAN from https://github.com/sdv-dev/TGAN

3- install eGAN (ALAD) from https://github.com/houssamzenati/Adversarially-Learned-Anomaly-Detection
3a - replace the files we provide in this repo, in the ALAD folder, with the one provided by the authors. The files are configured to execute ADAFANet and CICIDS18.

4- download ARN from https://github.com/arnwg/arn

5- install the conda environment attack.yaml

6- download CICIDS18 and ADFANet datasets. Pre-processed versions are also available, for example you can use the ones provided here in this repository.

**CONFIGURATION**
It is necessary to set the proper PATHS. The easiest way is to search through all files for the tag "notebook", and replace the identified paths with your paths. It is intuitive also if you just run and check the error messages. The PATH should be to a directory where you have read and write access.

All algorithms will write their results to *adfa_competitors.csv* and *cicids_competitors.csv*.

**EXECUTION**

We recommend to execute with the following order.

1. Execute ALAD (eGAN). 

