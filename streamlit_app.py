import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from config import DB_CONFIG
import time

st.set_page_config(page_title="Dashboard Climatico Costa Caribe", layout="wide")

@st.cache_resource
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

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

st.title("Dashboard Climatico Costa Caribe Colombiana")

if st.button("Actualizar"):
    st.rerun()

df = get_current_weather()

if not df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Mapa de Temperaturas")
        fig = px.scatter_mapbox(
            df.drop_duplicates('city_name'),
            lat="latitude",
            lon="longitude",
            color="temperature",
            hover_name="city_name",
            zoom=5
        )
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig)
    
    with col2:
        st.subheader("Datos Recientes")
        st.dataframe(df.head(20))
else:
    st.warning("No hay datos disponibles")
