import os
from django.shortcuts import render
from generador_dataset.generator import generate_dataset
from generador_dataset.trainer import training_model
from django.conf import settings
import pandas as pd
from django.http import JsonResponse
import json

def home(request):
    return render(request, "home.html")


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
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    # Verificar si el archivo viene como 'file' (primera sección) o 'evaluate_file' (última sección)
    file_key = 'file' if 'file' in request.FILES else 'evaluate_file' if 'evaluate_file' in request.FILES else None
    
    if not file_key:
        return JsonResponse({'success': False, 'error': 'No se proporcionó ningún archivo'}, status=400)
    
    uploaded_file = request.FILES[file_key]
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Validar extensión del archivo
    if file_extension not in ['.xlsx', '.csv']:
        return JsonResponse({'success': False, 'error': 'Formato de archivo no soportado'}, status=400)
    
    try:
        # Determinar el nombre del archivo según la sección
        file_name = 'uploaded_dataset.csv' if file_key == 'file' else 'temp_dataset.csv'
        file_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', file_name)
        
        if file_extension == '.xlsx':
            df = pd.read_excel(uploaded_file)
        else:  # .csv
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        # Guardar como CSV para consistencia
        df.to_csv(file_path, index=False)
        
        return JsonResponse({
            'success': True,
            'filename': uploaded_file.name,
            'message': 'Archivo cargado correctamente'
        })
        
    except pd.errors.EmptyDataError:
        return JsonResponse({'success': False, 'error': 'El archivo está vacío'}, status=400)
    except pd.errors.ParserError:
        return JsonResponse({'success': False, 'error': 'Error al parsear el archivo'}, status=400)
    except UnicodeDecodeError:
        return JsonResponse({'success': False, 'error': 'Problema de codificación del archivo. Intente guardarlo como UTF-8'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def load_evaluation_data(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Verificar si se envió un archivo (para la primera sección)
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_extension == '.xlsx':
                df = pd.read_excel(uploaded_file)
            else:  # .csv
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            
            # Guardar temporalmente
            temp_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', 'temp_dataset.csv')
            df.to_csv(temp_path, index=False)
        else:
            # Usar el archivo ya cargado (para la primera sección)
            temp_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', 'uploaded_dataset.csv')
        
        # Leer el archivo
        df = pd.read_csv(temp_path)
        
        # Columnas requeridas (diferentes para cada caso)
        if 'Riesgo' in df.columns:
            # Primera sección (dataset completo)
            required_columns = ['ID', 'Edad', 'Horas_Trabajadas_Por_Semana', 
                              'Ausencias_Por_Enfermedad', 'Nivel_de_Estres', 
                              'Tipo_de_Trabajo', 'Riesgo']
        else:
            # Última sección (datos para evaluación)
            required_columns = ['ID', 'Edad', 'Horas_Trabajadas_Por_Semana', 
                              'Ausencias_Por_Enfermedad', 'Nivel_de_Estres', 
                              'Tipo_de_Trabajo']
        
        # Verificar columnas requeridas
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({
                'success': False,
                'error': f'Faltan columnas requeridas: {", ".join(missing_columns)}'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'dataset': df.to_dict('records'),
            'message': 'Dataset cargado correctamente'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def evaluate_employees(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener datos del cuerpo JSON
        data = json.loads(request.body)
        dataset = data.get('dataset', [])
        
        if not dataset:
            return JsonResponse({'success': False, 'error': 'No se proporcionaron datos para evaluar'}, status=400)
        
        # Convertir a DataFrame
        df = pd.DataFrame(dataset)
        
        # Validar que el DataFrame tenga las columnas requeridas
        required_columns = ['ID', 'Edad', 'Horas_Trabajadas_Por_Semana', 
                          'Ausencias_Por_Enfermedad', 'Nivel_de_Estres', 
                          'Tipo_de_Trabajo']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JsonResponse({
                'success': False,
                'error': f'Faltan columnas requeridas: {", ".join(missing_columns)}'
            }, status=400)
        
        # Resto del código para cargar el modelo y predecir...
        from generador_dataset.trainer import load_trained_model, predict_risk
        model, encoder, scaler = load_trained_model()
        
        if model is None:
            return JsonResponse({
                'success': False,
                'error': 'El modelo no ha sido entrenado aún. Entrena el modelo primero.'
            }, status=400)
        
        predictions = predict_risk(df, model, encoder, scaler)
        
        results_df = df.copy()
        results_df['Riesgo_Predicho'] = predictions
        
        return JsonResponse({
            'success': True,
            'results': results_df.to_dict('records'),
            'message': 'Evaluación completada correctamente'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)