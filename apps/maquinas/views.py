from django.shortcuts import render
from .models import Posiciones


def layout_laboratorio(request):
    posiciones = list(
        Posiciones.objects.filter(activo=True)
        .prefetch_related('maquinas')
        .order_by('fila', 'columna')
    )

    for posicion in posiciones:
        posicion.maquinas_asignadas = [
            maquina for maquina in posicion.maquinas.all() if maquina.activo
        ]

    total_columnas = max((posicion.columna for posicion in posiciones), default=1)

    return render(request, 'layout.html', {
        'posiciones': posiciones,
        'total_columnas': total_columnas,
    })
