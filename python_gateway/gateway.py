import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# ================= CẤU HÌNH INFLUXDB =================
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "tZfTsisdVOPfs9OfVOcjstnryewHe341Xf0eXkrmQv77nfgLT9M23cOeLeIlcyLCVJDqbdcd3v1ljgn3ugXLMA=="
INFLUX_ORG = "PTIT"
INFLUX_BUCKET = "sensor_data"

# ================= CẤU HÌNH MQTT =================
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/telemetry"

# Khởi tạo kết nối đến InfluxDB
db_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = db_client.write_api(write_options=SYNCHRONOUS)

# Hàm chạy khi kết nối thành công với MQTT Broker
def on_connect(client, userdata, flags, rc):
    print(f"✅ Đã kết nối MQTT Broker (Mosquitto). Mã trạng thái: {rc}")
    client.subscribe(MQTT_TOPIC)
    print(f"📡 Đang lắng nghe dữ liệu từ topic: {MQTT_TOPIC} ...\n")

# Hàm chạy khi có tin nhắn (dữ liệu) gửi đến topic
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"📥 Nhận được chuỗi JSON: {payload}")
    
    try:
        # Chuyển chuỗi JSON thành Dictionary Python
        data = json.loads(payload)
        
        # Tiền xử lý: Kiểm tra xem có đủ trường dữ liệu không
        temp = data.get("temperature")
        hum = data.get("humidity")
        dist = data.get("distance_cm")
        
        if temp is not None and hum is not None:
            # Tạo một "Điểm dữ liệu" (Point) để ghi vào InfluxDB
            point = Point("environment_metrics") \
                .tag("device_id", "ESP32_Wokwi") \
                .field("temperature", float(temp)) \
                .field("humidity", float(hum)) \
                .field("distance", float(dist) if dist else 0.0)
            
            # Thực thi ghi vào Database
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            print("💾 -> Đã ghi thành công vào InfluxDB!\n")
        else:
            print("⚠️ -> Dữ liệu không hợp lệ (thiếu nhiêt độ/độ ẩm). Bỏ qua.\n")
            
    except json.JSONDecodeError:
        print("❌ -> Lỗi: Không thể phân tích cú pháp JSON.\n")
    except Exception as e:
        print(f"❌ -> Lỗi hệ thống: {e}\n")

# Khởi tạo MQTT Client và gán các hàm callback
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Kết nối và duy trì vòng lặp lắng nghe
print("🚀 Đang khởi động hệ thống Gateway...")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_forever()