from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.http import  HttpResponse

def login(request):
    return render (request, "login.html")

def inicio(request):
    return render (request, "inicio.html")