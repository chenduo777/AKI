import pandas as pd
import numpy as np

#-----------------------------------------------------------------
#now code to all patients
#-----------------------------------------------------------------

df = pd.read_csv("output_2.csv")
df_2 = pd.read_csv("labevents.csv")

#轉成numpy格式
df = df.to_numpy()
subject_id = df_2["subject_id"].to_numpy()
df_2 = df_2.to_numpy()

#轉成list型態
date=pd.to_datetime(df[:,1]).tolist()

#創造空矩陣(結果)
ans = np.zeros((1,12)).astype(np.object_)

def serum_creatinine():
    global creatinine

    #找出相同subject_id的人
    unique_index=np.where(subject_id==df[num][0])[0]
    creatinine = []

    #抓出該病人的creatinine
    creatinine_count = 0
    for k in unique_index:
        creatinine.append(df_2[k][1])
        creatinine_count += 1
    if (creatinine_count == 0):
        creatinine = 0
    else:
        creatinine_sort = sorted(creatinine)

        #找index
        creatinine = np.array(creatinine).astype("<U3")
        creatinine_index = np.where(creatinine==str(creatinine_sort[0]))
        for index in range(creatinine_index[0][0]+1,len(creatinine)):

            # >= min * 2表示label有aki
            if (float(creatinine[index]) >= (float(creatinine_sort[0]) * 2)):
                creatinine = 1
                break
        if (creatinine != 1):
            creatinine = 0

def Logistic_deal_with():
    global ans
    
    #創造空矩陣(新增)
    feature=np.zeros((1,12)).astype(np.object_)

    #剔除小於30筆
    if ((i-num-28) > 0):
        for j in range(i-num-28):

            #開始時間點
            str_time = num + j

            #urine output and serum creatinine判斷病人是否發生aki
            aki_risk = 0
            for k in range(30,36):
                if (creatinine == 1 and  df[str_time+k][3] == 1):
                    aki_risk = 1
                    break
            feature[0,11] = aki_risk

            #slide window
            for a in range(12,1,-1):
                mean = []

                #mean
                for b in range(31-a):
                    count = 0

                    #slide window range
                    for c in range(a):
                        count += df[str_time + b + c][2]
                    count /= a
                    mean.append(count)
                mean = sorted(mean)
                feature[0,12-a] = mean[0]

            ans=pd.DataFrame({"Features1":feature[:,0],"Features2":feature[:,1],"Features3":feature[:,2],"Features4":feature[:,3],"Features5":feature[:,4],"Features6":feature[:,5],"Features7":feature[:,6],"Features8":feature[:,7],"Features9":feature[:,8],"Features10":feature[:,9],"Features11":feature[:,10],"aki":feature[:,11]})
            ans.to_csv("my_aiot.csv", mode = 'a', header = False, index = False)
            print("i總",np.shape(df)[0],"跑到",i)
            if (aki_risk == 1):
                break



num = 0

#subject_id找出不同的病人
for i in range(np.shape(df)[0]):

    #最後一位
    if (i == np.shape(df)[0]-1):
        serum_creatinine()
        Logistic_deal_with()

    #不同病人
    elif (df[i][0] != df[i+1][0]):

        #第一個病人
        if (num == 0):
            serum_creatinine()
            Logistic_deal_with()
            num = i + 1
        else:
            serum_creatinine()
            Logistic_deal_with()
            num = i + 1
    
    #兩筆時間差大於9小時
    elif(540 < (date[i+1]-date[i]).seconds/60):
            serum_creatinine()
            Logistic_deal_with()
            num = i + 1

#過濾空矩陣第一筆
"""ans=ans[1:]

save_csv=pd.DataFrame({"Features1":ans[:,0],"Features2":ans[:,1],"Features3":ans[:,2],"Features4":ans[:,3],"Features5":ans[:,4],"Features6":ans[:,5],"Features7":ans[:,6],"Features8":ans[:,7],"Features9":ans[:,8],"Features10":ans[:,9],"Features11":ans[:,10],"aki":ans[:,11]})
save_csv.to_csv("my_aiot.csv")"""
