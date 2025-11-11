import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import DB_CONFIG

def detect_outliers():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        
        query = """
            SELECT 
                cw.reading_id,
                ws.city_name,
                cw.temperature,
                cw.pressure,
                cw.wind_speed,
                cw.timestamp,
                LAG(cw.temperature) OVER (PARTITION BY cw.station_id ORDER BY cw.timestamp) as prev_temp,
                LAG(cw.pressure) OVER (PARTITION BY cw.station_id ORDER BY cw.timestamp) as prev_pressure
            FROM current_weather cw
            JOIN weather_stations ws ON cw.station_id = ws.station_id
            ORDER BY cw.timestamp DESC;
        """
        
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print("No hay datos suficientes para detectar outliers")
            conn.close()
            return
        
        print("\n=== SISTEMA DE DETECCION DE OUTLIERS ===\n")
        
        outliers_found = []
        
        df['temp_change'] = abs(df['temperature'] - df['prev_temp'])
        temp_outliers = df[df['temp_change'] > 5]
        
        if not temp_outliers.empty:
            print("ALERTA: Cambios bruscos de temperatura detectados:")
            for _, row in temp_outliers.iterrows():
                msg = f"  - {row['city_name']}: Cambio de {row['temp_change']:.1f}C"
                print(msg)
                outliers_found.append(msg)
        
        df['pressure_zscore'] = np.abs((df['pressure'] - df['pressure'].mean()) / df['pressure'].std())
        pressure_outliers = df[df['pressure_zscore'] > 2]
        
        if not pressure_outliers.empty:
            print("\nALERTA: Anomalias en presion atmosferica:")
            for _, row in pressure_outliers.iterrows():
                msg = f"  - {row['city_name']}: Presion anomala de {row['pressure']:.1f} hPa (Z-score: {row['pressure_zscore']:.2f})"
                print(msg)
                outliers_found.append(msg)
        
        wind_outliers = df[df['wind_speed'] > 15]
        
        if not wind_outliers.empty:
            print("\nALERTA: Vientos extremos detectados:")
            for _, row in wind_outliers.iterrows():
                msg = f"  - {row['city_name']}: Viento de {row['wind_speed']:.1f} m/s"
                print(msg)
                outliers_found.append(msg)
        
        print(f"\n=== ESTADISTICAS ===")
        print(f"Total de lecturas analizadas: {len(df)}")
        print(f"Outliers detectados: {len(outliers_found)}")
        print(f"Temperatura promedio: {df['temperature'].mean():.1f}C")
        print(f"Temperatura min/max: {df['temperature'].min():.1f}C / {df['temperature'].max():.1f}C")
        print(f"Presion promedio: {df['pressure'].mean():.1f} hPa")
        print(f"Viento promedio: {df['wind_speed'].mean():.1f} m/s")
        
        if not outliers_found:
            print("\nNo se detectaron anomalias en los datos")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    detect_outliers()
