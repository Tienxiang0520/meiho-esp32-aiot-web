from flask import Flask, render_template, request, jsonify
import os, threading, time

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
