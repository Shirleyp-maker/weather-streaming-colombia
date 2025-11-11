import psycopg2
import requests
import time
from datetime import datetime
from config import DB_CONFIG

# Coordenadas de las ciudades
CITIES = [
    {"id": 1, "name": "Santa Marta", "lat": 11.2408, "lon": -74.2120},
    {"id": 2, "name": "Barranquilla", "lat": 10.9685, "lon": -74.7813},
    {"id": 3, "name": "Cartagena", "lat": 10.3910, "lon": -75.4794},
    {"id": 4, "name": "Valledupar", "lat": 10.4631, "lon": -73.2532},
    {"id": 5, "name": "Riohacha", "lat": 11.5444, "lon": -72.9072},
    {"id": 6, "name": "Monteria", "lat": 8.7479, "lon": -75.8814},
    {"id": 7, "name": "Sincelejo", "lat": 9.3047, "lon": -75.3978},
    {"id": 8, "name": "San Andres", "lat": 12.5847, "lon": -81.7006}
]

def fetch_weather_data(lat, lon):
    """Obtener datos del clima desde Open-Meteo API"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m,precipitation,cloud_cover,weather_code"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error obteniendo datos: {e}")
        return None

def insert_weather_reading(cursor, station_id, data):
    """Insertar lectura del clima en la base de datos"""
    try:
        current = data.get("current", {})
        
        cursor.execute("""
            INSERT INTO current_weather 
            (station_id, temperature, humidity, pressure, wind_speed, wind_direction, 
             precipitation, cloud_cover, weather_code, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            station_id,
            current.get("temperature_2m"),
            current.get("relative_humidity_2m"),
            current.get("pressure_msl"),
            current.get("wind_speed_10m"),
            current.get("wind_direction_10m"),
            current.get("precipitation"),
            current.get("cloud_cover"),
            current.get("weather_code"),
            datetime.now()
        ))
        return True
    except Exception as e:
        print(f"Error insertando lectura: {e}")
        return False

def stream_weather_data(duration_minutes=5):
    """Streaming de datos del clima por duracion especificada"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"\nIniciando streaming de datos climaticos por {duration_minutes} minutos...")
        print("Presiona Ctrl+C para detener\n")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        total_insertions = 0
        
        while time.time() < end_time:
            iteration_start = time.time()
            successful = 0
            
            # Obtener datos de todas las ciudades
            for city in CITIES:
                data = fetch_weather_data(city["lat"], city["lon"])
                if data:
                    if insert_weather_reading(cursor, city["id"], data):
                        successful += 1
                        total_insertions += 1
                
                time.sleep(0.1)  # Pausa breve entre peticiones
            
            conn.commit()
            
            # Mostrar estadisticas
            elapsed = time.time() - start_time
            remaining = end_time - time.time()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Insertados: {successful}/{len(CITIES)} | Total: {total_insertions} | Tiempo restante: {int(remaining)}s")
            
            # Esperar hasta completar 1 minuto de ciclo
            iteration_time = time.time() - iteration_start
            if iteration_time < 60:
                time.sleep(60 - iteration_time)
        
        cursor.close()
        conn.close()
        
        print(f"\nStreaming completado!")
        print(f"Total de registros insertados: {total_insertions}")
        print(f"Promedio: {total_insertions / duration_minutes:.1f} registros por minuto")
        
    except KeyboardInterrupt:
        print("\nStreaming detenido por el usuario")
        conn.close()
    except Exception as e:
        print(f"Error en streaming: {e}")

if __name__ == "__main__":
    # Ejecutar streaming por 5 minutos (puedes cambiar la duracion)
    stream_weather_data(duration_minutes=5)
