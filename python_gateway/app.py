import streamlit as st
import pandas as pd
from influxdb_client import InfluxDBClient

# ================= CẤU HÌNH =================
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "tZfTsisdVOPfs9OfVOcjstnryewHe341Xf0eXkrmQv77nfgLT9M23cOeLeIlcyLCVJDqbdcd3v1ljgn3ugXLMA==" 
INFLUX_ORG = "PTIT"
INFLUX_BUCKET = "sensor_data"

st.set_page_config(page_title="IoT Dashboard", layout="wide")
st.title("🎛️ Bảng Điều Khiển Cảm Biến IoT")

# Hàm lấy dữ liệu (cập nhật tự động)
def load_data():
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -15m)
      |> filter(fn: (r) => r["_measurement"] == "environment_metrics")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    try:
        result = client.query_api().query_data_frame(query)
        df = pd.concat(result, ignore_index=True) if isinstance(result, list) else result
        if not df.empty:
            df = df[(df['temperature'] > 0) & (df['humidity'] > 0)] # Lọc rác
        return df
    except:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Đang chờ dữ liệu từ cảm biến...")
else:
    # Lấy dòng dữ liệu mới nhất
    latest = df.iloc[-1]
    
    # Hiển thị các ô thông số nổi bật
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ Nhiệt độ", f"{latest['temperature']:.1f} °C")
    col2.metric("💧 Độ ẩm", f"{latest['humidity']:.1f} %")
    
    dist_val = latest.get('distance_cm', latest.get('distance', 0))
    col3.metric("📏 Khoảng cách", f"{dist_val:.1f} cm")

    # Vẽ biểu đồ biến thiên
    st.subheader("Biểu đồ nhiệt độ & độ ẩm (15 phút qua)")
    chart_data = df.set_index('_time')[['temperature', 'humidity']]
    st.line_chart(chart_data)
    
    # Nút làm mới dữ liệu thủ công
    if st.button("Cập nhật dữ liệu"):
        st.rerun()