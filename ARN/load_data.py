import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils import shuffle

def _encode_text_dummy(df, name):
    
    names = []
    dummies = pd.get_dummies(df.loc[:,name])
    i = 0
    
    tmpL = []
    for x in dummies.columns:
        dummy_name = "{}-{}".format(name, x)
        df.loc[:, dummy_name] = dummies[x]
        names.append(dummy_name)
        _x = [i, x]
        tmpL.append(_x)
        i += 1
    
    df.drop(name, axis=1, inplace=True)
    return names, tmpL


def _to_xy(df, target):
    """Converts a Pandas dataframe to the x,y inputs"""
    y = df[target]
    x = df.drop(columns=target)
    return x, y

def removeB(df):
    str_df = df.select_dtypes([np.object])
    str_df = str_df.stack().str.decode('utf-8').unstack()
    
    for col in str_df:
        df[col] = str_df[col]
    
    return df

def get_Bank(PATH, seed, scale = True, show = False, anoIndex = 0, normIndex = 1):
    from scipy.io import arff
    
    data, _ = arff.loadarff(PATH)
    df = pd.DataFrame(data)
    df = removeB(df)
    
    discreteCol = df[df.columns.difference(['y'])].columns.tolist()
    columns = df.columns
    
    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t

    labels = df['y'].copy()
    labels[labels != 'no'] = anoIndex # anomalous
    labels[labels == 'no'] = normIndex # normal

    df['y'] = labels
    normal = df[df['y'] == normIndex] 
    abnormal = df[df['y'] == anoIndex]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)+1]
    abnormal_2 = abnormal[int(len(abnormal)*.5)+1:]


    train_size = 26383
    val_size = 2551

    train_set = normal[:train_size]
    val_normal = normal[train_size: train_size+val_size]
    test_normal = normal[train_size+val_size: ]

    val_size = 580
    test_size = 1740
    val_abnormal = abnormal_1[:val_size]
    test_abnormal = abnormal_1[val_size:val_size+test_size]

    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))
    
    x_train, y_train = _to_xy(train_set, target='y')
    x_val, y_val = _to_xy(val_set, target='y')
    x_test, y_test = _to_xy(test_set, target='y')
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == normIndex])} normal records and {len(x_train[y_train == anoIndex])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == normIndex])} normal records and {len(x_val[y_val == anoIndex])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == normIndex])} normal records and {len(x_test[y_test == anoIndex])} abnormal records')
    
    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp
        
    index = np.arange(0, len(columns)-len(discreteCol)-1)
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['discreteCol'] = discreteCol
    dataset['selectedColumns'] = selected_columns
    dataset['index'] = index
    
    return dataset


def get_KDDCUP99(PATH, seed, scale = True, show = False):
    
    columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land',
        'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised',
        'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
        'num_access_files', 'num_outbound_cmds', 'is_hot_login',
        'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
        'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
        'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
        'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
        'dst_host_srv_serror_rate', 'dst_host_rerror_rate','dst_host_srv_rerror_rate', 'label']
    
    df = pd.read_csv(PATH, header=None, names=columns)
    discreteCol = ['protocol_type', 'service', 'flag', 'land', 'logged_in', 'is_hot_login', 'is_guest_login']
    
    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t

    labels = df['label'].copy()
    labels[labels != 'normal.'] = 0 # anomalous
    labels[labels == 'normal.'] = 1 # normal

    df['label'] = labels
    normal = df[df['label'] == 1] 
    abnormal = df[df['label'] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)+1]
    abnormal_2 = abnormal[int(len(abnormal)*.5)+1:]


    train_size = int(len(normal)*.8)
    val_size = int(len(normal)*.05)+1

    train_set = normal[:train_size]
    val_normal = normal[train_size: train_size+val_size]
    test_normal = normal[train_size+val_size: ]

    val_size = int(len(abnormal_1)*.05)+1
    test_size = int(len(abnormal_1)*.15)+1
    val_abnormal = abnormal_1[:val_size]
    test_abnormal = abnormal_1[val_size:val_size+test_size]

    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))
    
    x_train, y_train = _to_xy(train_set, target='label')
    x_val, y_val = _to_xy(val_set, target='label')
    x_test, y_test = _to_xy(test_set, target='label')
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    index = np.arange(0, len(columns)-len(discreteCol)-1)

    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['oneHot'] = oneHot
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    return dataset


