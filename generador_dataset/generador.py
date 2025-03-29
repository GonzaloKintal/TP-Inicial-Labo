import os
import numpy as np
import pandas as pd

def asignar_riesgo(horas, ausencias):
    if horas > 55 or ausencias > 5:
        return "Alto Riesgo"
    return "Bajo Riesgo"

def generar_dataset(seed=50, nro_empleados=200):
    np.random.seed(seed)

    horas_trabajadas = np.random.randint(20, 71, nro_empleados)
    ausencias = np.random.randint(0, 16, nro_empleados)
    edad = np.random.randint(18, 66, nro_empleados)

    riesgo = [asignar_riesgo(horas, falta) for horas, falta in zip(horas_trabajadas, ausencias)]

    df = pd.DataFrame({
        'Horas_Trabajadas': horas_trabajadas,
        'Ausencias': ausencias,
        'Edad': edad,
        'Riesgo': riesgo
    })

    df = df.sort_values(by=['Riesgo'])

    id_archivo = len(os.listdir("dataset")) + 1 
    nombre_archivo = f"dataset_empleados_{id_archivo}.csv"

    ruta_archivo = os.path.join("dataset", nombre_archivo)
 
    df.to_csv(ruta_archivo, index=False)

    return df