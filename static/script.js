document.addEventListener("DOMContentLoaded", () => {
  const sendBtn = document.getElementById("sendBtn");
  const commandInput = document.getElementById("commandInput");
  const statusBox = document.getElementById("status");

  // 讓 Enter 也能送出
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
      // 傳送使用者輸入給 Flask
      const response = await fetch("/control", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "command=" + encodeURIComponent(command),
      });

      const html = await response.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const newResult = doc.querySelector(".result")?.innerHTML || "（無回應）";

      // 顯示 AI 回覆
      statusBox.innerHTML = newResult;

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
