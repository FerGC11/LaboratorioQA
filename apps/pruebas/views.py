from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.

def inicioPruebasMaquinas(request):
    if request.method == "POST":
        return redirect("pruebas:inicioPruebasMaquinas")

    return render(request, 'maquinas/PruebasMaquinas.html')

def inicioPruebasAplicativos(request):
    if request.method == "POST":
        return redirect("pruebas:inicioPruebasAplicativos")

    return render(request, 'aplicativos/PruebasAplicativos.html')

def inicioEstadisticasPruebas(request):
    return render (request, 'estadisticas/estadisticas.html')
