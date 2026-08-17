from django.urls import path
from . import views

app_name = 'pruebas'  # importante para usar el template tag automático

urlpatterns = [
    path('pruebasMaquinas/', views.inicioPruebasMaquinas, name='PruebasMaquinas'),
    path('pruebasAplicativos/', views.inicioPruebasAplicativos, name='PruebasAplicativos')
]
