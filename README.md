# Hệ Thống Thu Thập Và Giám Sát Dữ Liệu IoT Cục Bộ

Dự án thực hành xây dựng luồng dữ liệu IoT độc lập, thu thập thông số môi trường từ Node cảm biến (ESP32), định tuyến qua MQTT, lưu trữ tại InfluxDB và trực quan hóa thời gian thực bằng Streamlit.

**Sinh viên thực hiện:** Nguyễn Đình Mạnh (B23DCAT181)
**Học viện:** Công nghệ Bưu chính Viễn thông (PTIT)

## 1. Cấu trúc mã nguồn
- `firmware/`: Mã nguồn C++ cho ESP32 và sơ đồ phần cứng `diagram.json` (chạy trên Wokwi).
- `python_gateway/gateway.py`: Script Subscribe MQTT và ghi dữ liệu InfluxDB.
- `python_gateway/preprocess.py`: Script Pandas truy vấn và làm sạch dữ liệu rác (loại bỏ các bản ghi `0.0`).
- `python_gateway/app.py`: Web Dashboard Streamlit giám sát thời gian thực.
- `requirements.txt`: Danh sách thư viện phụ thuộc.

## 2. Yêu cầu hệ thống
- Python 3.9+
- Cơ sở dữ liệu InfluxDB (Local) đang chạy tại port `8086`.
- Trình mô phỏng Wokwi (tích hợp trên VS Code hoặc bản Web).

## 3. Hướng dẫn triển khai (Step-by-Step)

**Bước 1: Cài đặt thư viện môi trường**
Mở Terminal tại thư mục gốc của dự án và chạy lệnh:
`pip install -r requirements.txt`

**Bước 2: Cấu hình Database**
Mở file `gateway.py` và `app.py`, cập nhật lại thông số `INFLUX_TOKEN` tương ứng với tài khoản InfluxDB nội bộ của bạn.

**Bước 3: Khởi động hệ thống**
Khởi chạy lần lượt các thành phần hệ thống trên các Terminal riêng biệt:
1. **Node mạng (ESP32):** Nạp code `main.cpp` và chạy mô phỏng Wokwi.
2. **Gateway:** `cd python_gateway` -> Chạy lệnh `python gateway.py`
3. **Web Dashboard:** Tại thư mục `python_gateway` -> Chạy lệnh `streamlit run app.py`

*Lưu ý kỹ thuật:* Do hạn chế về độ trễ đồng bộ xung nhịp (Timing delay) của giao thức 1-wire trên Wokwi extension của VS Code, cảm biến DHT22 có thể trả về `NaN`. Phiên bản `main.cpp` hiện tại sử dụng thuật toán giả lập dữ liệu trong dải môi trường thực tế để đảm bảo Pipeline thu thập, Database và Dashboard được vận hành thông suốt phục vụ kiểm thử.