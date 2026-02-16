import pandas as pd
import numpy as np

data = pd.read_csv("Urine.csv")

data['CHARTTIME'] = pd.to_datetime(data['CHARTTIME'])
# 創造空矩陣(結果)
ans = pd.DataFrame(columns=["SUBJECT_ID", "CHARTTIME", "VALUE"])

# 資料處理
d = {}
for subject_id_unique in data["SUBJECT_ID"].unique():

    # 找出相同subject_id的人
    unique_data = data[data["SUBJECT_ID"] == subject_id_unique]

    # 資料小於24小時剔除
    if len(unique_data) < 24:
        continue

    # ans存入第一筆
    first_row = unique_data.iloc[0]
    if first_row["CHARTTIME"].minute == 0:
        ans = ans.append(first_row)

    for j in range(1, len(unique_data)):
        print("j總", len(unique_data), "跑到", j)

        # 兩筆時間差
        minute = (unique_data.iloc[j]["CHARTTIME"] - unique_data.iloc[j-1]["CHARTTIME"]).seconds / 60

        # j-1的時間加多少到整點
        t_minute = 60 - unique_data.iloc[j-1]["CHARTTIME"].minute

        # j的分鐘
        s_minute = unique_data.iloc[j]["CHARTTIME"].minute

        # 時間差小於60
        if minute < 60:

            # Timestamp精確度到奈秒計算，把非整點加到整點
            key = unique_data.iloc[j]["CHARTTIME"].value + 1000000000 * t_minute * 60

            # 有無在d裡
            if key in d:
                # 有，原時間做加法
                d[key] += unique_data.iloc[j]["VALUE"]
            else:
                # 無，創建新時間跟尿量
                d[key] = unique_data.iloc[j]["VALUE"]
            continue

        # j - 1秒數
        or_time = unique_data.iloc[j-1]["CHARTTIME"].value

        # 時間差9~1小時
        time_1 = 0
        time_2 = minute
        while 540 >= time_2 - time_1 >= 60:

            # 第一個時間跟t_minute不是整點
            if time_1 == 0 and t_minute != 0:

                # 加到time_1，給下個迴圈做大於等於60判斷
                time_1 += t_minute

                # 加到整點
                or_time += 1000000000 * t_minute * 60

                # 存入DataFrame
                new_row = {
                    "SUBJECT_ID": subject_id_unique,
                    "CHARTTIME": pd.Timestamp(or_time),
                    "VALUE": unique_data.iloc[j]["VALUE"] / minute * t_minute
                }
                ans = ans.append(new_row, ignore_index=True)
            else:
                time_1 += 60

                # 加1小時
                or_time += 1000000000 * 60 * 60

                new_row = {
                    "SUBJECT_ID": subject_id_unique,
                    "CHARTTIME": pd.Timestamp(or_time),
                    "VALUE": unique_data.iloc[j]["VALUE"] / minute * 60
                }
                ans = ans.append(
                    new_row, ignore_index=True)

            # while迴圈算完時間小於60，剩的尿量加到下一筆尿量
            if or_time in d:
                ans.loc[ans["CHARTTIME"] == pd.Timestamp(or_time), "VALUE"] += d[or_time]

        # j的分鐘不是整數，尿量加到下一個小時
        key = unique_data.iloc[j]["CHARTTIME"].value + 1000000000 * (60 - s_minute) * 60
        if key in d:
            d[key] += unique_data.iloc[j]["VALUE"] / minute * s_minute
        else:
            d[key] = unique_data.iloc[j]["VALUE"] / minute * s_minute

# 输出结果
ans.to_csv("Urineoutput.csv", mode="a", header=True, index=True)
