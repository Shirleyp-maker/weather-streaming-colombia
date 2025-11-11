import psycopg2
from config import DB_CONFIG

def insert_stations():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Insertando estaciones meteorologicas de la Costa Caribe Colombiana...")
        
        stations = [
            ('Santa Marta', 'Magdalena', 11.2408, -74.2120, 2),
            ('Barranquilla', 'Atlantico', 10.9685, -74.7813, 18),
            ('Cartagena', 'Bolivar', 10.3910, -75.4794, 2),
            ('Valledupar', 'Cesar', 10.4631, -73.2532, 169),
            ('Riohacha', 'La Guajira', 11.5444, -72.9072, 5),
            ('Monteria', 'Cordoba', 8.7479, -75.8814, 18),
            ('Sincelejo', 'Sucre', 9.3047, -75.3978, 213),
            ('San Andres', 'San Andres y Providencia', 12.5847, -81.7006, 3)
        ]
        
        for city, dept, lat, lon, elev in stations:
            cursor.execute("""
                INSERT INTO weather_stations (city_name, department, latitude, longitude, elevation)
                VALUES (%s, %s, %s, %s, %s);
            """, (city, dept, lat, lon, elev))
            print(f"   - {city}, {dept}")
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM weather_stations;")
        count = cursor.fetchone()[0]
        print(f"\nTotal de estaciones insertadas: {count}")
        
        cursor.execute("SELECT station_id, city_name, department FROM weather_stations ORDER BY station_id;")
        stations = cursor.fetchall()
        print("\nEstaciones en la base de datos:")
        for station in stations:
            print(f"   ID {station[0]}: {station[1]}, {station[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    insert_stations()
