#include <WiFi.h> 
#include <PubSubClient.h> 

const char* WIFI_SSID = "Wokwi-GUEST"; 
const char* WIFI_PASSWORD = ""; 
const char* MQTT_SERVER = "broker.emqx.io"; 
const int MQTT_PORT = 1883; 

const int LED_PIN = 2; 
const unsigned long SEND_INTERVAL_MS = 5000; 

WiFiClient wifiClient; 
PubSubClient mqttClient(wifiClient); 
unsigned long lastSend = 0; 
unsigned long sequenceNo = 0; 

void connectWiFi() { 
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6); 
  Serial.print("Connecting WiFi"); 
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  } 
  Serial.println(" connected"); 
} 

void connectMQTT() { 
  while (!mqttClient.connected()) { 
    String clientId = "ESP32-Bai2-" + String((uint32_t)ESP.getEfuseMac(), HEX); 
    Serial.print("Connecting MQTT..."); 
    if (mqttClient.connect(clientId.c_str())) { 
      Serial.println(" connected"); 
    } else { 
      Serial.printf(" failed, rc=%d. Retry in 2 s\n", mqttClient.state()); 
      delay(2000); 
    } 
  } 
} 

void setup() { 
  Serial.begin(115200); 
  pinMode(LED_PIN, OUTPUT); 
  
  connectWiFi(); 
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT); 
  mqttClient.setBufferSize(256); 
  
  // Khởi tạo mầm ngẫu nhiên để sinh số liệu
  randomSeed(analogRead(0));
} 

void loop() { 
  if (WiFi.status() != WL_CONNECTED) connectWiFi(); 
  if (!mqttClient.connected()) connectMQTT(); 
  mqttClient.loop(); 
  
  unsigned long now = millis(); 
  if (now - lastSend < SEND_INTERVAL_MS) return; 
  lastSend = now; 
  
  // SINH DỮ LIỆU GIẢ LẬP ĐỂ TEST DATABASE
  // Nhiệt độ từ 20.0 đến 35.0 độ C
  float temperature = 20.0 + random(0, 150) / 10.0; 
  // Độ ẩm từ 50.0 đến 90.0 %
  float humidity = 50.0 + random(0, 400) / 10.0;    
  // Khoảng cách từ 10.0 đến 200.0 cm
  float distance = 10.0 + random(0, 1900) / 10.0;   
  
  sequenceNo++; 
  char payload[256]; 
  snprintf(payload, sizeof(payload), 
    "{\"temperature\":%.2f,\"humidity\":%.2f,\"distance_cm\":%.2f," 
    "\"rssi\":%d,\"sequence\":%lu,\"uptime_s\":%lu}", 
    temperature, humidity, distance, WiFi.RSSI(), 
    sequenceNo, millis() / 1000); 
    
  bool ok = mqttClient.publish("sensor/telemetry", payload); 
  Serial.printf("%s | publish=%s\n", payload, ok ? "OK" : "FAILED"); 
  
  digitalWrite(LED_PIN, HIGH); 
  delay(80); 
  digitalWrite(LED_PIN, LOW); 
}