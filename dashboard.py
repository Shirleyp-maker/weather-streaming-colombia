import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import pandas as pd
from datetime import datetime
from config import DB_CONFIG

# Crear app
app = dash.Dash(__name__)
app.title = "Dashboard Climatico Costa Caribe"

# Funcion para conectar a la base de datos
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_current_weather():
    conn = get_connection()
    query = """
        SELECT 
            ws.city_name,
            ws.department,
            ws.latitude,
            ws.longitude,
            cw.temperature,
            cw.humidity,
            cw.pressure,
            cw.wind_speed,
            cw.precipitation,
            cw.cloud_cover,
            cw.timestamp
        FROM current_weather cw
        JOIN weather_stations ws ON cw.station_id = ws.station_id
        WHERE cw.timestamp >= NOW() - INTERVAL '1 hour'
        ORDER BY cw.timestamp DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_latest_readings():
    conn = get_connection()
    query = """
        SELECT DISTINCT ON (ws.city_name)
            ws.city_name,
            ws.latitude,
            ws.longitude,
            cw.temperature,
            cw.humidity,
            cw.wind_speed
        FROM current_weather cw
        JOIN weather_stations ws ON cw.station_id = ws.station_id
        ORDER BY ws.city_name, cw.timestamp DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_statistics():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM current_weather;")
    total_readings = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT station_id) FROM current_weather;")
    active_stations = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(timestamp) FROM current_weather;")
    last_update = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    return total_readings, active_stations, last_update

# Layout
app.layout = html.Div([
    html.H1("Dashboard en Tiempo Real - Costa Caribe Colombiana", 
            style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div(id='stats-container', style={'margin': '20px'}),
    
    html.Hr(),
    
    html.Div([
        html.Div([
            dcc.Graph(id='map-temperature')
        ], style={'width': '65%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("Temperaturas Actuales", style={'textAlign': 'center'}),
            html.Div(id='current-temps')
        ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ]),
    
    html.Hr(),
    
    html.Div([
        html.Div([
            dcc.Graph(id='temp-trend')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='wind-chart')
        ], style={'width': '48%', 'display': 'inline-block'})
    ]),
    
    html.Hr(),
    
    html.H3("Datos Recientes", style={'textAlign': 'center'}),
    html.Div(id='data-table', style={'margin': '20px'}),
    
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # 30 segundos
        n_intervals=0
    )
])

@app.callback(
    [Output('stats-container', 'children'),
     Output('map-temperature', 'figure'),
     Output('current-temps', 'children'),
     Output('temp-trend', 'figure'),
     Output('wind-chart', 'figure'),
     Output('data-table', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    # Obtener datos
    df_weather = get_current_weather()
    df_latest = get_latest_readings()
    total_readings, active_stations, last_update = get_statistics()
    
    # Estadisticas
    stats = html.Div([
        html.Div([
            html.H3(f"{total_readings:,}", style={'margin': '0'}),
            html.P("Total de Lecturas", style={'margin': '0'})
        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(f"{active_stations}", style={'margin': '0'}),
            html.P("Estaciones Activas", style={'margin': '0'})
        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center'}),
        
        html.Div([
            html.H3(last_update.strftime("%H:%M:%S") if last_update else "N/A", style={'margin': '0'}),
            html.P("Ultima Actualizacion", style={'margin': '0'})
        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center'})
    ])
    
    # Mapa
    fig_map = px.scatter_mapbox(
        df_latest,
        lat="latitude",
        lon="longitude",
        color="temperature",
        size="temperature",
        hover_name="city_name",
        hover_data={"temperature": ":.1f", "humidity": True, "wind_speed": ":.1f"},
        color_continuous_scale="RdYlBu_r",
        zoom=5.5,
        height=500
    )
    fig_map.update_layout(mapbox_style="open-street-map", title="Mapa de Temperaturas")
    
    # Temperaturas actuales
    temps = []
    for _, row in df_latest.iterrows():
        temps.append(html.Div([
            html.H4(row['city_name'], style={'margin': '5px'}),
            html.P(f"{row['temperature']:.1f}C - {row['humidity']:.0f}% humedad", 
                   style={'margin': '5px', 'fontSize': '14px'})
        ], style={'padding': '10px', 'border': '1px solid #ddd', 'margin': '5px', 'borderRadius': '5px'}))
    
    # Tendencia de temperatura
    fig_temp = px.line(
        df_weather,
        x="timestamp",
        y="temperature",
        color="city_name",
        title="Tendencia de Temperatura (ultima hora)"
    )
    fig_temp.update_layout(height=400)
    
    # Velocidad del viento
    fig_wind = px.bar(
        df_latest,
        x="city_name",
        y="wind_speed",
        color="wind_speed",
        color_continuous_scale="Blues",
        title="Velocidad del Viento por Ciudad"
    )
    fig_wind.update_layout(height=400)
    
    # Tabla
    table = dash_table.DataTable(
        data=df_weather.head(20).to_dict('records'),
        columns=[{"name": i, "id": i} for i in df_weather.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'}
    )
    
    return stats, fig_map, temps, fig_temp, fig_wind, table

if __name__ == '__main__':
    print("\nDashboard corriendo en: http://127.0.0.1:8050/")
    print("Presiona Ctrl+C para detener\n")
    app.run(debug=False, port=8050)
