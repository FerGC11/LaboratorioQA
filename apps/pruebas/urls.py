from django.urls import path
from . import views
from .catalogos import detalles_generales

app_name = 'pruebas'  # importante para usar el template tag automático

urlpatterns = [
    path("detalles-generales/", detalles_generales, name="DetallesGenerales"),
    path("detalles-generales/<slug:catalogo>/", detalles_generales, name="Catalogo"),
    path('pruebasMaquinas/', views.guardarPruebaMaquina, name='PruebasMaquinas'),
    path('pruebasAplicativos/', views.guardarPruebaAplicativo, name='PruebasAplicativos'),
    path('estadisticasPruebas/', views.inicioEstadisticasPruebas, name='EstadisticasPruebas')
]
