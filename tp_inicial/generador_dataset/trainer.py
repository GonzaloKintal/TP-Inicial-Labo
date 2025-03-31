import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from django.conf import settings
from sklearn.preprocessing import StandardScaler
import os
import joblib  # 


def training_model(df):

    df_prueba=df

    # Separamos datos en variables independientes (X) y objetivo (y)
    X = df[["Horas_Trabajadas_Por_Semana", "Ausencias_Por_Enfermedad","Nivel_de_Estres", "Edad", "Tipo_de_Trabajo"]]
    y = df["Riesgo"]

    # Convertimos "Tipo_de_Trabajo" en variables dummy (0 o 1)
    X = pd.get_dummies(X, drop_first=True)

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Dividimos en conjunto de entrenamiento y prueba (80%-20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenamos el modelo de regresión logística
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Hacemos las predicciones
    y_pred = model.predict(X_test)

    # Evaluamos el modelo
    precision = accuracy_score(y_test, y_pred)
    print(f"Precisión del modelo: {precision:.2f}")

    # Guardamos los resultados en un CSV

    resultados = pd.DataFrame({"Real": y_test, "Predicho": y_pred})
    file_path = os.path.join(settings.FILE_PATH, "resultados_modelo.csv")
    resultados.to_csv(file_path, index=False)
    print("Resultados guardados en 'resultados_modelo.csv'.")

    model_path = os.path.join(settings.FILE_PATH, "modelo_riesgo.joblib")
    scaler_path = os.path.join(settings.FILE_PATH, "scaler_riesgo.joblib")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    predecir_riesgo()

    
    return precision * 100 # Devolvemos el modelo entrenado



def predecir_riesgo():

    file_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', 'data_prueba.csv')
    nuevos_datos = pd.read_csv(file_path)

    nuevos_datos= nuevos_datos[["Horas_Trabajadas_Por_Semana", "Ausencias_Por_Enfermedad","Nivel_de_Estres", "Edad", "Tipo_de_Trabajo"]]
   
    model_path = os.path.join(settings.FILE_PATH, "modelo_riesgo.joblib")
    scaler_path = os.path.join(settings.FILE_PATH, "scaler_riesgo.joblib")
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    nuevos_datos = pd.get_dummies(nuevos_datos, drop_first=True)
    nuevos_datos_scaled = scaler.transform(nuevos_datos)

    prediccion = model.predict(nuevos_datos_scaled)

    nuevos_datos["Riesgo"] = prediccion

    file_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', 'prediccion.csv')
    nuevos_datos.to_csv(file_path, index=False)  


    return prediccion
