# Sistema de Monitoreo Climatico en Tiempo Real - Costa Caribe Colombiana

## Descripcion del Proyecto
Sistema de analisis de datos climaticos en tiempo real para la Costa Caribe Colombiana, implementado con Azure PostgreSQL, Python y Dash.

## Componentes del Sistema

### 1. Base de Datos (Azure PostgreSQL)
- **weather_stations**: 8 estaciones meteorologicas
- **current_weather**: Lecturas climaticas en tiempo real
- **weather_forecasts**: Pronosticos del clima

### 2. Pipeline de Streaming
- Fuente de datos: Open-Meteo API
- Frecuencia: 8 ciudades cada minuto
- Total insertado: 40+ registros

### 3. Dashboard en Tiempo Real
- Mapa interactivo con temperaturas
- Graficos de tendencias
- Actualizacion automatica cada 30 segundos
- URL: http://127.0.0.1:8050/

### 4. Deteccion de Outliers
- Cambios bruscos de temperatura (>5C)
- Anomalias en presion (Z-score > 2)
- Vientos extremos (>15 m/s)
- Outliers detectados: 20

### 5. Modelo de Machine Learning
- Algoritmo: SGDRegressor (Online Learning)
- Variables: humedad, presion, viento, nubes
- MAE: 0.77C
- R2 Score: 0.680

## Ciudades Monitoreadas
1. Santa Marta, Magdalena
2. Barranquilla, Atlantico
3. Cartagena, Bolivar
4. Valledupar, Cesar
5. Riohacha, La Guajira
6. Monteria, Cordoba
7. Sincelejo, Sucre
8. San Andres, San Andres y Providencia

## Archivos del Proyecto
- config.py: Configuracion de BD
- create_tables.py: Creacion de tablas
- insert_stations.py: Insercion de estaciones
- data_streaming.py: Pipeline de streaming
- dashboard.py: Dashboard interactivo
- outlier_detection.py: Deteccion de anomalias
- ml_model.py: Modelo de prediccion

## Ejecucion

### Streaming de datos
```
python data_streaming.py
```

### Dashboard
```
python dashboard.py
```

### Deteccion de outliers
```
python outlier_detection.py
```

### Modelo ML
```
python ml_model.py
```

## Tecnologias Utilizadas
- Azure PostgreSQL
- Python 3.14
- Dash & Plotly
- Pandas & NumPy
- Scikit-learn
- Open-Meteo API

## Autores
Shirley y Johanna Blanquicet

## Fecha
Noviembre 2025
