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
    
    file_key = 'file' if 'file' in request.FILES else 'evaluate_file' if 'evaluate_file' in request.FILES else None
    
    if not file_key:
        return JsonResponse({'success': False, 'error': 'No se proporcionó ningún archivo'}, status=400)
    
    uploaded_file = request.FILES[file_key]
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension not in ['.xlsx', '.csv']:
        return JsonResponse({'success': False, 'error': 'Formato de archivo no soportado'}, status=400)
    
    try:
        # Usar nombres de archivo diferentes para cada sección
        if file_key == 'file':
            file_name = 'uploaded_dataset.csv'  # Para la sección superior
        else:
            file_name = 'evaluation_dataset.csv'  # Para la sección de evaluación
            
        file_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', file_name)
        
        if file_extension == '.xlsx':
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        df.to_csv(file_path, index=False)
        
        return JsonResponse({
            'success': True,
            'filename': uploaded_file.name,
            'message': 'Archivo cargado correctamente'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
def load_evaluation_data(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Determinar qué archivo cargar según el tipo de petición
        if 'evaluate_file' in request.FILES:
            # Es una carga desde la sección de evaluación
            file_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', 'evaluation_dataset.csv')
        else:
            # Es una carga desde la sección superior
            file_path = os.path.join(settings.BASE_DIR, 'my_app', 'dataset', 'uploaded_dataset.csv')
        
        df = pd.read_csv(file_path)
        
        # Columnas requeridas (diferentes para cada caso)
        if 'Riesgo' in df.columns:
            required_columns = ['ID', 'Edad', 'Horas_Trabajadas_Por_Semana', 
                              'Ausencias_Por_Enfermedad','Ausencias_Sin_Justificar', 'Nivel_de_Estres', 
                              'Tipo_de_Trabajo', 'Riesgo']
        else:
            required_columns = ['ID', 'Edad', 'Horas_Trabajadas_Por_Semana', 
                              'Ausencias_Por_Enfermedad', 'Ausencias_Sin_Justificar', 'Nivel_de_Estres', 
                              'Tipo_de_Trabajo']
        
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
                          'Ausencias_Por_Enfermedad', 'Ausencias_Sin_Justificar', 'Nivel_de_Estres', 
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