def get_KDDCUP99_INV(PATH, seed, scale = True, show = False):
    
    columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land',
        'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised',
        'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
        'num_access_files', 'num_outbound_cmds', 'is_hot_login',
        'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
        'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
        'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
        'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
        'dst_host_srv_serror_rate', 'dst_host_rerror_rate','dst_host_srv_rerror_rate', 'label']
    
    df = pd.read_csv(PATH, header=None, names=columns)
    discreteCol = ['protocol_type', 'service', 'flag', 'land', 'logged_in', 'is_hot_login', 'is_guest_login']
    
    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t

    labels = df['label'].copy()
    labels[labels != 'normal.'] = 1 # normal
    labels[labels == 'normal.'] = 0 # anomalous

    df['label'] = labels
    normal = df[df['label'] == 1] 
    abnormal = df[df['label'] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)+1]
    abnormal_2 = abnormal[int(len(abnormal)*.5)+1:]

    test_size_ab = int(len(abnormal_1)*(3/4))
    val_size_ab = int(len(abnormal_1)*(1/4))+1

    train_size = 274006
    val_size = 31540

    train_set = normal[:train_size]
    val_normal = normal[train_size: train_size+val_size]
    test_normal = normal[train_size+val_size: ]

    val_abnormal = abnormal_1[:val_size_ab]
    test_abnormal = abnormal_1[val_size_ab:val_size_ab+test_size_ab]

    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))
    
    x_train, y_train = _to_xy(train_set, target='label')
    x_val, y_val = _to_xy(val_set, target='label')
    x_test, y_test = _to_xy(test_set, target='label')
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    index = np.arange(0, len(columns)-len(discreteCol)-1)

    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['oneHot'] = oneHot
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    return dataset


def get_DoH(PATH_B, PATH_M, seed, scale = True, show = False):
    
    columns = ['SourceIP', 'DestinationIP', 'SourcePort', 'DestinationPort',
       'TimeStamp', 'Duration', 'FlowBytesSent', 'FlowSentRate',
       'FlowBytesReceived', 'FlowReceivedRate', 'PacketLengthVariance',
       'PacketLengthStandardDeviation', 'PacketLengthMean',
       'PacketLengthMedian', 'PacketLengthMode', 'PacketLengthSkewFromMedian',
       'PacketLengthSkewFromMode', 'PacketLengthCoefficientofVariation',
       'PacketTimeVariance', 'PacketTimeStandardDeviation', 'PacketTimeMean',
       'PacketTimeMedian', 'PacketTimeMode', 'PacketTimeSkewFromMedian',
       'PacketTimeSkewFromMode', 'PacketTimeCoefficientofVariation',
       'ResponseTimeTimeVariance', 'ResponseTimeTimeStandardDeviation',
       'ResponseTimeTimeMean', 'ResponseTimeTimeMedian',
       'ResponseTimeTimeMode', 'ResponseTimeTimeSkewFromMedian',
       'ResponseTimeTimeSkewFromMode',
       'ResponseTimeTimeCoefficientofVariation', 'Label'] 
    
    benign = pd.read_csv(PATH_B)
    malicious = pd.read_csv(PATH_M)
    
    df = pd.concat([benign, malicious])
    df.drop(columns=['TimeStamp', 'ResponseTimeTimeMedian', 'ResponseTimeTimeSkewFromMedian'], inplace = True)
    discreteCol = ['SourceIP', 'DestinationIP']
    
    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t

    labels = df['Label'].copy()
    labels[labels != 'Benign'] = 0 # anomalous
    labels[labels == 'Benign'] = 1 # normal

    df['Label'] = labels
    normal = df[df['Label'] == 1] 
    abnormal = df[df['Label'] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)]
    abnormal_2 = abnormal[int(len(abnormal)*.5):]

    train_size = int(len(normal)*.8)+1
    val_size = int(len(normal)*.05)
    train_set = normal[:train_size]
    val_normal = normal[train_size: train_size+val_size]
    test_normal = normal[train_size+val_size: ]

    val_size = int(len(abnormal_1)*.05)+1
    test_size = int(len(abnormal_1)*.15)+1
    val_abnormal = abnormal_1[:val_size]
    test_abnormal = abnormal_1[val_size:val_size+test_size]

    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))

    x_train, y_train = _to_xy(train_set, target='Label')
    x_val, y_val = _to_xy(val_set, target='Label')
    x_test, y_test = _to_xy(test_set, target='Label')
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    index = np.arange(0, len(columns)-len(discreteCol)-1)

    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['oneHot'] = oneHot
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    return dataset

