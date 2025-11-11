# Para desplegar en Streamlit Cloud:

1. Ve a https://share.streamlit.io/
2. Conecta tu cuenta de GitHub
3. Selecciona el repositorio: weather-streaming-colombia
4. Main file path: streamlit_app.py
5. Configura los secrets en Settings con tus credenciales de Azure

## Secrets necesarios (formato TOML):

[database]
DB_HOST = "clasebdun.postgres.database.azure.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "shirleyp"
DB_PASSWORD = "bigdata1$"
DB_SSLMODE = "require"
