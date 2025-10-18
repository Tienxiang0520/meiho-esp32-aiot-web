document.addEventListener("DOMContentLoaded", () => {
  const sendBtn = document.getElementById("sendBtn");
  const commandInput = document.getElementById("commandInput");
  const statusBox = document.getElementById("status");

  // 1. MQTT 客戶端設定 (使用 WebSocket 連接)
  const MQTT_SERVER = "broker.hivemq.com";
  const MQTT_PORT = 8000; // HiveMQ 公開 Broker 的 WebSockets Port
  const STATUS_TOPIC = "/esp32/status"; // 監聽 ESP32 的狀態主題
  
  // 建立 MQTT 連線實例
  const client = new Paho.MQTT.Client(MQTT_SERVER, MQTT_PORT, "/ws", "ClientID_" + parseInt(Math.random() * 100, 10));

  // 2. 設定連線和訊息接收的回呼函式
  client.onConnectionLost = onConnectionLost;
  client.onMessageArrived = onMessageArrived;
  client.connect({ onSuccess: onConnect, useSSL: false }); // 連線到 Broker

  function onConnect() {
    console.log("✅ MQTT Client Connected!");
    client.subscribe(STATUS_TOPIC); // 訂閱 ESP32 的狀態主題
    statusBox.innerHTML = "<p>📡 Web 已連線到 Broker，等待指令...</p>";
  }

  function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
      console.log("❌ MQTT Connection Lost: " + responseObject.errorMessage);
      statusBox.innerHTML = `<p style='color:red;'>❌ MQTT 連線中斷！</p>`;
    }
  }

  function onMessageArrived(message) {
    if (message.destinationName === STATUS_TOPIC) {
      const payload = message.payloadString;
      console.log("🔔 Received Status: " + payload);
      
      // 實時更新狀態
      if (payload.includes("done")) {
        statusBox.innerHTML = `<p>✅ 硬體回報：${payload}</p>`;
      }
    }
  }

  // 讓 Enter 直接送出
  commandInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendBtn.click();
  });
  
  sendBtn.addEventListener("click", async () => {
    const command = commandInput.value.trim();
    if (!command) return alert("請輸入指令！");

    // 🔒 防連點 + 改文字
    sendBtn.disabled = true;
    const originalText = sendBtn.textContent;
    sendBtn.textContent = "處理中...";
    statusBox.innerHTML = "<p>🧠 AI 正在思考中... (等待硬體實時回覆)</p>";

    try {
      // === 第一步：送出指令給 Flask (Render) ===
      await fetch("/control", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "command=" + encodeURIComponent(command),
      });

      // 成功送出後，前端只需等待 MQTT 訊息。

    } catch (err) {
      statusBox.innerHTML = `<p style='color:red;'>❌ 發送失敗：${err}</p>`;
    } finally {
      // ✅ 恢復按鈕、清空輸入、重新聚焦
      sendBtn.textContent = originalText;
      sendBtn.disabled = false;
      commandInput.value = "";
      commandInput.focus();
    }
  });
});