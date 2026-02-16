import pandas as pd

# 读取数据集
df = pd.read_csv("Urineoutput.csv")
ans = pd.DataFrame(columns=["SUBJECT_ID", "CHARTTIME", "VALUE","HAVEAKI"])
grouped = df.groupby("SUBJECT_ID")

# 遍歷每個組
for subject_id, group_data in grouped:
    count = 0
    flag = 0
    # 遍歷每個組的每一行資料
    for i in range(len(group_data)):
        print("總行數", len(group_data), "目前行數", i)
        # 標準BMI體重=75.1
        if group_data.iloc[i]['VALUE'] <= 37.5:
            count += 1
            if count >= 12:
                flag = 1
        else:
            flag = 0
            count = 0

        # 將結果加入新的DataFrame
        new_row = {
            "SUBJECT_ID": subject_id,
            "CHARTTIME": group_data.iloc[i]["CHARTTIME"],
            "VALUE": group_data.iloc[i]["VALUE"],
            "HAVEAKI": int(flag)
        }
        ans = ans.append(new_row, ignore_index=True)

filtered_df = ans.groupby('SUBJECT_ID').filter(lambda x: (x['HAVEAKI'] == 1).any())
filtered_df.to_csv('output.csv', index=False)
