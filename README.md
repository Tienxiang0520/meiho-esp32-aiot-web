# 🌐 AIoT 智慧控制系統 (ESP32 + Flask + Render + Ollama)

這是一個結合 ESP32、Python Flask 與雲端平台的智慧控制專題。
可透過網頁輸入「開燈」、「關燈」等指令，控制實體 ESP32 LED。

## 🔧 架構
使用者 → Flask 雲端伺服器 → Ollama AI 模型 → Flask 判斷 → MQTT → ESP32 → LED 控制

## 部署環境
• 雲端伺服器：Render (Python 3.11)
• 本地 AI 模型：Ollama (phi3:mini)
• 通訊協定：MQTT（HiveMQ 公開 Broker）
• 開發語言：Python (Flask)、C++ (Arduino)
• 控制硬體：ESP32-S 模組，GPIO4 控制 LED



## 快速上傳

git add .
git commit -m "update"
git push

