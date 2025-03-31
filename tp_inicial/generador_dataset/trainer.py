import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from django.conf import settings
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os


def training_model(df):
    # Separamos datos en variables independientes (X) y objetivo (y)
    X = df[["Horas_Trabajadas_Por_Semana", "Ausencias_Por_Enfermedad", 
            "Nivel_de_Estres", "Edad", "Tipo_de_Trabajo"]]
    y = df["Riesgo"]

    # Convertimos "Tipo_de_Trabajo" usando LabelEncoder (mejor que get_dummies para predicción)
    encoder = LabelEncoder()
    X["Tipo_de_Trabajo"] = encoder.fit_transform(X["Tipo_de_Trabajo"])

    # Escalamos las características
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Dividimos en conjunto de entrenamiento y prueba (80%-20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # Entrenamos el modelo de regresión logística
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Hacemos las predicciones
    y_pred = model.predict(X_test)

    # Evaluamos el modelo
    precision = accuracy_score(y_test, y_pred)
    print(f"Precisión del modelo: {precision:.2f}")

    # Guardamos los componentes del modelo
    model_dir = os.path.join(settings.BASE_DIR, 'my_app', 'models')
    os.makedirs(model_dir, exist_ok=True)  # Crea la carpeta si no existe
    
    # Guardar el modelo
    model_path = os.path.join(model_dir, 'modelo_entrenado.pkl')
    joblib.dump(model, model_path)
    
    # Guardar el encoder
    encoder_path = os.path.join(model_dir, 'label_encoder.pkl')
    joblib.dump(encoder, encoder_path)
    
    # Guardar el scaler
    scaler_path = os.path.join(model_dir, 'standard_scaler.pkl')
    joblib.dump(scaler, scaler_path)
    
    print(f"Modelo guardado en: {model_path}")
    print(f"Encoder guardado en: {encoder_path}")
    print(f"Scaler guardado en: {scaler_path}")

    # Opcional: Guardar resultados de prueba
    resultados_path = os.path.join(model_dir, 'resultados_modelo.csv')
    pd.DataFrame({"Real": y_test, "Predicho": y_pred}).to_csv(resultados_path, index=False)
    print(f"Resultados guardados en: {resultados_path}")

    return precision * 100

def load_trained_model():
    """Carga el modelo entrenado y los transformadores desde archivos"""
    model_dir = os.path.join(settings.BASE_DIR, 'my_app', 'models')
    
    try:
        model_path = os.path.join(model_dir, 'modelo_entrenado.pkl')
        encoder_path = os.path.join(model_dir, 'label_encoder.pkl')
        scaler_path = os.path.join(model_dir, 'standard_scaler.pkl')
        
        if not os.path.exists(model_path):
            print("Modelo no encontrado en:", model_path)
            return None, None, None
            
        model = joblib.load(model_path)
        encoder = joblib.load(encoder_path)
        scaler = joblib.load(scaler_path)
        
        return model, encoder, scaler
    except Exception as e:
        print(f"Error al cargar el modelo: {str(e)}")
        return None, None, None
    
def predict_risk(data, model, encoder, scaler):
    """Realiza predicciones con el modelo entrenado"""
    # Hacer una copia para no modificar el dataframe original
    X = data[["Horas_Trabajadas_Por_Semana", "Ausencias_Por_Enfermedad", 
              "Nivel_de_Estres", "Edad", "Tipo_de_Trabajo"]].copy()
    
    # Codificar variable categórica
    X["Tipo_de_Trabajo"] = encoder.transform(X["Tipo_de_Trabajo"])
    
    # Escalar características
    X_scaled = scaler.transform(X)
    
    # Hacer predicciones
    predictions = model.predict(X_scaled)
    
    return predictions