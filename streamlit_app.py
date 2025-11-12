import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Dashboard Climatico Costa Caribe", layout="wide")

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host=st.secrets["database"]["DB_HOST"],
        port=st.secrets["database"]["DB_PORT"],
        database=st.secrets["database"]["DB_NAME"],
        user=st.secrets["database"]["DB_USER"],
        password=st.secrets["database"]["DB_PASSWORD"],
        sslmode=st.secrets["database"]["DB_SSLMODE"]
    )

def get_current_weather():
    conn = get_connection()
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

st.title("🌤️ Dashboard Climatico Costa Caribe Colombiana")

if st.button("🔄 Actualizar"):
    st.rerun()

try:
    df = get_current_weather()
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🗺️ Mapa de Temperaturas")
            fig = px.scatter_mapbox(
                df.drop_duplicates('city_name'),
                lat="latitude",
                lon="longitude",
                color="temperature",
                hover_name="city_name",
                hover_data={"temperature": ":.1f", "humidity": True, "wind_speed": ":.1f"},
                color_continuous_scale="RdYlBu_r",
                zoom=5
            )
            fig.update_layout(mapbox_style="open-street-map", height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Datos Recientes")
            st.dataframe(df.head(20), use_container_width=True)
    else:
        st.warning("⚠️ No hay datos disponibles. Ejecuta data_streaming.py primero.")
        
except Exception as e:
    st.error(f"❌ Error de conexión: {str(e)}")
    st.info("Verifica que las credenciales en Secrets estén correctas y que el servidor Azure esté accesible.")

