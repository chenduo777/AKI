from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Conv1D, LSTM
from keras.utils.vis_utils import plot_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from imblearn.over_sampling import BorderlineSMOTE
import matplotlib.pyplot as plt
from collections import Counter
import time
import pandas as pd
import numpy as np

def oldData():
    df_volume = pd.read_csv('C:\Programming\Python program\AIOT_CNN_LSTM\output.csv')
    df_volume = df_volume.to_numpy()

    #subject_id、尿量、ans
    df_volume = np.array([df_volume[:,1], df_volume[:,3], df_volume[:,4]])

    # 找出筆數大於等於36的病人
    check = [] 
    for key, val in Counter(df_volume[0]).items():
        if val >= 36:  
            check.append(key)

    # 病人後接上尿量、ans
    dict = {}
    for i in range(len(df_volume[0])):
        if df_volume[0][i] in check:
            if df_volume[0][i] not in dict:
                dict[df_volume[0][i]] = [[df_volume[1][i], df_volume[2][i]]]
            else:
                dict[df_volume[0][i]].append([df_volume[1][i], df_volume[2][i]])

    def Filter1(x):
        li = []
        for i in x:
            li.append(int(i[0]))
        return li

    def Filter2(x):
        li = []
        for i in x:
            li.append(i[1])
        for j in li:
            if j == 1:
                return 1
            else:
                return 0

    data = []
    ans = []
    sequence_length = 36
    for key, val in dict.items():
        for index in range(len(val) - sequence_length):
            data.append(Filter1(val[index : index+sequence_length-6])) #1~30
            ans.append(Filter2(val[index+31 : index+sequence_length]))

    X_train, x_test, Y_train, y_test = train_test_split(data, ans, test_size=0.8)

    X_train = np.array(X_train)
    Y_train = np.array(Y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)

    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1],1))
    Y_train = Y_train.reshape((Y_train.shape[0], 1))
    x_test = x_test.reshape((x_test.shape[0], x_test.shape[1],1))
    y_test = y_test.reshape((y_test.shape[0], 1))


    filters = 32
    kernel_size = 7
    epochs = 30

    # 建構模型
    model = Sequential()

    # Convolution
    model.add(Conv1D(
        filters = filters, #資料特徵的組合數
        kernel_size = kernel_size, #擷取資料特徵範圍
        input_shape = (X_train.shape[1], 1), 
        activation = 'relu', 
        strides = 1, #擷取資料特徵所移動的步數
        padding = 'valid'))

    # LSTM
    # 有 輸入、輸出、忘記，這三個控制
    # 如果輸入內容對於主要內容很重要的話，就會寫入主要部分
    # 如果主要內容被輸入內容改變，忘記控制會按比例忘掉先前的主要內容
    # 輸出控制會判斷要輸出主要內容還是輸入的內容
    model.add(LSTM(20))

    # 利用一個輸出的sigmoid輸出
    model.add(Dense(1, activation='sigmoid')) #輸出0~1之間


    # 編譯模型
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # 列印模型架構
    print(model.summary())

    plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)

    # SMOTE之改良 => 解決資料不平衡
    X_train = X_train.reshape(1588, 30)
    X_res, y_res = BorderlineSMOTE(random_state=42, kind="borderline-2").fit_resample(X_train, Y_train)
    X_res = X_res.reshape((X_res.shape[0], X_res.shape[1], 1))

    # 把訓練資料與模型擬合
    history = model.fit(X_res, y_res, batch_size = 1, epochs = epochs)

    def int2Float_1(x):
        li = []
        for i in x:
            li.append(np.float32(i[0]))
        return li

    def int2Float_2(x):
        li = []
        for i in x:
            if round(np.float32(i[0]), 1) >= 0.5:
                li.append(1.0)
            else:
                li.append(0.0)
        return li

    #下方程式使用在model.fit(X_train,y_train)之後
    y_pred = model.predict(x_test)
    print("Report:\n", classification_report(int2Float_1(y_test), int2Float_2(y_pred)))
    print("AUC:", round(roc_auc_score(y_test, y_pred), 5))
    print()

    model.save('AIOT_CNN_LSTM_model.h5')

    loss, accuracy = model.evaluate(x_test, y_test.reshape((y_test.shape[0], )))

    plt.plot(history.history['accuracy'])
    plt.plot(history.history['loss'])
    plt.title('Model')
    plt.ylabel('Accuracy & Loss')
    plt.xlabel('Epoch')
    plt.legend(['Accuracy', 'Loss'], loc='upper left')
    plt.show()

    print('測試資料的 loss:', round(loss, 2))
    print('測試集準確率:', accuracy, 2)

def main():
    s = time.time()
    oldData()
    e = time.time()
    print(round(e-s, 2), '秒')

if __name__ == '__main__':
    main()