def get_DoH_INV(PATH_B, PATH_M, seed, scale = True, show = False):
    
    columns = ['SourceIP', 'DestinationIP', 'SourcePort', 'DestinationPort',
       'TimeStamp', 'Duration', 'FlowBytesSent', 'FlowSentRate',
       'FlowBytesReceived', 'FlowReceivedRate', 'PacketLengthVariance',
       'PacketLengthStandardDeviation', 'PacketLengthMean',
       'PacketLengthMedian', 'PacketLengthMode', 'PacketLengthSkewFromMedian',
       'PacketLengthSkewFromMode', 'PacketLengthCoefficientofVariation',
       'PacketTimeVariance', 'PacketTimeStandardDeviation', 'PacketTimeMean',
       'PacketTimeMedian', 'PacketTimeMode', 'PacketTimeSkewFromMedian',
       'PacketTimeSkewFromMode', 'PacketTimeCoefficientofVariation',
       'ResponseTimeTimeVariance', 'ResponseTimeTimeStandardDeviation',
       'ResponseTimeTimeMean', 'ResponseTimeTimeMedian',
       'ResponseTimeTimeMode', 'ResponseTimeTimeSkewFromMedian',
       'ResponseTimeTimeSkewFromMode',
       'ResponseTimeTimeCoefficientofVariation', 'Label'] 
    
    benign = pd.read_csv(PATH_B)
    malicious = pd.read_csv(PATH_M)
    
    df = pd.concat([benign, malicious])
    df.drop(columns=['TimeStamp', 'ResponseTimeTimeMedian', 'ResponseTimeTimeSkewFromMedian'], inplace = True)
    discreteCol = ['SourceIP', 'DestinationIP']
    
    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t

    labels = df['Label'].copy()
    labels[labels != 'Benign'] = 1 # normal
    labels[labels == 'Benign'] = 0 # anomalous

    df['Label'] = labels
    normal = df[df['Label'] == 1] 
    abnormal = df[df['Label'] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)]
    abnormal_2 = abnormal[int(len(abnormal)*.5):]

    train_size = 184444
    val_size = 15598
    train_set = normal[:train_size]
    val_normal = normal[train_size: train_size+val_size]
    test_normal = normal[train_size+val_size: ]

    val_size = 2475
    test_size = 7427
    val_abnormal = abnormal_1[:val_size]
    test_abnormal = abnormal_1[val_size:val_size+test_size]

    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))

    x_train, y_train = _to_xy(train_set, target='Label')
    x_val, y_val = _to_xy(val_set, target='Label')
    x_test, y_test = _to_xy(test_set, target='Label')
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    index = np.arange(0, len(columns)-len(discreteCol)-1)

    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['oneHot'] = oneHot
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    return dataset


