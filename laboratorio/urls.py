from django.contrib import admin
from django.urls import include, path
from laboratorio.views import *
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include("apps.usuarios.urls")),
    path('pruebas/', include("apps.pruebas.urls")),
    path('maquinas/', include("apps.maquinas.urls")),
    path('', login, name='login'),
    path('inicio/', inicio, name='inicio' ),
   #path('', TemplateView.as_view(template_name="inicio.html"), name="inicio"),
]
