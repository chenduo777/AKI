from keras.layers import Dropout
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from hx711 import HX711
from firebase import firebase
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import time
import datetime
import numpy as np
import requests

ORIGNE_VALUE = -315300
ML = -73


def aki_predict(new_data):  
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
    model.load_weights("AIOT_CNN_LSTM_model.h5")
    answer = model.predict(new_data)
    return answer


def linenotifymessage(msg, hours, id):
    url = 'https://notify-api.line.me/api/notify'
    token = '52WHYwv47g8n7mhoz32HotEM8fg3lCMcpcYrufHU7DV'
    headers = {
        "Authorization": "Bearer " + token,
    }

    data = {
        'message': msg 
    }
    image = open(f"{id}-{hours}.png","rb")
    imgfiles = { 'imageFile': image }

    r = requests.post(url, headers = headers, data=data, files = imgfiles)


#用舊有的資料測試
def data_filter(data, hours):
    #總共30個數
    filter_data = data[hours-30:hours]
    return filter_data


def get_urine_weight(value):
    GPIO.setmode(GPIO.BCM)
    hx = HX711(dout_pin=14, pd_sck_pin=15)
    hx.reset()
    reading = hx.get_raw_data_mean()
    urine_weight = value - reading
    if urine_weight > 0:
        urine_weight = 0
    return int(urine_weight / ML) , reading


def reset_urine_weight(value):
    return value == 0
    


def firebase_datapost(data):
    url = "https://aki-predict-56d08-default-rtdb.asia-southeast1.firebasedatabase.app/"
    fdb = firebase.FirebaseApplication(url, None) 
    fdb.put('/','data',data)


def main():
    inhospital_hours = 0
    uri_data = []
    risk_data = []
    time_list = []
    subject_id = input("Please input the Subject_ID:")
    last_value = ORIGNE_VALUE 


    while True:
        inhospital_hours += 1
        new_urine, last_value = get_urine_weight(last_value)
        uri_data.append(new_urine)
        subject_dict = {
            "subject_id":subject_id, 
            "total_hours":inhospital_hours,
            "urine":uri_data,
            "risk":risk_data,
        }
        #plot用
        time_list.append(inhospital_hours)

        now = datetime.datetime.now()
        print(f"subject_id:{subject_id}\ntime:{now}\nurine_weight:{new_urine}\n累計住院時數:{inhospital_hours}")
        print("---------------------")
        #AKI happen
        if len(subject_dict["urine"]) >= 30:
            filtered_data = data_filter(subject_dict["urine"],inhospital_hours)
            answer = aki_predict(filtered_data)
            answer = np.round(answer,2)
            json_answer = float(answer[0][0])
            risk_data.append(json_answer)
            print(json_answer)
            print(f"30小時尿量:{filtered_data}")
            if answer > 0.7:
                lines = plt.plot(time_list,subject_dict["urine"],)
                plt.title("urine history data")
                plt.xlabel("inhospital time")
                plt.ylabel("urine(ml)")
                plt.setp(lines,marker = "o")
                plt.grid(True)
                plt.savefig(f"{subject_id}-{inhospital_hours}.png")
                print(f"患者ID:{subject_id},HAVE AKI!,HAVE AKI!,HAVE AKI!,HAVE AKI!")
                print("---------------------")
                message = f'患者ID:{subject_id},將在六小時內發生AKI,請駐院醫生即時支援。'
                linenotifymessage(message, inhospital_hours, subject_id)
            else:
                print(f"NO AKI,患者ID:{subject_id},AKI監測正常。")
                print("---------------------")
        else:
            risk_data.append(0)
        firebase_datapost(subject_dict)
        time.sleep(1)


if __name__ == "__main__":
    main()


