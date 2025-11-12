import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Climatico Costa Caribe", layout="wide")

def get_current_weather():
    """Obtener datos del clima conectándose cada vez"""
    try:
        # Crear nueva conexión cada vez
        conn = psycopg2.connect(
            host=st.secrets["database"]["DB_HOST"],
            port=st.secrets["database"]["DB_PORT"],
            database=st.secrets["database"]["DB_NAME"],
            user=st.secrets["database"]["DB_USER"],
            password=st.secrets["database"]["DB_PASSWORD"],
            sslmode=st.secrets["database"]["DB_SSLMODE"]
        )
        
        query = """
            SELECT 
                ws.city_name,
                ws.latitude,
                ws.longitude,
                cw.temperature,
                cw.humidity,
                cw.wind_speed,
                cw.timestamp
            FROM current_weather cw
            JOIN weather_stations ws ON cw.station_id = ws.station_id
            ORDER BY cw.timestamp DESC
            LIMIT 100;
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        return df
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return pd.DataFrame()

st.title("🌤️ Dashboard Climatico Costa Caribe Colombiana")

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if st.button("🔄 Actualizar"):
        st.rerun()

df = get_current_weather()

if not df.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ Mapa de Temperaturas")
        
        df_unique = df.drop_duplicates('city_name')
        
        fig = px.scatter_mapbox(
            df_unique,
            lat="latitude",
            lon="longitude",
            color="temperature",
            hover_name="city_name",
            hover_data={
                "temperature": ":.1f°C",
                "humidity": ":.0f%",
                "wind_speed": ":.1f m/s",
                "latitude": False,
                "longitude": False
            },
            color_continuous_scale="RdYlBu_r",
            zoom=5.5,
            height=500
        )
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Temperaturas Actuales")
        for _, row in df_unique.iterrows():
            st.metric(
                label=row['city_name'],
                value=f"{row['temperature']:.1f}°C",
                delta=f"{row['humidity']:.0f}% humedad"
            )
    
    st.markdown("---")
    
    st.subheader("📋 Datos Recientes")
    st.dataframe(
        df[['city_name', 'temperature', 'humidity', 'wind_speed', 'timestamp']].head(20),
        use_container_width=True
    )
    
    st.success(f"✅ Mostrando {len(df)} lecturas del clima")
    
else:
    st.warning("⚠️ No hay datos disponibles en la base de datos.")
    st.info("💡 Ejecuta `python data_streaming.py` en tu computadora local para generar datos.")