def get_CoverType(PATH, seed, scale = True, show = False):
    
    df = pd.read_csv(PATH, header = None)
    discreteCol = np.arange(10, len(df.columns)-1)
    
    labels = df[54].copy()
    labels.replace({1: 1, 2: 1, 3: 1, 4:0, 5:0, 6:0, 7:0}, inplace = True)
    df[54] = labels

    normal = df[df[54] == 1] 
    abnormal = df[df[54] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)+1]
    abnormal_2 = abnormal[int(len(abnormal)*.5)+1:]

    test_size_ab = int(len(abnormal_1)*(3/4))
    val_size_ab = int(len(abnormal_1)*(1/4))+1

    test_size_n = int(.15 * (len(normal) + len(abnormal_1)) - test_size_ab)
    val_size_n = int(.05 * (len(normal) + len(abnormal_1)) - val_size_ab)

    train_size = int(len(normal) - val_size_n - test_size_n)

    train_set = normal[:train_size]
    val_normal = normal[train_size: train_size+val_size_n]
    test_normal = normal[train_size+val_size_n: ]

    val_abnormal = abnormal_1[:val_size_ab]
    test_abnormal = abnormal_1[val_size_ab:val_size_ab+test_size_ab]

    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))

    x_train, y_train = _to_xy(train_set, target=54)
    x_val, y_val = _to_xy(val_set, target=54)
    x_test, y_test = _to_xy(test_set, target=54)
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        selected_columns[name] = x_train.columns.get_loc(name)
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    index = index = np.arange(0, len(df.columns)-len(discreteCol)-1)

    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    return dataset


def get_CoverTypeRev(PATH, seed, mz = 1/4, my = 3/4, scale = True, show = False):
    
    df = pd.read_csv(PATH, header = None)
    discreteCol = np.arange(10, len(df.columns)-1)
    
    labels = df[54].copy()
    labels.replace({1: 1, 2: 1, 3: 1, 4:0, 5:0, 6:0, 7:0}, inplace = True)
    df[54] = labels
    
    normal = df[df[54] == 1] 
    abnormal = df[df[54] == 0]

    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)+1]
    abnormal_2 = abnormal[int(len(abnormal)*.5)+1:]

    x_size = len(normal) - len(abnormal_1)
    y_size = my * len(abnormal_1)
    z_size = mz * len(abnormal_1)

    train_set = normal[:int(len(normal)*.8)]
    sizeVal = int(np.round((len(normal) - len(normal)*.8)/4))
    val_normal = normal[int(len(normal)*.8): int(len(normal)*.8)+sizeVal]
    test_normal = normal[int(len(normal)*.8)+sizeVal: ]

    val_abnormal = abnormal_1[:int(z_size)+1]
    test_abnormal = abnormal_1[int(z_size)+1:int(z_size)+int(y_size)+2]

    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))

    x_train, y_train = _to_xy(train_set, target=54)
    x_val, y_val = _to_xy(val_set, target=54)
    x_test, y_test = _to_xy(test_set, target=54)
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        selected_columns[name] = x_train.columns.get_loc(name)
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    index = index = np.arange(0, len(df.columns)-len(discreteCol)-1)

    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    return dataset


def get_KDDCUP99_REV(PATH, seed, scale = True, show = False):
    
    columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land',
        'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised',
        'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
        'num_access_files', 'num_outbound_cmds', 'is_hot_login',
        'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
        'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
        'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
        'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
        'dst_host_srv_serror_rate', 'dst_host_rerror_rate','dst_host_srv_rerror_rate', 'label'] 
    
    df = pd.read_csv(PATH, header=None, names=columns)
    discreteCol = ['protocol_type', 'service', 'flag', 'land', 'logged_in', 'is_hot_login', 'is_guest_login']
    
    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t
        
    # Delete nepture, smurf
    df_neptune = df[df['label'] == 'neptune.']
    df_smurf = df[df['label'] == 'smurf.']
    df = df.loc[~df.index.isin(df_neptune.index)]
    df = df.loc[~df.index.isin(df_smurf.index)]

    labels = df['label'].copy()
    labels[labels != 'normal.'] = 0 # anomalous
    labels[labels == 'normal.'] = 1 # normal

    df['label'] = labels
    normal = df[df['label'] == 1] 
    abnormal = df[df['label'] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)]
    abnormal_2 = abnormal[int(len(abnormal)*.5):]

    test_size_ab = int(len(abnormal_1)*(3/4))
    val_size_ab = int(len(abnormal_1)*(1/4))

    test_size_n = int(.15 * (len(normal) + len(abnormal_1)) - test_size_ab + 1)
    val_size_n = int(.05 * (len(normal) + len(abnormal_1)) - val_size_ab + 1)

    train_size = int(len(normal) - val_size_n - test_size_n)+1

    train_set = normal[:train_size]
    val_normal = normal[train_size: train_size+val_size_n]
    test_normal = normal[train_size+val_size_n: ]

    val_abnormal = abnormal[:val_size_ab]
    test_abnormal = abnormal[val_size_ab:val_size_ab+test_size_ab]

    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))

    x_train, y_train = _to_xy(train_set, target='label')
    x_val, y_val = _to_xy(val_set, target='label')
    x_test, y_test = _to_xy(test_set, target='label')
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    index = np.arange(0, len(columns)-len(discreteCol)-1)

    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['oneHot'] = oneHot
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    return dataset

