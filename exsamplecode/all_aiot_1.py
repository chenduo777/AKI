import pandas as pd
import numpy as np

data=pd.read_csv("D:\下載\MIMIC\OUTPUTEVENTS.csv\OUTPUTEVENTS.csv")

#移除itemid不等於40055 226559
itemid = (data['ITEMID'] == 40055)
itemid += (data['ITEMID'] == 226559)
data = data[itemid]

#移除需透析患者(subject_id = 10059、10126、44212)
data = data[(data["subject_id"] != 10059)]
data = data[(data["subject_id"] != 10126)]
data = data[(data["subject_id"] != 44212)]

#空值補零
data = data.fillna(0)

#時間排序(因為資料是亂的)
data["charttime"] = pd.to_datetime(data["charttime"])
data = data.sort_values(by="charttime")

#轉成list型態
date=pd.to_datetime(data["charttime"]).tolist()

#轉成numpy型態
subject_id=data["subject_id"].to_numpy()
charttime=data["charttime"].to_numpy()
value=data["value"].to_numpy()

#找出subject_id的聯集
subject_id_unique=np.unique(subject_id)

#創造空矩陣(結果)
ans=np.zeros((1,3)).astype(np.object_)

#資料處理
d={}
for i in range(len(subject_id_unique)):

    #找出相同subject_id的人
    unique_index=np.where(subject_id==subject_id_unique[i])[0]

    #資料小於24小時剔除
    if(len(unique_index)<24):
        continue
    
    #時間及尿量處理
    time_1=0
    time_2=0

    #ans存入第一筆
    if (date[unique_index[0]].minute == 0):
        ans=np.append(ans,np.array([[subject_id[unique_index[0]],charttime[unique_index[0]],value[unique_index[0]]]]).astype(np.object_),axis=0)
        ans=ans[1:]
        ans=pd.DataFrame({"subject_id":ans[:,0],"charttime":ans[:,1],"value":ans[:,2]})
        ans.to_csv("output_1.csv", mode = 'a', header = False, index = False)

    for j in range(1,len(unique_index)):
        print("j總",len(unique_index),"跑到",j)

        #兩筆時間差
        minute=(date[unique_index[j]]-date[unique_index[j-1]]).seconds/60

        #j-1的時間加多少到整點
        t_minute=60-date[unique_index[j-1]].minute

        #j的分鐘
        s_minute=date[unique_index[j]].minute

        #時間差小於60
        if(minute<60):

            #Timestamp精確度到奈秒計算，把非整點加到整點
            key=date[unique_index[j]].value+1000000000*t_minute*60

            #有無在d裡
            if(key in d):
                #有，原時間做加法
                d[key]+=value[unique_index[j]]
            else:
                #無，創建新時間跟尿量
                d[key]=value[unique_index[j]]
            continue
        
        #創造空矩陣(新增)
        new_data=np.zeros((1,3)).astype(np.object_)

        #j - 1秒數
        or_time=date[unique_index[j-1]].value

        #時間差9~1小時
        time_1=0
        time_2=minute
        while(540 >= time_2-time_1 >= 60):

            #第一個時間跟t_minute不是整點
            if(time_1==0 and t_minute!=0):
                
                #加到time_1，給下個迴圈做大於等於60判斷
                time_1+=t_minute

                #加到整點
                or_time+=1000000000*t_minute*60

                #存入矩陣
                new_data[0,0]=subject_id_unique[i]
                new_data[0,1]=str(pd.Timestamp(or_time))
                new_data[0,2]=value[unique_index[j]]/minute*t_minute
            else:
                time_1+=60

                #加1小時
                or_time+=1000000000*60*60

                new_data[0,0]=subject_id_unique[i]
                new_data[0,1]=str(pd.Timestamp(or_time))
                new_data[0,2]=value[unique_index[j]]/minute*60

            # while迴圈算完時間小於60，剩的尿量加到下一筆尿量
            if(or_time in d):
                new_data[0,2]+=d[or_time]

            #ans存入new_data
            #ans=np.append(ans,new_data,axis=0)
            df=pd.DataFrame({"subject_id":new_data[:,0],"charttime":new_data[:,1],"value":new_data[:,2]})
            df.to_csv("output_1.csv", mode = 'a', header = False, index = False)

        #j的分鐘不是整數，尿量加到下一個小時
        key=date[unique_index[j]].value+1000000000*(60-s_minute)*60
        if(key in d):
            d[key]+=value[unique_index[j]]/minute*s_minute
        else:
            d[key]=value[unique_index[j]]/minute*s_minute

#過濾空矩陣第一筆
"""ans=ans[3:]

df=pd.DataFrame({"subject_id":ans[:,0],"charttime":ans[:,1],"value":ans[:,2]})
df.to_csv("output.csv")"""