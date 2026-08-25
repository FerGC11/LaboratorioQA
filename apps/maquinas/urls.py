from django.urls import path
from . import views

app_name = 'maquinas'  # importante para usar el template tag automático

urlpatterns = [
    path('layoutLaboratorio/', views.layout_laboratorio, name='layout'),
]