def get_CreditCard(PATH, seed, mz = 1/4, my = 3/4, scale = True, show = False):
    
    df = pd.read_csv(PATH)
    
    labels = df['Class'].copy()
    labels.replace({0: 1, 1: 0}, inplace = True)

    df['Class'] = labels

    normal = df[df['Class'] == 1] 
    abnormal = df[df['Class'] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)
    
    test_size_ab = int(len(abnormal)*(3/4))
    val_size_ab = int(len(abnormal)*(1/4))
    
    test_size_n = int(.15 * (len(normal) + len(abnormal)) - test_size_ab)
    val_size_n = int(.05 * (len(normal) + len(abnormal)) - val_size_ab)
    
    train_size = int(len(normal) - val_size_n - test_size_n)
    
    train_set = normal[:train_size]
    val_normal = normal[train_size: train_size+val_size_n]
    test_normal = normal[train_size+val_size_n: ]
    
    val_abnormal = abnormal[:val_size_ab]
    test_abnormal = abnormal[val_size_ab:val_size_ab+test_size_ab]
    
    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))
    
    x_train, y_train = _to_xy(train_set, target='Class')
    x_val, y_val = _to_xy(val_set, target='Class')
    x_test, y_test = _to_xy(test_set, target='Class')
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train)
        x_train = scaler.transform(x_train)
        x_val = scaler.transform(x_val)
        x_test = scaler.transform(x_test)
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['scaler'] = scaler
    
    return dataset


def get_CreditCard_Rev(PATH, seed, mz = 1/4, my = 3/4, scale = True, show = False):
    
    df = pd.read_csv(PATH)
    
    labels = df['Class'].copy()
    labels.replace({0: 1, 1: 0}, inplace = True)

    df['Class'] = labels

    normal = df[df['Class'] == 1] 
    abnormal = df[df['Class'] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)
    
    x_size = len(normal) - len(abnormal)
    y_size = my * len(abnormal)
    z_size = mz * len(abnormal)
    
    train_set = normal[:int(len(normal)*.8)]
    sizeVal = int(np.round((len(normal) - len(normal)*.8)/4))
    val_normal = normal[int(len(normal)*.8): int(len(normal)*.8)+sizeVal]
    test_normal = normal[int(len(normal)*.8)+sizeVal: ]
    
    val_abnormal = abnormal[:int(z_size)]
    test_abnormal = abnormal[int(z_size):int(z_size)+int(y_size)+1]
    
    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))
    
    x_train, y_train = _to_xy(train_set, target='Class')
    x_val, y_val = _to_xy(val_set, target='Class')
    x_test, y_test = _to_xy(test_set, target='Class')
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train)
        x_train = scaler.transform(x_train)
        x_val = scaler.transform(x_val)
        x_test = scaler.transform(x_test)
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['scaler'] = scaler
    
    return dataset


