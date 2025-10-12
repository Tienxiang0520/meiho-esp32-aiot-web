from flask import Flask, render_template, request
import paho.mqtt.publish as publish
import os

app = Flask(__name__)

MQTT_SERVER = "broker.hivemq.com"
TOPIC = "/esp32/led"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    command = request.form['command']
    if "開" in command:
        publish.single(TOPIC, "LED_ON", hostname=MQTT_SERVER)
        result = "已發送：LED_ON"
    elif "關" in command:
        publish.single(TOPIC, "LED_OFF", hostname=MQTT_SERVER)
        result = "已發送：LED_OFF"
    else:
        result = "未知指令"
    return render_template('index.html', result=result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
