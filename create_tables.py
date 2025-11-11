import psycopg2
from config import DB_CONFIG

def create_tables():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Creando tablas en Azure PostgreSQL...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_stations (
                station_id SERIAL PRIMARY KEY,
                city_name VARCHAR(100) NOT NULL,
                department VARCHAR(100),
                latitude DECIMAL(10, 6),
                longitude DECIMAL(10, 6),
                elevation INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Tabla weather_stations creada")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_weather (
                reading_id SERIAL PRIMARY KEY,
                station_id INTEGER REFERENCES weather_stations(station_id),
                temperature DECIMAL(5, 2),
                humidity INTEGER,
                pressure DECIMAL(6, 2),
                wind_speed DECIMAL(5, 2),
                wind_direction INTEGER,
                precipitation DECIMAL(5, 2),
                cloud_cover INTEGER,
                weather_code INTEGER,
                timestamp TIMESTAMP NOT NULL
            );
            
            CREATE INDEX IF NOT EXISTS idx_timestamp ON current_weather(timestamp);
            CREATE INDEX IF NOT EXISTS idx_station_timestamp ON current_weather(station_id, timestamp);
        """)
        print("Tabla current_weather creada con indices")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_forecasts (
                forecast_id SERIAL PRIMARY KEY,
                station_id INTEGER REFERENCES weather_stations(station_id),
                forecast_time TIMESTAMP NOT NULL,
                temperature DECIMAL(5, 2),
                precipitation_prob INTEGER,
                conditions VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Tabla weather_forecasts creada")
        
        conn.commit()
        print("\nTodas las tablas creadas exitosamente!")
        
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\nTablas en la base de datos:")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_tables()