def get_NSLKDD(PATH_TRAIN, PATH_TEST, seed, mx = 0.889, mz = 0.028, my = 0.083, scale = True, show = False):
    columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land',
        'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised',
        'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
        'num_access_files', 'num_outbound_cmds', 'is_hot_login',
        'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
        'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
        'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
        'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
        'dst_host_srv_serror_rate', 'dst_host_rerror_rate','dst_host_srv_rerror_rate', 'label', 'unknown']
    
    train = pd.read_csv(PATH_TRAIN, delimiter = ',', header = None, names = columns)
    test = pd.read_csv(PATH_TEST, delimiter = ',', header = None, names = columns)
    
    train.drop(columns = ['unknown'], inplace = True)
    test.drop(columns = ['unknown'], inplace = True)
    
    rest = set(train.columns) - set(test.columns)
    for i in rest:
        idx = train.columns.get_loc(i)
        test.insert(loc=idx, column=i, value=0)
    
    
    df = pd.concat((train, test))
    discreteCol = ['protocol_type', 'service', 'flag', 'land', 'logged_in', 'is_hot_login', 'is_guest_login']
    
    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t

    labels = df['label'].copy()
    labels[labels != 'normal'] = 0 # anomalous
    labels[labels == 'normal'] = 1 # normal

    df['label'] = labels
    normal = df[df['label'] == 1] 
    abnormal = df[df['label'] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)+1]
    abnormal_2 = abnormal[int(len(abnormal)*.5)+1:]
    
    train_set = normal[:int(mx*len(normal))]
    val_normal = normal[int(mx*len(normal)): int(mx*len(normal))+int(mz*len(normal))]
    test_normal = normal[int(mx*len(normal))+int(mz*len(normal)): ]
    
    val_abnormal = abnormal_1[:int(mz*len(normal))]
    test_abnormal = abnormal_1[int(mz*len(normal)):int(mz*len(normal))+int(my*len(normal))+1]
    
    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))
    
    x_train, y_train = _to_xy(train_set, target='label')
    x_val, y_val = _to_xy(val_set, target='label')
    x_test, y_test = _to_xy(test_set, target='label')
    
    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    index = np.arange(0, len(columns)-len(discreteCol)-1)

    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['oneHot'] = oneHot
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    return dataset


def get_ADFA(PATH, seed, scale = True, show = True):
    columns = ['packets', 'bytes', 'Duration', 'label']
    df = pd.read_csv(PATH)
    discreteCol = ['packets']#'protocol_type', 'service', 'flag', 'land', 'logged_in', 'is_hot_login', 'is_guest_login']
    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t

    labels = df['label'].copy()
    labels[labels != 'normal'] = 1 # anomalous
    labels[labels == 'normal'] = 0 # normal
    df['label'] = labels
    
    normal = df[df['label'] == 0] 
    abnormal = df[df['label'] == 1]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

#    abnormal_1 = abnormal[:int(len(abnormal)*.5)]
    abnormal_2 = abnormal#[int(len(abnormal)*.5):]

    train_size = int(len(normal)*.6)

    train_set = normal[:train_size]

#    val_normal = normal[train_size: train_size+val_size]
    test_normal = normal[train_size:]

    val_size = 0
    test_size = int(len(abnormal_2))
#    val_abnormal = abnormal_1
    test_abnormal = abnormal_2

