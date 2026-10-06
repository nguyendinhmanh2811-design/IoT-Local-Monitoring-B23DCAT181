import pandas as pd
from influxdb_client import InfluxDBClient

# ================= CẤU HÌNH INFLUXDB =================
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "tZfTsisdVOPfs9OfVOcjstnryewHe341Xf0eXkrmQv77nfgLT9M23cOeLeIlcyLCVJDqbdcd3v1ljgn3ugXLMA==" 
INFLUX_ORG = "PTIT"
INFLUX_BUCKET = "sensor_data"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

flux_query = f"""
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "environment_metrics")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
"""

try:
    result = query_api.query_data_frame(flux_query)
    df = pd.concat(result, ignore_index=True) if isinstance(result, list) else result
    
    if not df.empty:
        # 1. Xử lý đồng nhất tên cột khoảng cách
        dist_col = 'distance_cm' if 'distance_cm' in df.columns else 'distance'
        if dist_col not in df.columns:
            dist_col = None # Đề phòng trường hợp không có cả hai cột
            
        print(f"Tổng số bản ghi ban đầu: {len(df)}")
        
        # 2. Lọc dữ liệu: Bỏ qua các giá trị 0.0 ảo
        df_cleaned = df[(df['temperature'] > 0) & (df['humidity'] > 0)]
        
        print("\n--- BẢNG DỮ LIỆU ĐÃ LÀM SẠCH ---")
        if df_cleaned.empty:
            print("[!] Toàn bộ dữ liệu đang là 0.0. Hãy vào Wokwi kéo thanh trượt cảm biến để tạo số liệu thực!")
        else:
            cols_to_print = ['_time', 'temperature', 'humidity']
            if dist_col: cols_to_print.append(dist_col)
            
            print(df_cleaned[cols_to_print].tail(5)) # In ra 5 dòng mới nhất
            
            print("\n--- THỐNG KÊ CƠ BẢN ---")
            stats_cols = ['temperature', 'humidity']
            if dist_col: stats_cols.append(dist_col)
            print(df_cleaned[stats_cols].describe())
            
except Exception as e:
    print(f"Lỗi truy vấn: {e}")