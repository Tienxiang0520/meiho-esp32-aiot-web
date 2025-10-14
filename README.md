# 🌐 AIoT 智慧燈控制系統（ESP32 × Ollama × MQTT × Flask）

這是一個基於 **ESP32**、**Ollama 本地 AI 模型** 與 **MQTT 通訊協定** 的智慧控制專題。  
使用者可透過網頁介面輸入自然語言指令（例如「開燈」「關燈」），  
系統會由本地 AI 判斷語意，經由 MQTT 控制 ESP32 實體 LED 的開關狀態。

---

## 🧠 系統架構圖

```text
使用者（Render 雲端頁面）
        │
        ▼
Flask（Render） → 暫存指令
        │
        ▼
Flask + Ollama（本地上位機）
   ├── AI 判斷「開燈」或「關燈」
   ├── 發送 MQTT 訊息（HiveMQ Broker）
   └── 回報執行狀態至 Render
        │
        ▼
ESP32（訂閱 /esp32/led）
   ├── 接收 LED_ON / LED_OFF
   └── 控制實體 LED 開關


## 部署環境
1. 雲端伺服器：Render (Python 3.11)
2. 本地 AI 模型：Ollama (phi3:mini)
3. 通訊協定：MQTT（HiveMQ 公開 Broker）
4. 開發語言：Python (Flask)、C++ (Arduino)
5. 控制硬體：ESP32-S 模組，GPIO4 控制 LED



## 快速上傳

. git add .
. git commit -m "update"
. git push