#    val_set = val_abnormal
    test_set = pd.concat((test_normal, test_abnormal))
    
    x_train, y_train = _to_xy(train_set, target='label')
    x_val, y_val = _to_xy(train_set, target='label')
    x_test, y_test = _to_xy(test_set, target='label')

    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_2)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 0])} normal records and {len(x_train[y_train == 1])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 0])} normal records and {len(x_val[y_val == 1])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 0])} normal records and {len(x_test[y_test == 1])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp

    x_train = x_train.to_numpy().astype(np.float32)
    x_val = x_val.to_numpy().astype(np.float32)
    x_test = x_test.to_numpy().astype(np.float32)

    index = np.arange(0, len(columns)-len(discreteCol)-1)


    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
#        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
    
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['oneHot'] = oneHot
    dataset['index'] = index
    dataset['scaler'] = scaler

    np.save('/home/notebook/attack_generation/saved_attacks_generated/adfa/ARN_x_train.npy', dataset['x_train'])
    np.save('/home/notebook/attack_generation/saved_attacks_generated/adfa/ARN_y_train.npy', dataset['y_train'])
    np.save('/home/notebook/attack_generation/saved_attacks_generated/adfa/ARN_x_test.npy', dataset['x_test'])
    np.save('/home/notebook/attack_generation/saved_attacks_generated/adfa/ARN_y_test.npy', dataset['y_test'])

    return dataset


def get_CICIDS(PATH, seed, scale = True, show = True):
    
    df = pd.read_csv(PATH)
    df=df.drop('Timestamp', axis=1, inplace=False)
    df=df.replace([np.inf], 0)
    df=df.replace([-np.inf], 0)
    df=df.replace([-np.inf], 0)
    df=df.fillna(0)

    columns = list(df.columns)

#['packets', 'bytes', 'Duration', 'label']
#    df = pd.read_csv(PATH)
#    discreteCol = ['packets']#'protocol_type', 'service', 'flag', 'land', 'logged_in', 'is_hot_login', 'is_guest_login']
    discreteCol = ['Protocol','Fwd_PSH_Flags','Bwd_PSH_Flags','Fwd_URG_Flags', 'Bwd_URG_Flags',
                    'FIN_Flag_Cnt','SYN_Flag_Cnt','RST_Flag_Cnt','PSH_Flag_Cnt','ACK_Flag_Cnt',
                    'URG_Flag_Cnt','CWE_Flag_Count','ECE_Flag_Cnt','DownUp_Ratio','Fwd_Bytsb_Avg',
                    'Fwd_Pktsb_Avg','Fwd_Blk_Rate_Avg','Bwd_Bytsb_Avg','Bwd_Pktsb_Avg','Bwd_Blk_Rate_Avg']

    
    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t

    labels = df['label'].copy()
    labels[labels != 'normal'] = 1 # anomalous
    labels[labels == 'normal'] = 0 # normal
    df['label'] = labels

    normal = df[df['label'] == 0] 
    abnormal = df[df['label'] == 1]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)]
    abnormal_2 = abnormal[int(len(abnormal)*.5):]

    train_size = int(len(normal)*.6)

    train_set = normal[:train_size]
