import psycopg2
from config import DB_CONFIG

def test_connection():
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        
        print("✅ Conexión exitosa a Azure PostgreSQL!")
        
        # Probar una consulta simple
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"📊 Versión de PostgreSQL: {db_version[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_connection()