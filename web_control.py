from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

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
    return render_template('index.html', result=f"📩 指令已送出：{user_input}")

@app.route('/latest_command')
def get_command():
    return jsonify(latest_command)

@app.route('/update_status', methods=['POST'])
def update_status():
    """上位機回報完成狀態"""
    data = request.get_json()
    latest_command["status"] = data.get("status", "unknown")

    # ✅ 如果收到 done，清空狀態
    if "done" in latest_command["status"]:
        print("🔄 上位機處理完成，清空指令狀態")
        latest_command["command"] = None
        latest_command["status"] = "idle"

    return {"result": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
