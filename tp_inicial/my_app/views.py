from multiprocessing import context
from this import d
from django.shortcuts import render
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from generador_dataset.generator import generate_dataset
from generador_dataset.trainer import training_model
import random

def home(request):
    return render(request, "home.html")

def generate(request):
    df = generate_dataset()
    df =df.to_dict(orient='records')

    return render(request, "home.html", {"dataset": df})