#    val_normal = normal[train_size: train_size+val_size]
    test_normal = normal[train_size:]

    val_size = int(len(abnormal_1))
    test_size = int(len(abnormal_2))
    val_abnormal = abnormal_1
    test_abnormal = abnormal_2

    val_set = val_abnormal
    test_set = pd.concat((test_normal, test_abnormal))
    
    x_train, y_train = _to_xy(train_set, target='label')
    x_val, y_val = _to_xy(val_set, target='label')
    x_test, y_test = _to_xy(test_set, target='label')

    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 0])} normal records and {len(x_train[y_train == 1])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 0])} normal records and {len(x_val[y_val == 1])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 0])} normal records and {len(x_test[y_test == 1])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp

#    x_train.apply(pd.to_numeric)
#    x_test.apply(pd.to_numeric)    
#    x_val.apply(pd.to_numeric)

    x_train = x_train.to_numpy().astype(np.float32)
    x_val = x_val.to_numpy().astype(np.float32)
    x_test = x_test.to_numpy().astype(np.float32)

    index = np.arange(0, len(columns)-len(discreteCol)-1)


    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['oneHot'] = oneHot
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    np.save('/home/notebook/attack_generation/saved_attacks_generated/cicids/ARN_x_train.npy', dataset['x_train'])
    np.save('/home/notebook/attack_generation/saved_attacks_generated/cicids/ARN_y_train.npy', dataset['y_train'])
    np.save('/home/notebook/attack_generation/saved_attacks_generated/cicids/ARN_x_test.npy', dataset['x_test'])
    np.save('/home/notebook/attack_generation/saved_attacks_generated/cicids/ARN_y_test.npy', dataset['y_test'])
    
    return dataset

def get_ADFA_old(PATH, seed, scale = True, show = False):
    columns = ['packets', 'bytes', 'Duration', 'label']
    df = pd.read_csv(PATH)
    discreteCol = ['packets']#'protocol_type', 'service', 'flag', 'land', 'logged_in', 'is_hot_login', 'is_guest_login']

    names = []
    oneHot = dict()
    for name in discreteCol:
        n, t = _encode_text_dummy(df, name)
        names.extend(n)
        oneHot[name] = t

    labels = df['label'].copy()
    labels[labels != 'normal'] = 0 # anomalous
    labels[labels == 'normal'] = 1 # normal

    df['label'] = labels
    normal = df[df['label'] == 1] 
    abnormal = df[df['label'] == 0]
    
    normal = shuffle(normal, random_state = seed)
    abnormal = shuffle(abnormal, random_state = seed)

    abnormal_1 = abnormal[:int(len(abnormal)*.5)+1]
    abnormal_2 = abnormal[int(len(abnormal)*.5)+1:]

    train_size = int(len(normal)*.5)
    val_size = int(len(normal)*.05)+1

    train_set = normal[:train_size]
    val_normal = normal[train_size: train_size+val_size]
    test_normal = normal[train_size+val_size: ]

    val_size = int(len(abnormal_1)*.05)+1
    test_size = int(len(abnormal_1)*.15)+1
    val_abnormal = abnormal_1[:val_size]
    test_abnormal = abnormal_1[val_size:val_size+test_size]

    val_set = pd.concat((val_normal, val_abnormal))
    test_set = pd.concat((test_normal, test_abnormal))
    
    x_train, y_train = _to_xy(train_set, target='label')
    x_val, y_val = _to_xy(val_set, target='label')
    x_test, y_test = _to_xy(test_set, target='label')

    if show:
        print('{} normal records, {} anormal records'.format(len(normal), len(abnormal)))
        print(f'We use {len(abnormal_1)} anomalous records')
        print('-' * 89)
        print(f'There are {len(x_train)} records in training set')
        print(f'Training set is composed by {len(x_train[y_train == 1])} normal records and {len(x_train[y_train == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_val)} records in validation set')
        print(f'Validation set is composed by {len(x_val[y_val == 1])} normal records and {len(x_val[y_val == 0])} abnormal records')
        print('-' * 89)
        print(f'There are {len(x_test)} records in test set')
        print(f'Test set is composed by {len(x_test[y_test == 1])} normal records and {len(x_test[y_test == 0])} abnormal records')

    selected_columns = dict()
    
    for name in discreteCol:
        cols = [col for col in names if name in col]
        tmp = []
        
        for c in cols:
            tmp.append(x_train.columns.get_loc(c))

        selected_columns[name] = tmp
    
    x_train = x_train.to_numpy()
    x_val = x_val.to_numpy()
    x_test = x_test.to_numpy()
    
    index = np.arange(0, len(columns)-len(discreteCol)-1)

    if scale:
        scaler = MinMaxScaler()
        scaler.fit(x_train[:, index])
        x_train[:, index] = scaler.transform(x_train[:, index])
        x_val[:, index] = scaler.transform(x_val[:, index])
        x_test[:, index] = scaler.transform(x_test[:, index])
        
        
    dataset = {}
    dataset['x_train'] = x_train.astype(np.float32)
    dataset['y_train'] = y_train.astype(np.float32)
    
    dataset['x_val'] = x_val.astype(np.float32)
    dataset['y_val'] = y_val.astype(np.float32)
    
    dataset['x_test'] = x_test.astype(np.float32)
    dataset['y_test'] = y_test.astype(np.float32)
    
    dataset['selectedColumns'] = selected_columns
    dataset['discreteCol'] = discreteCol
    dataset['oneHot'] = oneHot
    dataset['index'] = index
    dataset['scaler'] = scaler
    
    return dataset
