import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def training_model(df) :
    # Separamos datos en variables independientes (X) y objetivo (y)
    X = df[["Horas_Trabajadas_Por_Semana", "Ausencias_Por_Enfermedad", "Edad", "Tipo_de_Trabajo"]]
    y = df["Riesgo"]

    # Convertimos "Tipo_de_Trabajo" en variables dummy (0 o 1)
    X = pd.get_dummies(X, drop_first=True)

    # Dividi,ps en conjunto de entrenamiento y prueba (80%-20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenamos al modelo de regresión logística
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Hacemos las predicciones
    y_pred = model.predict(X_test)

    # Evaluamos el modelo
    precision = accuracy_score(y_test, y_pred)
    print(f"Precisión del modelo: {precision:.2f}")


