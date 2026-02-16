from keras.layers.regularization.dropout import Dropout
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
import time
import pandas as pd
import numpy as np
import requests

def predict(new_data):
  filters = 30
  kernel_size = 7
  new_data = np.array(new_data)
  new_data = new_data.reshape((1,new_data.shape[0],1))
  model = Sequential()
  model.add(Conv1D(filters = filters,kernel_size = kernel_size, activation='relu', strides=1,input_shape = (new_data.shape[1],1)))
  model.add(MaxPooling1D())
  model.add(Dropout(0.2))
  model.add(Conv1D(filters = filters,kernel_size = kernel_size, activation='relu', strides=1,input_shape = (new_data.shape[1],1)))
  model.add(MaxPooling1D())
  model.add(Dropout(0.2))
  model.add(LSTM(100,activation='relu'))
  model.add(Dense(1,activation='sigmoid'))
  model.load_weights("weight\AIOT_CNN_LSTM_model.h5")
  answer = model.predict(new_data)
  return answer


def lineNotifyMessage(token, msg):
  headers = {
      "Authorization": "Bearer " + token,
      "Content-Type" : "application/x-www-form-urlencoded"
  }

  payload = {'message': msg }
  r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
  return r.status_code


def loadcsv():
  df = pd.read_csv("data/test_subject_38.csv")
  df = df.to_numpy()
  df = np.array([df[:,0],df[:,2]])
  new_data = {}
  for i in range(len(df[0])):
    if df[0][i] not in new_data:
      new_data[df[0][i]] = [df[1][i]]
    else:
      new_data[df[0][i]].append(df[1][i])
  return new_data


# #假設新尿量匯入(還沒寫完)
# def newurine(input_data):
#   count = 0
#   if count < len(input_data):
#     urine = input_data["VALUE"][count]
#     count += 1
#   return urine

# #如果有新增的尿量，就從最新抓到前30小時的資料
# def newdata_filter(data):
#   filter_data = data[-30:]
#   print(filter_data)
#   return filter_data


#用舊有的資料測試
def data_filter(data,inhospital_hours):
  #總共30個數
  int_data = Filter1(data)
  filter_data = int_data[inhospital_hours-30:inhospital_hours] 
  return filter_data

def Filter1(x):
  li = []
  for i in x:
    li.append(int(i))
  return li

token = '52WHYwv47g8n7mhoz32HotEM8fg3lCMcpcYrufHU7DV'
hospitalized = True
#住院時間
inhospital_hours = 30
data = loadcsv()
#若有AKI的狀況發生
aki_data_list=[80, 100, 50, 80, 40, 40, 40, 35, 30, 4, 3, 4, 4, 4, 20, 30, 5, 30, 30, 20, 10, 9, 20, 3, 25, 28, 13, 13, 17, 4]


for subject_id in data:
  while hospitalized:
    if len(data[subject_id]) > 30:
      filtered_data = data_filter(data[subject_id],inhospital_hours)
      answer = predict(filtered_data)
      print(f"30小時尿量:{filtered_data}")
      print(answer)
      if answer > 0.5:
        print("HAVE AKI!")
        message = f'患者ID:{subject_id},將在六小時內發生AKI,請駐院醫生即時支援。'
        lineNotifyMessage(token, message)
      else :
        print(f"NO AKI,患者ID:{subject_id},AKI監測正常。")
        print(f"累計住院時數:{inhospital_hours}")
      time.sleep(10)
      inhospital_hours += 1


