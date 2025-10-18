from flask import Flask, jsonify
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import requests, json, time, threading

app = Flask(__name__)

# ======== 載入設定檔 ========
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 💡 Render URL 變數
RENDER_BASE_URL = "https://meiho-esp32-aiot-web.onrender.com" 
RENDER_GET_URL = f"{RENDER_BASE_URL}/latest_command"
RENDER_CLEAR_URL = f"{RENDER_BASE_URL}/clear_command" # <--- 新增清除 URL

MQTT_SERVER = "broker.hivemq.com"
NOTIFY_TOPIC = "meiho-aiot-notify/new_command_available"
CONTROL_TOPIC = "/esp32/led"

OLLAMA_URL = config["ollama"]["url"]
MODEL = config["ollama"]["model"]
OPTIONS = config["ollama"]["options"]
SYSTEM_PROMPT = config["system_prompt"]

# ... (ask_ollama 函式保持不變) ...

# ======== 發送 MQTT 指令 (新增清空指令) ========
def send_mqtt(cmd):
    try:
        publish.single(CONTROL_TOPIC, cmd, hostname=MQTT_SERVER)
        print(f"✅ 已發送 MQTT 指令：{cmd}")
        
        # 💡 [新增] 在指令發送後，通知 Render 伺服器清空指令
        requests.post(RENDER_CLEAR_URL)
        
    except Exception as e:
        print("❌ MQTT 發送失敗：", e)


# ======== 訊息處理函式：收到通知即抓取指令 ========
def fetch_and_process_command():
    try:
        # ⚠️ 這裡使用 GET URL
        res = requests.get(RENDER_GET_URL, timeout=5)
        data = res.json()
        user_input = data.get("command")

        # 只需要判斷是否有新指令
        if user_input:
            print(f"🆕 收到使用者輸入：{user_input}")
            ai_reply = ask_ollama(user_input)
            
            # 💡 簡化判斷
            if ai_reply.startswith("開燈"): 
                send_mqtt("LED_ON")
            elif ai_reply.startswith("關燈"):
                send_mqtt("LED_OFF")
            else:
                print("🤖 AI 無法判斷")

    except Exception as e:
        print("⚠️ 無法從 Render 取得資料或處理指令：", e)


# ======== MQTT 客戶端回呼函式 (保持不變) ========
def on_connect(client, userdata, flags, rc):
    print("✅ MQTT 客戶端連線成功")
    client.subscribe(NOTIFY_TOPIC)
    print(f"📡 已訂閱通知主題：{NOTIFY_TOPIC}")

def on_message(client, userdata, msg):
    print("🔔 收到新指令通知！")
    # 使用獨立執行緒來處理，避免阻塞 MQTT 迴圈
    threading.Thread(target=fetch_and_process_command).start()

# ======== 啟動 MQTT 監聽程序 (保持不變) ========
def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, 1883, 60)
    client.loop_forever() 

@app.route('/')
def index():
    return jsonify({"status": "Local AIoT Running (MQTT Event Driven)"})

if __name__ == '__main__':
    print("🚀 本地 AI + MQTT 控制器已啟動 ...")
    
    # 1. 啟動 Flask Server（允許 Render GET 指令）
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5001}).start()
    
    # 2. 啟動 MQTT 客戶端
    start_mqtt_client()