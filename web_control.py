from flask import Flask, render_template, request, jsonify
import os
import paho.mqtt.publish as publish 

app = Flask(__name__)

# MQTT 設定
MQTT_SERVER = "broker.hivemq.com" 
NOTIFY_TOPIC = "meiho-aiot-notify/new_command_available"

# 💡 [保留] 最新 AI 指令與狀態 (PC 仍需從這裡 GET 指令)
latest_command = {"command": None, "status": "idle"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    # 這是前端按鈕會發送的路由
    user_input = request.form['command']
    
    # 1. 儲存指令
    latest_command["command"] = user_input
    latest_command["status"] = "pending"

    # 2. 📢 透過 MQTT 發送通知給 PC（確保在回傳前執行）
    try:
        # 由於這個主題只需要通知事件發生，內容可以很輕量
        publish.single(NOTIFY_TOPIC, "NOTIFY", hostname=MQTT_SERVER)
        print(f"✅ 已透過 MQTT 發送新指令通知到主題：{NOTIFY_TOPIC}")
    except Exception as e:
        error_message = f"❌ MQTT 通知發送失敗: {e}"
        print(error_message)
        return jsonify({
            "status": "error",
            "message": error_message,
            "command": user_input
        }), 500

    # 3. 改為回傳 JSON 格式的回應，更穩定
    return jsonify({
        "status": "success",
        "message": f"📩 指令已送出：{user_input}",
        "command": user_input
    })

@app.route('/latest_command')
def get_command():
    # 💡 [PC 用] 讓 PC 可以 GET 取得指令
    return jsonify(latest_command)

@app.route('/command_status', methods=['POST'])
def update_command_status():
    """💡 [PC 用] 更新最新指令的狀態（例如：done、processing 等）"""
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if not status:
        return jsonify({"error": "status is required"}), 400

    latest_command["status"] = status

    if "command" in data:
        latest_command["command"] = data["command"]

    print(f"🔄 指令狀態已更新為：{status}")
    return jsonify({"result": "ok", "latest_command": latest_command})


@app.route('/clear_command', methods=['POST'])
def clear_command():
    # 💡 [PC 用] 讓 PC 在處理完畢後，可以 POST 清除 Render 上的指令
    latest_command["command"] = None
    latest_command["status"] = "idle"
    print("🧹 指令已由 PC 上位機清空，準備下一指令")
    return {"result": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
