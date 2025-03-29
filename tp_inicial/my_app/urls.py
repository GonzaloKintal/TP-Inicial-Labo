from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("generar_dataset", views.generate, name="generate_dataset"),
]
