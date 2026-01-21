import warnings
warnings.simplefilter(action='ignore', category=Warning)
import numpy as np
import pandas as pd
from scipy.io import arff
import math

epi_var = b'EPILEPSY'
walk_var = b'WALKING'
run_var = b'RUNNING'
saw_var = b'SAWING'

#Open X-Dimension in one Dataframe
EDTR1 = arff.loadarff('/home/admin/seizure_device/Epilepsy_Dataset/EpilepsyDimension1_TRAIN.arff')
EDTE1 = arff.loadarff('/home/admin/seizure_device/Epilepsy_Dataset/EpilepsyDimension1_TEST.arff')
dfED1 = pd.DataFrame(EDTR1[0])
dfET1 = pd.DataFrame(EDTE1[0])
Dim1 = dfED1._append(dfET1)
activity_col = Dim1['activity']

#open Y-Dimension in one Dataframe
EDTR2 = arff.loadarff('/home/admin/seizure_device/Epilepsy_Dataset/EpilepsyDimension2_TRAIN.arff')
EDTE2 = arff.loadarff('/home/admin/seizure_device/Epilepsy_Dataset/EpilepsyDimension2_TEST.arff')
dfED2 = pd.DataFrame(EDTR2[0])
dfET2 = pd.DataFrame(EDTE2[0])
Dim2 = dfED2._append(dfET2)

#Open Z-Dimension in one Dataframe
EDTR3 = arff.loadarff('/home/admin/seizure_device/Epilepsy_Dataset/EpilepsyDimension3_TRAIN.arff')
EDTE3 = arff.loadarff('/home/admin/seizure_device/Epilepsy_Dataset/EpilepsyDimension3_TEST.arff')
dfED3 = pd.DataFrame(EDTR3[0])
dfET3 = pd.DataFrame(EDTE3[0])
Dim3 = dfED3._append(dfET3)

#create TimeSeries df
df_xyz = pd.DataFrame()
df_TimeSeries = pd.DataFrame()
i = 0
while i < (len(Dim1.columns) - 1):
    columnDim1 = Dim1.columns[i]
    columnDim1Data = Dim1.iloc[:, i].tolist()
    df_xyz[f'X_{columnDim1}'] = columnDim1Data
    columnDim2 = Dim2.columns[i]
    columnDim2Data = Dim2.iloc[:, i].tolist()
    df_xyz[f'Y_{columnDim2}'] = columnDim2Data
    columnDim3 = Dim3.columns[i]
    columnDim3Data = Dim3.iloc[:, i].tolist()
    df_xyz[f'Z_{columnDim3}'] = columnDim3Data
    df_TimeSeries[f'{i}'] = ((df_xyz[f'X_channel_0_{i}']**2) + (df_xyz[f'Y_channel_1_{i}']**2) +(df_xyz[f'Z_channel_2_{i}']**2))
    df_TimeSeries[f'{i}'] = np.sqrt(df_TimeSeries[f'{i}'])
    i = i+1
activity_col.reset_index(drop=True, inplace=True)
df_TimeSeries.reset_index(drop=True, inplace=True)
df_TimeSeries= pd.concat([df_TimeSeries, activity_col], axis=1)
df_TimeSeries['activity'] = np.where(df_TimeSeries['activity'] == b'EPILEPSY', 1, 0)

#transform to and save as csv
csv_data = df_TimeSeries.to_csv('/home/admin/seizure_device/TimeSeries_DataFrame.csv', index = False)
