import pandas as pd
import numpy as np

df = pd.read_csv("output_1.csv")

#移除異常資料
df = df[1:]

#轉成numpy格式
df = df.to_numpy()

#創造空矩陣(結果)
#ans = np.zeros((1,4)).astype(np.object_)

def solution(j):
    global ans
    count = 0

    #創造空矩陣(新增)
    new_data=np.zeros((1,4)).astype(np.object_)
    if (j < 11):
        new_data[0,0] = df[num + j][0]
        new_data[0,1] = df[num + j][1]
        new_data[0,2] = df[num + j][2]
        new_data[0,3] = 0
        
    else:
        new_data[0,0] = df[num + j][0]
        new_data[0,1] = df[num + j][1]
        new_data[0,2] = df[num + j][2]

        #體重75.1，連續12小時<450.6表示有AKI(IBM計算理想體重)
        for k in range(12):
            count += df[num + j - k][2]
        if (count < 450.6):
            new_data[0,3] = 1
        else:
            new_data[0,3] = 0

    #ans=np.append(ans,new_data,axis=0)
    ans=pd.DataFrame({"subject_id":new_data[:,0],"charttime":new_data[:,1],"value":new_data[:,2],"ans":new_data[:,3]})
    ans.to_csv("output_2.csv", mode = 'a', header = False, index = False)

num = 0
#subject_id找出不同的病人
for i in range(np.shape(df)[0]):

    #最後一位
    if (i == np.shape(df)[0]-1):
        for j in range(i-num+1):
            solution(j)

    #不同病人
    elif (df[i][0] != df[i+1][0]):

        #第一個病人
        if (num == 0):
            for j in range(i-num+1):
                solution(j)
            num = i + 1
        else:
            for j in range(i-num+1):
                solution(j)
            num = i + 1
        print("i總",np.shape(df)[0],"跑到",i)

#過濾空矩陣第一筆
"""ans=ans[1:]

df=pd.DataFrame({"subject_id":ans[:,0],"charttime":ans[:,1],"value":ans[:,2],"ans":ans[:,3]})
df.to_csv("output.csv")"""
