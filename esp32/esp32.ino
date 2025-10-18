#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Wi-Fi 和 MQTT 設定 (保持不變)
const char* ssid = "OPPO A5 Pro 5G p7cf";
const char* password = "00000000";
const char* mqtt_server = "broker.hivemq.com";

WiFiClient espClient;
PubSubClient client(espClient);
int ledPin = 4;

// ===== Wi-Fi 連線 =====
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    display.clearDisplay();
    display.setCursor(0, 0);
    display.print("Connecting WiFi...");
    display.display();
  }

  Serial.println("\n✅ WiFi connected!");
  Serial.print("📶 IP: ");
  Serial.println(WiFi.localIP());

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("WiFi Connected!");
  display.setCursor(0, 16);
  display.print("IP: ");
  display.println(WiFi.localIP());
  display.display();
}

// ===== MQTT 收到訊息時呼叫 (已修正並新增回報) =====
void callback(char* topic, byte* message, unsigned int length) {
  String msg;
  String status_msg = ""; 
  for (int i = 0; i < length; i++) {
    msg += (char)message[i];
  }

  Serial.print("📨 Topic: ");
  Serial.println(topic);
  Serial.print("📦 Payload: ");
  Serial.println(msg);

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("MQTT Message:");
  display.setCursor(0, 16);
  display.println(msg);
  display.display();

  if (msg == "LED_ON") {
    digitalWrite(ledPin, HIGH);
    display.setCursor(0, 32);
    display.println(" LED ON");
    display.display();
    status_msg = "LED_ON done"; 
  } else if (msg == "LED_OFF") {
    digitalWrite(ledPin, LOW);
    display.setCursor(0, 32);
    display.println(" LED OFF");
    display.display();
    status_msg = "LED_OFF done"; 
  }

  // 📢 執行完畢後，立即發布狀態到新主題
  if (status_msg != "") {
    client.publish("/esp32/status", status_msg.c_str()); 
    Serial.print("📢 Published status: ");
    Serial.println(status_msg);
  }
} // <-- 修正：if (status_msg != "") 區塊結束

// ===== MQTT 重新連線機制 =====
void reconnect() {
  while (!client.connected()) {
    Serial.print("🔁 MQTT reconnect...");
    if (client.connect("ESP32Client_TienXiang")) {
      Serial.println("connected ✅");
      client.subscribe("/esp32/led");

      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("MQTT Connected!");
      display.display();
    } else {
      Serial.print("❌ failed, rc=");
      Serial.print(client.state());
      Serial.println(" retry in 5s...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

  // OLED 初始化
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED not found!");
    for (;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("ESP32 Booting...");
  display.display();

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}