from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("generar_dataset", views.generate, name="generate_dataset"),
    path("entrenar_modelo", views.train_model, name="train_model"),
    # path("predecir_riesgo", views.predict_risk, name="predict_risk"),
    path('upload_dataset/', views.upload_dataset, name='upload_dataset'),
]

