import os
import numpy as np
import pandas as pd
from django.conf import settings

def assign_risk(horas, ausencias):
    if horas > 55 or ausencias > 5:
        return "Alto Riesgo"
    return "Bajo Riesgo"

def generate_dataset(seed=50, nro_empleados=200):
    np.random.seed(seed)

    horas_trabajadas = np.random.randint(20, 71, nro_empleados)
    ausencias = np.random.randint(0, 16, nro_empleados)
    edad = np.random.randint(18, 66, nro_empleados)
    tipos_trabajo = np.random.choice(['Oficina', 'Físico'], nro_empleados)

    riesgo = [assign_risk(horas, falta) for horas, falta in zip(horas_trabajadas, ausencias)]


    df = pd.DataFrame({
        'Horas_Trabajadas_Por_Semana': horas_trabajadas,
        'Ausencias_Por_Enfermedad': ausencias,
        'Edad': edad,
        'Tipo_de_Trabajo': tipos_trabajo,
        'Riesgo': riesgo
    })

    df["Riesgo"] = df["Riesgo"].map({"Alto Riesgo": 1, "Bajo Riesgo": 0})
    
    df = df.sort_values(by=['Riesgo'])

    file_name = "dataset_empleados.csv"

    file_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)

    return df