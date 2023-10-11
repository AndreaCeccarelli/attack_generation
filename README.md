# attack_generation

Repository of the paper *Intrusion detection without attack knowledge: generating Out-of-Distribution tabular data - Practical Experience Report*.

Anonymous version for submission.

PDF submitted, not reported here.

Instructions to reproduce the results of the paper are below.

**INSTALLATION INSTRUCTIONS**

1- install CTGAN from https://github.com/sdv-dev/CTGAN

2- install TGAN from https://github.com/sdv-dev/TGAN

3- install eGAN (ALAD) from https://github.com/houssamzenati/Adversarially-Learned-Anomaly-Detection

3a - use the files we provide in the eGAN folder to replace the ones provided by the eGAN (ALAD) authors. The files are configured to execute ADAFANet and CICIDS18.

4- download and install ARN from https://github.com/arnwg/arn

5- install the conda environment notebook.yml provided with this github

6- get CICIDS18 and ADFANet datasets. The easiest is to use the versions already prepared by us and available in the zip files adfa.zip and cicids.zip. These are the train-test split we used in the paper. Otherwise, you can re-create them using the jupyter notebooks "zero-day attack generation-ADFA" and "zero-day attack generation-CICIDS" and starting from the CSVs. 

N.B. The train-test splits provided has NO attacks in the training set. All attacks are in the test set. Obviously, to run supervised algorithms, you need to re-balance the train and test. In this case, easiest is to use the CSVs (and the code we provided) and make a new train-test split.

**CONFIGURATION**

It is necessary to set the proper PATHS. The easiest way is to search the tag "notebook" through all files, and replace the identified paths with your paths. You can also just run and check the error messages. The PATHs should be to directories where you have read and write access.


**EXECUTION**

We strongly recommend to execute with the following order.

1. Execute ALAD (eGAN). Move to the folder where you installed ALAD, and you can execute ALAD on ADFANet and CICIDS respectively with:

python3 main.py  gan adfa run --nb_epochs=20 --label=1 --w=0.1 --m='cross-e' --d=2 --rd=42

python3 main.py  gan cicids run --nb_epochs=35 --label=1 --w=0.1 --m='cross-e' --d=2 --rd=42

The execution of ALAD will provide results from the ALAD detector in *adfa_competitors.csv* and *cicids_competitors.csv*. Also, it will generate a numpy file that contains generated attacks. This will later used to apply generated attacks togheter with normal data and train supervised and unsupervised algorithms (step 4 below).

2. Execute ARN. It is sufficient to execute the notebooks ADFA-ARN_ADFA_REV_Generation.ipynb and CICIDS-ARN_CICIDS_REV_Generation.ipynb . You should only have to configure PATHS to your own folders.

The execution of ARN will provide results from the ARN detector in *adfa_competitors.csv* and *cicids_competitors.csv*. Also, it will generate a numpy file that contains generated attacks. This will later used to apply generated attacks togheter with normal data and train supervised and unsupervised algorithms (step 4 below).


3. Execute TGAN. This is in the notebook "TABGAN - ADFANet" and "TABGAN - CICIDS". You should only have to configure PATHS to your own folders.

The execution of TGAN will generate a numpy file that contains generated attacks. This will later used to apply generated attacks togheter with normal data and train supervised and unsupervised algorithms (step 4 below).


4. Execute all the rest: run the notebooks "attack generation-ADFA" and "attack generation-CICIDS". The notebooks assume that you start from the  ADFANet and CICDS CSV files, but you can use the splits we provide, and load them instead (and remove the initial loading part).


All algorithms will write their results to *adfa_competitors.csv* and *cicids_competitors.csv*. These files will be populated progressively, when you run things.


**CONTACTS**

You are welcome to contact us in case of any problem running the above, or for whatever question about our work.
