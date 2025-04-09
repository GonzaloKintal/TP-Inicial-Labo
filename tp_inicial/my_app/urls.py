from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("generar_dataset/", views.generate, name="generate_dataset"),
    path("train_model/", views.train_model, name="train_model"),
    path('upload_dataset/', views.upload_dataset, name='upload_dataset'),
    path('load_evaluation_data/', views.load_evaluation_data, name='load_evaluation_data'),
    path('evaluate_employees/', views.evaluate_employees, name='evaluate_employees'),
]

