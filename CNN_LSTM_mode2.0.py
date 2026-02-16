from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from keras.utils.vis_utils import plot_model
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.layers.convolutional import Conv1D
from keras.callbacks import ModelCheckpoint
from collections import Counter
import matplotlib.pyplot as plt
import time
import pandas as pd
import numpy as np

def oldData():
    df_volume = pd.read_csv('../data/output.csv')
    df_volume = df_volume.to_numpy()

    #subject_id、尿量、ans
    df_volume = np.array([df_volume[:,0], df_volume[:,2], df_volume[:,3]])
    # 找出筆數大於等於36的病人
    check = []
    for key, val in Counter(df_volume[0]).items():
        if val >= 36:
            check.append(key)

    # 病人後接上尿量、ans
    Dictionary = {}
    for i in range(len(df_volume[0])):
        if df_volume[0][i] in check:
            if df_volume[0][i] not in Dictionary:
                Dictionary[df_volume[0][i]] = [[df_volume[1][i], df_volume[2][i]]]
            else:
                Dictionary[df_volume[0][i]].append([df_volume[1][i], df_volume[2][i]])

    def Filter1(x):
        li = []
        for i in x:
            li.append(int(i[0]))
        return li

    #六小時內會有發生AKI output=1
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
    for key, val in Dictionary.items():
        for index in range(len(val) - sequence_length):
            data.append(Filter1(val[index: index+sequence_length-6])) #1~30
            ans.append(Filter2(val[index+31: index+sequence_length]))

    X_train, x_test, Y_train, y_test = train_test_split(data, ans, test_size=0.2)

    X_train = np.array(X_train)
    Y_train = np.array(Y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)

    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    Y_train = Y_train.reshape((Y_train.shape[0], 1))
    x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], 1))
    y_test = y_test.reshape((y_test.shape[0], 1))

    print("-----------------------------------------")
    print(f"訓練集X shape:{X_train.shape}")
    print(f"訓練集Y shape:{Y_train.shape}")
    print(f"測試集X shape:{x_test.shape}")
    print(f"測試集Y shape:{y_test.shape}")
    print("-----------------------------------------")

    filters = 32
    kernel_size = 16
    epochs = 5

    batch_size = 64

    model = Sequential()
    model.add(Conv1D(filters=filters,kernel_size=kernel_size, activation='relu', strides=1, padding="same",
                     input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(32,activation='relu'))
    model.add(Dropout(0.2))
    model.add(LSTM(32, activation='relu'))
    model.add(Dense(1,activation='sigmoid'))
    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

    print(model.summary())

    plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)


    #存取最好的一次，記得修改檔案路徑
    filepath = "../weight/CNN_LSTM_modelV2.0.h5"
    checkpoint = ModelCheckpoint(filepath=filepath, monitor='accuracy', verbose=1, save_best_only=True, mode='max')

    #把訓練資料與模型擬合
    #如果要跳過SMOTE就改成X_train ,Y_train
    history = model.fit(X_train, Y_train, batch_size=batch_size, epochs=epochs,
                        callbacks=[checkpoint], verbose=0)

    def int2Float_1(x):
        li = []
        for i in x:
            li.append(np.float32(i[0]))
        return li

    def int2Float_2(x):
        li = []
        for i in x:
            if np.round(np.float32(i[0]), 1) >= 0.5:
                li.append(1.0)
            else:
                li.append(0.0)
        return li

    #下方程式使用在model.fit(X_train,y_train)之後
    y_pred = model.predict(x_test)
    print("Report:\n", classification_report(int2Float_1(y_test), int2Float_2(y_pred)))
    print("AUC:", round(roc_auc_score(y_test, y_pred), 5))


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