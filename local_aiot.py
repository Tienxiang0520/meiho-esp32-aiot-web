from flask import Flask, jsonify
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt # <-- 新增
import requests, json, time, threading # <-- 新增 threading

app = Flask(__name__)

# ======== 載入設定檔 ========
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# (Render/Ollama 設定變數保持不變)
RENDER_URL = "https://meiho-esp32-aiot-web.onrender.com/latest_command"
MQTT_SERVER = "broker.hivemq.com" # 從 config.json 或直接設定
# 通知主題（必須與 web_control.py 中的設定相同）
NOTIFY_TOPIC = "meiho-aiot-notify/new_command_available"
# ESP32 控制主題
CONTROL_TOPIC = "/esp32/led"

OLLAMA_URL = config["ollama"]["url"]
MODEL = config["ollama"]["model"]
OPTIONS = config["ollama"]["options"]
SYSTEM_PROMPT = config["system_prompt"]



# ======== 向 Ollama 發問 ========
def ask_ollama(prompt):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": OPTIONS
    }

    try:
        res = requests.post(OLLAMA_URL, json=payload)
        data = res.json()
        msg = data.get("message", {}).get("content", "").strip()
        print(f"🧠 AI 回覆：{msg}")
        return msg
    except Exception as e:
        print("❌ Ollama 連線錯誤：", e)
        return ""

# ======== 發送 MQTT 指令（微調 send_mqtt 函式）========
def send_mqtt(cmd):
    try:
        # 將主題替換為您的實際主題
        publish.single(CONTROL_TOPIC, cmd, hostname=MQTT_SERVER)
        print(f"✅ 已發送 MQTT 指令：{cmd}")             
        # 💡 [建議新增] 提醒：狀態回報現在應由 ESP32 完成
        print("💡 上位機已完成任務，請確保 ESP32 成功執行後發送狀態到 MQTT。")
    except Exception as e:
        print("❌ MQTT 發送失敗：", e)


# ======== 訊息處理函式：收到通知即抓取指令 ========
def fetch_and_process_command():
    # 💡 這裡將原本 poll_render() 的核心邏輯搬過來
    try:
        res = requests.get(RENDER_URL, timeout=5)
        data = res.json()
        user_input = data.get("command")

        # 這裡不需要 global last_cmd，因為 Web 伺服器會清空，我們只需要抓到非 None 的指令
        if user_input:
            print(f"🆕 收到使用者輸入：{user_input}")
            ai_reply = ask_ollama(user_input)
            
            # 💡 由於您系統提示已很嚴格，這裡可以簡化判斷
            if ai_reply.startswith("開燈"): 
                send_mqtt("LED_ON")
            elif ai_reply.startswith("關燈"):
                send_mqtt("LED_OFF")
            else:
                print("🤖 AI 無法判斷")
    except Exception as e:
        print("⚠️ 無法從 Render 取得資料或處理指令：", e)

# ======== MQTT 客戶端回呼函式 ========
def on_connect(client, userdata, flags, rc):
    print("✅ MQTT 客戶端連線成功")
    # 訂閱通知主題
    client.subscribe(NOTIFY_TOPIC)
    print(f"📡 已訂閱通知主題：{NOTIFY_TOPIC}")

def on_message(client, userdata, msg):
    # 收到任何訊息，表示 Web UI 有新指令，立即觸發指令抓取與處理
    print("🔔 收到新指令通知！")
    threading.Thread(target=fetch_and_process_command).start()

# ======== 啟動 MQTT 監聽程序 ========
def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, 1883, 60) # MQTT 預設 port 1883
    client.loop_forever() # 保持客戶端運行並監聽訊息

@app.route('/')
def index():
    return jsonify({"status": "Local AIoT Running (MQTT Event Driven)"})

if __name__ == '__main__':
    print("🚀 本地 AI + MQTT 控制器已啟動 ...")
    
    # 1. 啟動一個獨立執行緒來跑 Flask Server（如果需要）
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5001}).start()
    
    # 2. 啟動 MQTT 客戶端（會佔用主執行緒來監聽）
    start_mqtt_client()
