from flask import Flask, render_template, request, jsonify
import os, threading, time
import paho.mqtt.publish as publish # <-- 新增


app = Flask(__name__)

# MQTT 設定
# 💡 注意：由於 Render 環境中無法直接讀取本地 config.json，這裡需要直接寫死或使用 Render 的環境變數
# 這裡先使用您 local_aiot.py 中的 HiveMQ 公開 Broker
MQTT_SERVER = "broker.hivemq.com" 
# 設置一個專門用來通知上位機的通知主題 (請確保此主題不易被猜測，增加安全性)
NOTIFY_TOPIC = "meiho-aiot-notify/new_command_available"
# 最新 AI 指令與狀態
latest_command = {"command": None, "status": "idle"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    user_input = request.form['command']
    latest_command["command"] = user_input
    latest_command["status"] = "pending"  # 等上位機處理
    
    # 📢 優化：透過 MQTT 發送通知
    try:
        publish.single(NOTIFY_TOPIC, "NOTIFY", hostname=MQTT_SERVER)
        print(f"✅ 已透過 MQTT 發送新指令通知到主題：{NOTIFY_TOPIC}")
    except Exception as e:
        print(f"❌ MQTT 通知發送失敗: {e}")

    # result=f"..." 這一行應該在 index.html 模板中處理，但因為您目前的 control 路由回傳 render_template，所以保持現有寫法
    return render_template('index.html', result=f"📩 指令已送出：{user_input}")

@app.route('/latest_command')
def get_command():
    return jsonify(latest_command)

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    latest_command["status"] = data.get("status", "unknown")
    print("🔄 收到上位機回報：", latest_command["status"])

    # ✅ 延遲清空（給前端輪詢時間）
    def clear_status():
        time.sleep(5)
        latest_command["command"] = None
        latest_command["status"] = "idle"
        print("🧹 狀態已清空，準備下一指令")

    threading.Thread(target=clear_status).start()
    return {"result": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
