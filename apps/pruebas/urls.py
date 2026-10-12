from django.urls import path
from . import views

app_name = 'pruebas'  # importante para usar el template tag automático

urlpatterns = [
    path('pruebasMaquinas/', views.guardarPruebaMaquina, name='PruebasMaquinas'),
    path('pruebasAplicativos/', views.guardarPruebaAplicativo, name='PruebasAplicativos'),
    path('estadisticasPruebas/', views.inicioEstadisticasPruebas, name='EstadisticasPruebas')
]
