import sys
import logging
import numpy as np
import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
logger = logging.getLogger(__name__)

def get_train(*args):
    """Get training dataset for CICIDS"""
    return _get_adapted_dataset("train")

def get_test(*args):
    """Get testing dataset for CICIDS"""
    return _get_adapted_dataset("test")

def get_shape_input():
    """Get shape of the dataset for CICIDS"""
    return (None, 121)

def get_shape_label():
    """Get shape of the labels in CICIDS"""
    return (None,)

def _get_dataset():
    """ Gets the basic dataset
    Returns :
            dataset (dict): containing the data
                dataset['x_train'] (np.array): training images shape
                (?, 121)
                dataset['y_train'] (np.array): training labels shape
                (?,)
                dataset['x_test'] (np.array): testing images shape
                (?, 121)
                dataset['y_test'] (np.array): testing labels shape
                (?,)
    """
    import sys
    df=pd.read_csv("/home/notebook/attack_generation/datasets/CICIDS18_Shuffled_Reduced.csv")
    df=df.drop(columns=['Timestamp'])
    df.loc[df["Flow_Pktss"] == "Infinity", "Flow_Pktss"] = 0
    df=df.replace('Infinity', 0)
    df=df.replace('nan', 0)
    df=df.replace('NaN', 0)
    df=df.replace([np.inf, -np.inf], np.nan)
    df=df.fillna(0)
    df=df.replace([np.nan,-np.inf,np.inf], 0)
    df['label'] =df['label'].replace(['normal'],0)
    df.loc[df["label"] !=0, "label"] = 1
    df = df.apply(pd.to_numeric) 
    labels=df['label']
    df=df.drop(columns=['label'])


    enc = OneHotEncoder(handle_unknown='ignore')

    array= pd.DataFrame().assign(A=df['Protocol'],
                             B=df['Fwd_PSH_Flags'],
                             C=df['Bwd_PSH_Flags'], 
                             D=df['Fwd_URG_Flags'],
                             E=df['Bwd_URG_Flags'],
                             F=df['FIN_Flag_Cnt'],
                             G=df['SYN_Flag_Cnt'],
                             H=df['RST_Flag_Cnt'],
                             I=df['PSH_Flag_Cnt'],
                             J=df['ACK_Flag_Cnt'],
                             K=df['URG_Flag_Cnt'],
                             L=df['CWE_Flag_Count'],
                             M=df['ECE_Flag_Cnt'],
                             N=df['DownUp_Ratio'],
                             P=df['Fwd_Bytsb_Avg'],
                             Q=df['Fwd_Pktsb_Avg'],
                             R=df['Fwd_Blk_Rate_Avg'],
                             S=df['Bwd_Bytsb_Avg'],
                             T=df['Bwd_Pktsb_Avg'],
                             U=df['Bwd_Blk_Rate_Avg'],
                            )
    
    enc.fit(array)
    encoded=enc.transform(array).toarray()

    df= df.join(pd.DataFrame(encoded))


    df=df.join(pd.DataFrame(labels))
    df = df.apply(pd.to_numeric) 

    text_l = [] #no textual fields

    for name in text_l:
        _encode_text_dummy(df, name)

    col_names = _col_names1(df)

    df_normal=df[df['label']==0]
    
    df_train = df_normal.sample(frac=0.6, random_state=42)
    df_test = df.loc[~df.index.isin(df_train.index)]

    x_train, y_train = _to_xy(df_train, target='label')
    y_train = y_train.flatten().astype(int)
    x_test, y_test = _to_xy(df_test, target='label')
    y_test = y_test.flatten().astype(int)
    
    x_train = x_train[y_train != 1] #select only NORMAL DATA
    y_train = y_train[y_train != 1] #select only NORMAL DATA

#    scaler = MinMaxScaler()
#    scaler.fit(x_train)
#    scaler.transform(x_train)
#    scaler.transform(x_test)

    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)

    print(x_train.shape)
    print(x_test.shape)
    return dataset

def _get_adapted_dataset(split):
    """ Gets the adapted dataset for the experiments

    Args :
            split (str): train or test
    Returns :
            (tuple): <training, testing> images and labels
    """
    dataset = _get_dataset()
    key_img = 'x_' + split
    key_lbl = 'y_' + split

    if split != 'train':
        dataset[key_img], dataset[key_lbl] = _adapt(dataset[key_img],
                                                    dataset[key_lbl])

    return (dataset[key_img], dataset[key_lbl])

def _encode_text_dummy(df, name):
    """Encode text values to dummy variables(i.e. [1,0,0],[0,1,0],[0,0,1]
    for red,green,blue)
    """
    dummies = pd.get_dummies(df.loc[:,name])
    for x in dummies.columns:
        dummy_name = "{}-{}".format(name, x)
        df.loc[:, dummy_name] = dummies[x]
    df.drop(name, axis=1, inplace=True)

def _to_xy(df, target):
    """Converts a Pandas dataframe to the x,y inputs that TensorFlow needs"""
    result = []
    dummies = df[target]
    result=df.drop(columns=[target])
    return np.array(result), dummies.to_numpy()

def _col_names1(data):
    """Column names of the dataframe"""
    return list(data.columns)

def _col_names():
    """Column names of the dataframe"""
    data=get_dataset()
    return list(data.columns)
        

def _adapt(x, y, rho=0.2):
    """Adapt the ratio of normal/anomalous data"""

    # Normal data: label =0, anomalous data: label =1

    rng = np.random.RandomState(42) # seed shuffling

    inliersx = x[y == 0]
    inliersy = y[y == 0]
    outliersx = x[y == 1]
    outliersy = y[y == 1]

    size_outliers = outliersx.shape[0]
    inds = rng.permutation(size_outliers)
    outliersx, outliersy = outliersx[inds], outliersy[inds]

    size_test = inliersx.shape[0]
    out_size_test = int(size_test*rho/(1-rho))

    outestx = outliersx[:out_size_test]
    outesty = outliersy[:out_size_test]

    testx = np.concatenate((inliersx,outestx), axis=0)
    testy = np.concatenate((inliersy,outesty), axis=0)

    size_test = testx.shape[0]
    inds = rng.permutation(size_test)
    testx, testy = testx[inds], testy[inds]

    return testx, testy
