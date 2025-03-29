from multiprocessing import context
from django.shortcuts import render
from generador_dataset.generator import generate_dataset

def home(request):
    return render(request, "home.html")

def generate(request):
    df = generate_dataset()
    df = df.to_dict(orient='records')

    return render(request, "home.html", {"dataset": df})
