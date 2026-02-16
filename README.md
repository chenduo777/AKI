# 基於 CNN LSTM 的 AI 預測系統於急性腎衰竭 (AKI) 之預防
**AI Prediction System for Acute Kidney Injury Prevention Based on CNN LSTM**

## 📖 專案簡介 (Project Overview)

急性腎損傷 (AKI) 是一種常見的臨床問題，若未能及早識別，可能導致嚴重併發症甚至危及生命。本專案開發了一套結合 **AIOT (人工智慧物聯網)** 的預測系統，利用 **CNN-LSTM** 深度學習模型，透過分析患者前 30 小時的尿量數據，預測未來 6 小時內發生 AKI 的風險。

系統整合了嵌入式硬體 (Raspberry Pi)、重量感測器與雲端資料庫，實現 24 小時不間斷的自動監測。一旦預測到風險，系統會透過 Line 即時通知醫護人員，並提供可視化的網頁儀表板供隨時監控，旨在減輕醫療人力負擔並提供早期干預的機會。

---

## ✨ 主要功能 (Key Features)

* **自動化尿量監測**：利用電子秤與 HX711 重量感測器，每小時自動記錄尿袋重量並轉換為數位訊號。
* **AI 風險預測**：使用 CNN-LSTM 模型，依據前 30 小時的尿量序列，預測未來 6 小時是否符合 AKIN stage 2 標準。
* **即時通報系統**：當偵測到 AKI 風險時，系統自動發送 Line Notify 通知駐院醫師與護理師。
* **AIOT 視覺化儀表板**：透過 Node.js (Vite + Vue) 架設網頁，結合 Firebase Realtime Database，即時顯示患者尿量變化圖表與風險指數。

---

## 🛠️ 系統架構 (System Architecture)

### 硬體設備 (Hardware)

* **核心控制器**：Raspberry Pi 4 (處理 AI 運算、資料傳輸)。
* **感測模組**：HX711 高精度 24-bit A/D 轉換模組。
* **測量設備**：電子拉力秤結合醫療用尿袋。

### 軟體與技術棧 (Software & Tools)

* **核心語言**：Python 3.7.16
* **深度學習框架**：TensorFlow 2.11.0, CUDA 10.1 (GPU: Nvidia GTX 1650ti)
* **資料處理**：Pandas, NumPy
* **雲端資料庫**：Google Firebase (Realtime Database)
* **網頁前端**：Node.js, Vue.js, Vite
* **版本控制**：Git

---

## 📂 專案結構 (Project Structure)

```
project_root/
├── AKI-Monitor/          # 網頁前端專案 (Vite + Vue)
├── data/                 # 訓練與測試資料集
├── model/                # 訓練好的模型檔案 (.h5)
├── respberrypi/          # Raspberry Pi 端的預測程式 (v1.0 - v2.4)
├── weight/               # 模型權重檔案
├── CNN_LSTM_mode2.0.py   # CNN-LSTM 模型訓練程式
├── akipredict運作.py     # 主程式：整合資料讀取與預測邏輯
├── LSTM_test.py          # 模型測試腳本
└── README.md             # 專案說明文件
```

---

## 🧠 模型與資料集 (Model & Dataset)

### 資料集

* **來源**：MIMIC-III Dataset (Medical Information Mart for Intensive Care)
* **資料規模**：篩選後使用 2,012 位 AKI 患者，共 547,694 筆尿量資料。
* **前處理**：
    * 提取 `Urine Out Foley` 數據。
    * 依據 AKIN criteria 標註資料 (Stage 2)。
    * 處理缺失值與異常值，並移除透析患者與住院少於 24 小時之資料。

### 模型架構 (CNN-LSTM)

結合了卷積神經網絡 (CNN) 的特徵提取能力與長短期記憶網絡 (LSTM) 的時序記憶能力。

1. **Input Layer**: 接收 (Batch, 30, 1) 的時序資料。
2. **Conv1D + ReLU**: 提取尿量變化的局部特徵。
3. **MaxPooling**: 降維並保留重要特徵。
4. **LSTM Layers**: 捕捉長時間的依賴關係 (Long-term dependencies)。
5. **Dropout**: 防止過擬合 (Overfitting)。
6. **Dense Layer**: 輸出預測結果 (AKI 風險機率)。

---

## 📊 實作成果與模型表現 (Results)

本研究模型在測試集上的表現如下：

| 指標 (Metric) | 數值 (Value) | 說明 |
| --- | --- | --- |
| **Accuracy** | **0.979** | 模型整體預測準確率 |
| **Loss** | **0.0745** | 訓練損失率 (Binary Crossentropy) |
| **F1-Score** | **0.946** | 綜合考量 Precision 與 Recall 的指標 |
| **AUC** | **0.996** | ROC 曲線下面積，顯示極佳的分類能力 |

**實際應用場景驗證：**
系統在模擬測試中，能夠準確識別連續寡尿情況，並在符合 AKIN stage 2 標準時成功發出警報與 Line 通知。

---

## 🚀 使用說明 (Usage)

### 1. 硬體連接
* 將 HX711 連接至 Raspberry Pi 的 GPIO (DT 接 PIN8/TXD, SCK 接 PIN10/RXD)。
* 掛上尿袋並歸零電子秤。

### 2. 系統啟動 (Raspberry Pi 端)
```bash
# SSH 連線至 Raspberry Pi
ssh pi@<raspberry_pi_ip>

# 進入程式目錄
cd /path/to/project/respberrypi

# 執行預測程式 (例如 V2.4)
python respberrypi_predict_V2.4.py
```
* **輸入患者 ID**：程式啟動後需輸入 `Subject_id` 以開始監測。

### 3. 啟動監控儀表板 (Web Dashboard)
```bash
# 進入前端目錄
cd AKI-Monitor

# 安裝相依套件
npm install

# 啟動開發伺服器
npm run dev
```
* 開啟瀏覽器訪問顯示的 URL (例如 `http://localhost:5173`)。

### 4. 監控與通知
* 系統將自動每小時記錄數據至 Firebase。
* 醫護人員可透過 AIOT 網頁查看即時數據。
* 若預測風險指數過高，Line 將自動跳出警示訊息。

---

## 👥 專題製作團隊 (Team)

* **指導教授**：夏世昌 教授、王斯弘 教授
* **專題學生**：
    * 陳亮甫 (Chen, Liang-Fu)
    * 柯柏安 (Ko, Bo-An)
* **學校系所**：國立雲林科技大學 電子工程系
* **日期**：中華民國 113 年 4 月

---

> [!NOTE]
> 本專案使用之 MIMIC-III 資料集需完成 CITI 課程並簽署 DUA 協議方可使用。
