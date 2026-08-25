from django.shortcuts import render
from .models import PosicionesLaboratorio


def layout_laboratorio(request):
    posiciones = list(
        PosicionesLaboratorio.objects.filter(activa=True)
        .prefetch_related('maquinas_set')
        .order_by('fila', 'columna')
    )

    for posicion in posiciones:
        posicion.maquinas_asignadas = [
            maquina for maquina in posicion.maquinas_set.all() if maquina.activa
        ]

    total_columnas = max((posicion.columna for posicion in posiciones), default=1)

    return render(request, 'layout.html', {
        'posiciones': posiciones,
        'total_columnas': total_columnas,
    })