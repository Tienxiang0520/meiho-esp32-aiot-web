from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

latest_command = {"command": None}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    user_input = request.form['command']
    latest_command["command"] = user_input
    return render_template('index.html', result=f"📩 指令已送出：{user_input}")

@app.route('/latest_command')
def get_command():
    return jsonify(latest_command)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
