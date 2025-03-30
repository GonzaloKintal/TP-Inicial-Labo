import os
import numpy as np
import pandas as pd
from django.conf import settings
import random

def assign_risk(horas, ausencias, nivel_estres):
    ausencias_rel = (ausencias / horas) * 100 
    estres_rel = (nivel_estres / 10) 

    score = (ausencias_rel * 0.7) + (estres_rel * 0.2) + (horas * 0.1)
    
    return "Alto Riesgo" if score > 10 else "Bajo Riesgo"

def generate_dataset(seed=50, nro_empleados=500):
    np.random.seed(random.randint(1, 100))

    horas_trabajadas = np.random.randint(20, 71, nro_empleados)
    ausencias = np.random.randint(0, 6, nro_empleados)
    nivel_estres = np.random.randint(0, 11, nro_empleados)
    edad = np.random.randint(18, 66, nro_empleados)
    tipos_trabajo = np.random.choice(['Oficina', 'Físico'], nro_empleados)

    riesgo = [assign_risk(horas, falta,estres) for horas, falta , estres in zip(horas_trabajadas, ausencias, nivel_estres)]


    df = pd.DataFrame({
        'ID': range(1, nro_empleados + 1),
        'Horas_Trabajadas_Por_Semana': horas_trabajadas,
        'Ausencias_Por_Enfermedad': ausencias,
        'Nivel_de_Estres': nivel_estres,   
        'Edad': edad,
        'Tipo_de_Trabajo': tipos_trabajo,
        'Riesgo': riesgo
    })

    df["Riesgo"] = df["Riesgo"].map({"Alto Riesgo": 1, "Bajo Riesgo": 0})

    file_name = "dataset_empleados.csv"

    file_path = os.path.join(settings.FILE_PATH, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)

    return df