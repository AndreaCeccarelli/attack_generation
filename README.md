# attack_generation

Repository of the paper *Build intrusion detectors without attack knowledge: strategies and limitations - PER*.

Anonymous version for submission.

PDF submitted, not reported here.

Instructions to reproduce the results of the paper are below.

**INSTALLATION INSTRUCTIONS**

1- install CTGAN from https://github.com/sdv-dev/CTGAN

2- install TGAN from https://github.com/sdv-dev/TGAN

3- install eGAN (ALAD) from https://github.com/houssamzenati/Adversarially-Learned-Anomaly-Detection
3a - replace the files we provide in this repo, in the ALAD folder, with the one provided by the authors. The files are configured to execute ADAFANet and CICIDS18.

4- download ARN from https://github.com/arnwg/arn

5- install the conda environment notebook.yml provided with this github

6- install CICIDS18 and ADFANet datasets. The easiest is to use the versions already prepared by us and available in the zip files adfa.zip and cicids.zip. These are the train-test split we used in the paper. Otherwise, you can re-create them using the jupyter notebooks "zero-day attack generation-ADFA" and "zero-day attack generation-CICIDS" and starting from the CSVs that you can get from CICIDS18 and ADFANet web sites. 

N.B. The train-test splits provided has NO attacks in the training set. All attacks are in the test set. Obviously, to run supervised algorithms, you need to re-balance the train and test. Recommended (very quick) approach is to merge train and test, shuffle, and make a new split.

**CONFIGURATION**

It is necessary to set the proper PATHS. The easiest way is to searchthe tag "notebook"  through all files, and replace the identified paths with your paths. You can also just run and check the error messages. The PATHs should be to directories where you have read and write access.


**EXECUTION**

We recommend to execute with the following order.

1. Execute ALAD (eGAN). Move to the folder where you installed ALAD, and you can execute ALAD on ADFANet and CICIDS respectively with:

python3 main.py  gan adfa run --nb_epochs=20 --label=1 --w=0.1 --m='cross-e' --d=2 --rd=42

python3 main.py  gan cicids run --nb_epochs=35 --label=1 --w=0.1 --m='cross-e' --d=2 --rd=42


2. Execute ARN. It is sufficient to execute the notebooks ADFA-ARN_ADFA_REV_Generation.ipynb and CICIDS-ARN_CICIDS_REV_Generation.ipynb . You should only have to configure PATHS to your own folders.


3. Execute TGAN. This is in the notebook "TABGAN - ADFANet" and "TABGAN - CICIDS". You should only have to configure PATHS to your own folders.

4. Execute all the rest: run the notebooks "attack generation-ADFA" and "attack generation-CICIDS". The notebooks assume that you start from the  ADFANet and CICDS CSV files, but you can use the splits we provide, and load them instead (and remove the initial loading part).


All algorithms will write their results to *adfa_competitors.csv* and *cicids_competitors.csv*. These files will be populated progressively, when you run things.


**CONTACTS**

You are welcome to contact us in case of any problem running the above, or for whatever question about our work.
