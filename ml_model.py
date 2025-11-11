import psycopg2
import pandas as pd
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from config import DB_CONFIG
import pickle
import os

class OnlineWeatherPredictor:
    def __init__(self):
        self.model = SGDRegressor(max_iter=1000, tol=1e-3, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def train_incremental(self, X, y):
        """Entrenamiento incremental (online learning)"""
        if not self.is_fitted:
            # Primera vez: fit
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.is_fitted = True
        else:
            # Actualizaciones incrementales: partial_fit
            X_scaled = self.scaler.transform(X)
            self.model.partial_fit(X_scaled, y)
    
    def predict(self, X):
        """Prediccion de temperatura"""
        if not self.is_fitted:
            return None
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def save_model(self, filepath='weather_model.pkl'):
        """Guardar modelo"""
        with open(filepath, 'wb') as f:
            pickle.dump((self.model, self.scaler, self.is_fitted), f)
    
    def load_model(self, filepath='weather_model.pkl'):
        """Cargar modelo"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                self.model, self.scaler, self.is_fitted = pickle.load(f)
            return True
        return False

def get_training_data():
    """Obtener datos de entrenamiento"""
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT 
            cw.humidity,
            cw.pressure,
            cw.wind_speed,
            cw.cloud_cover,
            cw.temperature
        FROM current_weather cw
        WHERE cw.humidity IS NOT NULL 
          AND cw.pressure IS NOT NULL
          AND cw.wind_speed IS NOT NULL
          AND cw.temperature IS NOT NULL
        ORDER BY cw.timestamp;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def train_model():
    """Entrenar modelo con datos actuales"""
    print("\n=== ENTRENAMIENTO DE MODELO ML ===\n")
    
    # Cargar datos
    df = get_training_data()
    
    if len(df) < 10:
        print(f"No hay suficientes datos para entrenar (solo {len(df)} registros)")
        return
    
    print(f"Datos cargados: {len(df)} registros")
    
    # Preparar datos
    X = df[['humidity', 'pressure', 'wind_speed', 'cloud_cover']].values
    y = df['temperature'].values
    
    # Dividir en train/test (80/20)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Crear y entrenar modelo
    predictor = OnlineWeatherPredictor()
    
    # Entrenamiento por mini-batches (simulando streaming)
    batch_size = 5
    print(f"\nEntrenando con mini-batches de {batch_size} observaciones...")
    
    for i in range(0, len(X_train), batch_size):
        batch_X = X_train[i:i+batch_size]
        batch_y = y_train[i:i+batch_size]
        predictor.train_incremental(batch_X, batch_y)
        if (i // batch_size + 1) % 2 == 0:
            print(f"  Batch {i//batch_size + 1} procesado")
    
    print(f"\nEntrenamiento completado con {len(X_train)} observaciones")
    
    # Evaluar modelo
    if len(X_test) > 0:
        y_pred = predictor.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"\n=== METRICAS DEL MODELO ===")
        print(f"MAE (Error Absoluto Medio): {mae:.2f}C")
        print(f"R2 Score: {r2:.3f}")
        
        print(f"\n=== PREDICCIONES DE EJEMPLO ===")
        for i in range(min(5, len(y_test))):
            print(f"Real: {y_test[i]:.1f}C | Predicho: {y_pred[i]:.1f}C | Error: {abs(y_test[i] - y_pred[i]):.1f}C")
    
    # Guardar modelo
    predictor.save_model()
    print(f"\nModelo guardado en weather_model.pkl")
    
    # Ejemplo de prediccion nueva
    print(f"\n=== EJEMPLO DE PREDICCION ===")
    print("Condiciones: Humedad=80%, Presion=1010hPa, Viento=10m/s, Nubes=50%")
    new_data = np.array([[80, 1010, 10, 50]])
    prediction = predictor.predict(new_data)
    print(f"Temperatura predicha: {prediction[0]:.1f}C")

if __name__ == "__main__":
    train_model()
