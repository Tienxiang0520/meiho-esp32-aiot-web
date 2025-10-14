from flask import Flask, render_template, request
import paho.mqtt.publish as publish
import requests, os, socket, json

app = Flask(__name__)

# 載入設定檔
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

ESP_IP = "172.25.12.110"     # ⚠️ 改成你的 ESP32 IP
ESP_PORT = 8266
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
        response = requests.post(OLLAMA_URL, json=payload)
        data = response.json()
        msg = data.get("message", {}).get("content", data.get("response", "")).strip()
        print(f"🦙 AI 回覆：{msg}")
        return msg
    except Exception as e:
        print("❌ Ollama 連線失敗：", e)
        return ""

# ======== 傳送指令到 ESP32 ========
def send_to_esp32(command):
    try:
        publish.single(
            topic="/esp32/led",
            payload=command,
            hostname="broker.hivemq.com"
        )
        return f"已發送 {command}"
    except Exception as e:
        return f"MQTT 發送失敗：{e}"


# ======== Flask 頁面路由 ========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    user_input = request.form['command']
    ai_reply = ask_ollama(user_input)

    if any(k in ai_reply for k in ["開燈", "打開", "亮"]):
        result = send_to_esp32("LED_ON")
    elif any(k in ai_reply for k in ["關燈", "關閉", "熄滅"]):
        result = send_to_esp32("LED_OFF")
    else:
        result = "AI 無法判斷"

    return render_template('index.html', result=f"🦙 AI：{ai_reply} ｜ 💡 ESP32：{result}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
