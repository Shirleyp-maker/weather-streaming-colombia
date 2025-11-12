import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
import pickle
from datetime import datetime

st.set_page_config(page_title="Dashboard Climatico Costa Caribe", layout="wide", page_icon="🌤️")

# Estilos CSS
st.markdown("""
<style>
.big-metric { font-size: 24px; font-weight: bold; }
.update-time { color: #666; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

def get_current_weather():
    """Obtener datos del clima con conexión fresca"""
    try:
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
                cw.pressure,
                cw.cloud_cover,
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
        st.error(f"Error de conexión: {str(e)}")
        return pd.DataFrame()

@st.cache_resource
def train_ml_model(df):
    """Entrenar modelo ML con los datos disponibles"""
    try:
        # Preparar datos
        df_clean = df.dropna(subset=['humidity', 'pressure', 'wind_speed', 'cloud_cover', 'temperature'])
        
        if len(df_clean) < 10:
            return None, None, "Datos insuficientes"
        
        X = df_clean[['humidity', 'pressure', 'wind_speed', 'cloud_cover']].values
        y = df_clean['temperature'].values
        
        # Crear y entrenar modelo
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = SGDRegressor(max_iter=1000, tol=1e-3, random_state=42)
        model.fit(X_scaled, y)
        
        return model, scaler, None
        
    except Exception as e:
        return None, None, str(e)

def predict_temperature(model, scaler, humidity, pressure, wind_speed, cloud_cover):
    """Hacer predicción de temperatura"""
    if model is None or scaler is None:
        return None
    
    features = np.array([[humidity, pressure, wind_speed, cloud_cover]])
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)
    return prediction[0]

# ===== TÍTULO Y HEADER =====
st.title("🌤️ Dashboard Climático Costa Caribe Colombiana")

# Botones de control
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
with col_btn1:
    if st.button("🔄 Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
        
with col_btn2:
    auto_refresh = st.checkbox("Auto-refresh")

# ===== OBTENER DATOS =====
df = get_current_weather()

if not df.empty:
    # Mostrar hora de última actualización
    last_update = df['timestamp'].max()
    st.markdown(f"<p class='update-time'>📅 Última actualización: {last_update}</p>", unsafe_allow_html=True)
    
    # ===== SECCIÓN 1: MAPA Y TEMPERATURAS =====
    st.markdown("---")
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
        st.subheader("🌡️ Temperaturas Actuales")
        for _, row in df_unique.iterrows():
            st.metric(
                label=row['city_name'],
                value=f"{row['temperature']:.1f}°C",
                delta=f"{row['humidity']:.0f}% humedad"
            )
    
    # ===== SECCIÓN 2: PREDICCIONES ML INTERACTIVAS =====
    st.markdown("---")
    st.subheader("🤖 Predictor de Temperatura con Machine Learning")
    
    with st.expander("ℹ️ Cómo funciona el predictor", expanded=False):
        st.write("""
        Este modelo de Machine Learning predice la temperatura basándose en:
        - **Humedad** (%)
        - **Presión atmosférica** (hPa)
        - **Velocidad del viento** (m/s)
        - **Cobertura de nubes** (%)
        
        El modelo se entrena con todos los datos históricos disponibles en la base de datos.
        """)
    
    # Entrenar modelo
    model, scaler, error = train_ml_model(df)
    
    if model is not None:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### 🎯 Ingresa las condiciones climáticas:")
            humidity_input = st.slider("💧 Humedad (%)", 0, 100, 80, 5)
            pressure_input = st.slider("🌀 Presión (hPa)", 980, 1040, 1010, 5)
        
        with col2:
            st.markdown("##### ")
            st.write("")  # Espaciado
            wind_input = st.slider("💨 Viento (m/s)", 0, 40, 10, 1)
            cloud_input = st.slider("☁️ Nubes (%)", 0, 100, 50, 10)
        
        with col3:
            st.markdown("##### 🌡️ Predicción:")
            if st.button("🔮 Predecir Temperatura", use_container_width=True):
                prediction = predict_temperature(model, scaler, humidity_input, pressure_input, wind_input, cloud_input)
                if prediction is not None:
                    st.markdown(f"<div class='big-metric' style='color: #FF4B4B;'>🌡️ {prediction:.1f}°C</div>", unsafe_allow_html=True)
                    
                    # Comparar con promedios actuales
                    avg_temp = df['temperature'].mean()
                    diff = prediction - avg_temp
                    if diff > 0:
                        st.success(f"↑ {abs(diff):.1f}°C más cálido que el promedio actual ({avg_temp:.1f}°C)")
                    else:
                        st.info(f"↓ {abs(diff):.1f}°C más frío que el promedio actual ({avg_temp:.1f}°C)")
                    
                    # Mostrar condiciones ingresadas
                    st.markdown("**Condiciones ingresadas:**")
                    st.write(f"- Humedad: {humidity_input}%")
                    st.write(f"- Presión: {pressure_input} hPa")
                    st.write(f"- Viento: {wind_input} m/s")
                    st.write(f"- Nubes: {cloud_input}%")
    else:
        st.warning("⚠️ No hay suficientes datos para entrenar el modelo. Ejecuta `data_streaming.py` para generar más datos.")
    
    # ===== SECCIÓN 3: DETECCIÓN DE OUTLIERS =====
    st.markdown("---")
    st.subheader("🚨 Detección de Anomalías en Tiempo Real")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 🌡️ Cambios Bruscos de Temperatura")
        df['temp_change'] = df.groupby('city_name')['temperature'].diff().abs()
        temp_outliers = df[df['temp_change'] > 5]
        if not temp_outliers.empty:
            st.error(f"⚠️ {len(temp_outliers)} alertas detectadas")
            for _, row in temp_outliers.head(3).iterrows():
                st.write(f"• {row['city_name']}: Cambio de {row['temp_change']:.1f}°C")
        else:
            st.success("✅ No se detectaron cambios bruscos")
    
    with col2:
        st.markdown("##### 💨 Vientos Extremos")
        wind_outliers = df[df['wind_speed'] > 15]
        if not wind_outliers.empty:
            st.error(f"⚠️ {len(wind_outliers)} alertas detectadas")
            df_wind_unique = wind_outliers.drop_duplicates('city_name')
            for _, row in df_wind_unique.head(3).iterrows():
                st.write(f"• {row['city_name']}: {row['wind_speed']:.1f} m/s")
        else:
            st.success("✅ Vientos normales")
    
    with col3:
        st.markdown("##### 🌀 Presión Anómala")
        pressure_mean = df['pressure'].mean()
        pressure_std = df['pressure'].std()
        df['pressure_zscore'] = np.abs((df['pressure'] - pressure_mean) / pressure_std)
        pressure_outliers = df[df['pressure_zscore'] > 2]
        if not pressure_outliers.empty:
            st.error(f"⚠️ {len(pressure_outliers)} alertas detectadas")
            df_press_unique = pressure_outliers.drop_duplicates('city_name')
            for _, row in df_press_unique.head(3).iterrows():
                st.write(f"• {row['city_name']}: {row['pressure']:.1f} hPa")
        else:
            st.success("✅ Presión normal")
    
    # ===== SECCIÓN 4: TABLA DE DATOS =====
    st.markdown("---")
    st.subheader("📋 Datos Recientes")
    
    display_df = df[['city_name', 'temperature', 'humidity', 'wind_speed', 'pressure', 'timestamp']].head(20)
    display_df.columns = ['Ciudad', 'Temp (°C)', 'Humedad (%)', 'Viento (m/s)', 'Presión (hPa)', 'Timestamp']
    st.dataframe(display_df, use_container_width=True)
    
    # Estadísticas generales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total de Lecturas", len(df))
    with col2:
        st.metric("🌡️ Temp. Promedio", f"{df['temperature'].mean():.1f}°C")
    with col3:
        st.metric("🌡️ Temp. Máxima", f"{df['temperature'].max():.1f}°C")
    with col4:
        st.metric("🌡️ Temp. Mínima", f"{df['temperature'].min():.1f}°C")
    
    st.success(f"✅ Dashboard actualizado correctamente con {len(df)} lecturas")
    
else:
    st.warning("⚠️ No hay datos disponibles en la base de datos.")
    st.info("💡 Ejecuta `python data_streaming.py` en tu computadora local para generar datos.")

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()


