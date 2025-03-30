import os
from multiprocessing import context
from django.shortcuts import render
from generador_dataset.generator import generate_dataset
from generador_dataset.trainer import training_model
from django.conf import settings
import pandas as pd
from django.http import JsonResponse

def home(request):
    return render(request, "home.html")

# def generate(request):
#     df = generate_dataset()
#     df = df.to_dict(orient='records')

#     return render(request, "home.html", {"dataset": df})

def generate(request):
    df = generate_dataset()
    df_records = df.to_dict(orient='records')
    
    # Guardar el dataset en un archivo CSV
    file_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', 'dataset_empleados.csv')
    df.to_csv(file_path, index=False)
    
    return JsonResponse({
        'success': True,
        'dataset': df_records,
        'message': 'Dataset generado exitosamente'
    })


def train_model(request):
    file_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', 'dataset_empleados.csv')
    df = pd.read_csv(file_path)
    precision = training_model(df)

    return JsonResponse({"precision": precision})