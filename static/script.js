// script.js
document.addEventListener("DOMContentLoaded", () => {
  const sendBtn = document.getElementById("sendBtn");
  const commandInput = document.getElementById("commandInput");
  const statusBox = document.getElementById("status");

  sendBtn.addEventListener("click", async () => {
    const command = commandInput.value.trim();
    if (!command) return alert("請輸入指令！");
    statusBox.innerHTML = "<p>🧠 AI 正在思考中...</p>";

    try {
      const response = await fetch("/control", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "command=" + encodeURIComponent(command)
      });

      const html = await response.text();
      // 用一個臨時 DOM 解析 Flask 回傳的內容
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const newResult = doc.querySelector(".result").innerHTML;

      statusBox.innerHTML = newResult;
    } catch (err) {
      statusBox.innerHTML = "<p style='color:red;'>❌ 發送失敗：" + err + "</p>";
    }
  });
});
