document.addEventListener("DOMContentLoaded", () => {
  const sendBtn = document.getElementById("sendBtn");
  const commandInput = document.getElementById("commandInput");
  const statusBox = document.getElementById("status");

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
    statusBox.innerHTML = "<p>🧠 AI 正在思考中...</p>";

    try {
      // === 第一步：送出指令給 Flask ===
      const response = await fetch("/control", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "command=" + encodeURIComponent(command),
      });

      const html = await response.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const newResult = doc.querySelector(".result")?.innerHTML || "（無回應）";
      statusBox.innerHTML = newResult + "<p>📡 等待上位機處理中...</p>";

      // === 第二步：輪詢狀態直到完成 ===
      let success = false;
      for (let i = 0; i < 15; i++) { // 最多等 15 秒
        const res = await fetch("/latest_command");
        const data = await res.json();
        if (data.status && data.status.includes("done")) {
          success = true;
          statusBox.innerHTML += `<p>✅ 上位機回報：${data.status}</p>`;
          break;
        }
        await new Promise(r => setTimeout(r, 1000)); // 每秒查一次
      }

      if (!success) {
        statusBox.innerHTML += "<p style='color:orange;'>⚠️ 上位機回覆逾時</p>";
      }

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
