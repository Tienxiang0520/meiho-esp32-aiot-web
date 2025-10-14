from flask import Flask, jsonify
import paho.mqtt.publish as publish
import requests, json, time

app = Flask(__name__)

# ======== 載入設定檔 ========
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 讀取設定內容
RENDER_URL = "https://meiho-esp32-aiot-web.onrender.com/latest_command"
MQTT_SERVER = "broker.hivemq.com"
OLLAMA_URL = config["ollama"]["url"]
MODEL = config["ollama"]["model"]
OPTIONS = config["ollama"]["options"]
SYSTEM_PROMPT = config["system_prompt"]

last_cmd = None

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

# ======== 發送 MQTT 指令 ========
def send_mqtt(cmd):
    try:
        publish.single("/esp32/led", cmd, hostname=MQTT_SERVER)
        print(f"✅ 已發送 MQTT 指令：{cmd}")
    except Exception as e:
        print("❌ MQTT 發送失敗：", e)

# ======== 從 Render 抓指令並處理 ========
def poll_render():
    global last_cmd
    try:
        res = requests.get(RENDER_URL, timeout=5)
        data = res.json()
        user_input = data.get("command")

        if user_input and user_input != last_cmd:
            print(f"🆕 收到使用者輸入：{user_input}")
            ai_reply = ask_ollama(user_input)
            if any(k in ai_reply for k in ["開燈", "打開", "亮"]):
                send_mqtt("LED_ON")
            elif any(k in ai_reply for k in ["關燈", "關閉", "熄滅"]):
                send_mqtt("LED_OFF")
            else:
                print("🤖 AI 無法判斷")

            last_cmd = user_input
    except Exception as e:
        print("⚠️ 無法從 Render 取得資料：", e)

@app.route('/')
def index():
    return jsonify({"status": "Local AIoT Running"})

if __name__ == '__main__':
    print("🚀 本地 AI + MQTT 控制器已啟動 ...")
    while True:
        poll_render()
        time.sleep(3)
