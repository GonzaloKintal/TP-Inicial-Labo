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


def upload_dataset(request):
    if 'file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No se proporcionó ningún archivo'}, status=400)
    
    uploaded_file = request.FILES['file']
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Validar extensión del archivo
    if file_extension not in ['.xlsx', '.csv']:
        return JsonResponse({'success': False, 'error': 'Formato de archivo no soportado'}, status=400)
    
    try:
        # Opción 1: Trabajar con el archivo en memoria (recomendado)
        if file_extension == '.xlsx':
            df = pd.read_excel(uploaded_file)
        else:  # .csv
            # Especificar encoding y manejar posibles errores
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        # Validar que el DataFrame tenga las columnas requeridas
        required_columns = ['ID', 'Edad', 'Horas_Trabajadas_Por_Semana', 
                          'Ausencias_Por_Enfermedad', 'Nivel_de_Estres', 
                          'Tipo_de_Trabajo','Riesgo']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({
                'success': False,
                'error': f'Faltan columnas requeridas: {", ".join(missing_columns)}'
            }, status=400)
        
        # Convertir a lista de diccionarios para el frontend
        dataset = df.to_dict('records')
        
        return JsonResponse({
            'success': True,
            'dataset': dataset,
            'message': 'Archivo procesado correctamente'
        })
        
    except pd.errors.EmptyDataError:
        return JsonResponse({'success': False, 'error': 'El archivo está vacío'}, status=400)
    except pd.errors.ParserError:
        return JsonResponse({'success': False, 'error': 'Error al parsear el archivo'}, status=400)
    except UnicodeDecodeError:
        return JsonResponse({'success': False, 'error': 'Problema de codificación del archivo. Intente guardarlo como UTF-8'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)