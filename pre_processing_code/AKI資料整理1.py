import pandas as pd
import os

chunk_size = 1000  # 每個块的大小
min_hospital_hours = 24  # 最小住院時間（小時）
# 读取ADMISSIONS.csv文件以獲取住院時間信息
admissions_df = pd.read_csv("D:\下載\MIMIC\ADMISSIONS.csv")
df1 = pd.read_csv("D:\下載\MIMIC\DIAGNOSES_ICD.csv\DIAGNOSES_ICD.csv")

# 逐块讀取OUTPUTEVENTS.csv文件
for chunk in pd.read_csv("D:\下載\MIMIC\OUTPUTEVENTS.csv\OUTPUTEVENTS.csv", chunksize=chunk_size):
    # 在每個块中執行尿量資訊的提取操作
    urine_df = chunk[chunk['ITEMID'].isin([40055])]
    urine_df = urine_df[urine_df['VALUE'].notna()]
    urine_df = urine_df[['SUBJECT_ID', 'CHARTTIME', 'ITEMID', 'VALUE', 'VALUEUOM']]

    # 將CHARTTIME轉換為日期時間格式
    urine_df['CHARTTIME'] = pd.to_datetime(urine_df['CHARTTIME'])

    # 將尿量資訊與住院時間信息進行合併
    merged_df = pd.merge(urine_df, admissions_df[['SUBJECT_ID', 'ADMITTIME', 'DISCHTIME']], on='SUBJECT_ID', how='inner')

    # 計算住院時間（小時）
    merged_df['ADMITTIME'] = pd.to_datetime(merged_df['ADMITTIME'])
    merged_df['DISCHTIME'] = pd.to_datetime(merged_df['DISCHTIME'])
    merged_df['HOSPITAL_DURATION'] = (merged_df['DISCHTIME'] - merged_df['ADMITTIME']).dt.total_seconds() / 3600

    # 過濾住院時間小於24小時的病人
    filtered_df = merged_df[merged_df['HOSPITAL_DURATION'] >= min_hospital_hours]

    # 剔除指定的患者資料
    filtered_df = filtered_df[~filtered_df['SUBJECT_ID'].isin([10059, 10126, 44212])]

# 提取CSV文件中特定列的特定值
specific_values = df1[df1['ICD9_CODE'].str.startswith('584', na=False)]

merged_df = pd.merge(specific_values, filtered_df, on='SUBJECT_ID', how='inner')

merged_df[['SUBJECT_ID', 'CHARTTIME', 'ITEMID', 'VALUE', 'VALUEUOM']].to_csv("Urine.csv", mode='a', header=not os.path.exists("Urine.csv"), index=False)