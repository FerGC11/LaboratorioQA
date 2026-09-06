from django.db import transaction
from django.shortcuts import redirect, render

from .forms import (
    FiltroPruebaAplicativo,
    FiltroPruebaMaquina,
    FormularioPruebaAplicativo,
    FormularioPruebaMaquina,
)
from .models import Pruebas, PruebasAplicativos, PruebasMaquinas


def inicioPruebasMaquinas(request):
    formulario_registro = FormularioPruebaMaquina(request.POST or None)

    if request.method == "POST" and formulario_registro.is_valid():
        datos = formulario_registro.cleaned_data
        with transaction.atomic():
            prueba = Pruebas.objects.create(
                idEncargado=datos["idEncargado"],
                idTipoPrueba=datos["idTipoPrueba"],
                idResultado=datos["idResultado"],
                idEstado=datos["idEstado"],
                observaciones=datos["observaciones"],
                fechaPuestaPunto=datos["fechaPuestaPunto"],
                fechaInicio=datos["fechaInicio"],
                fechaFin=datos["fechaFin"],
            )
            PruebasMaquinas.objects.create(
                idPrueba=prueba,
                idProveedor=datos["idProveedor"],
                idJuego=datos["idJuego"],
                idMaquina=datos["idMaquina"],
                codigoPrueba=datos["codigoPrueba"],
            )
        return redirect("pruebas:PruebasMaquinas")

    pruebas_maquinas = PruebasMaquinas.objects.select_related(
        "idPrueba__idEncargado",
        "idPrueba__idTipoPrueba",
        "idPrueba__idResultado",
        "idPrueba__idEstado",
        "idProveedor",
        "idJuego",
        "idMaquina",
    ).order_by("-idPrueba__fechaInicio", "-idPruebaMaquina")

    formulario_filtro = FiltroPruebaMaquina(request.GET or None)
    if formulario_filtro.is_valid():
        filtros = formulario_filtro.cleaned_data
        if filtros["codigo"]:
            pruebas_maquinas = pruebas_maquinas.filter(codigoPrueba__icontains=filtros["codigo"])
        if filtros["fechaDesde"]:
            pruebas_maquinas = pruebas_maquinas.filter(idPrueba__fechaInicio__gte=filtros["fechaDesde"])
        if filtros["fechaHasta"]:
            pruebas_maquinas = pruebas_maquinas.filter(idPrueba__fechaInicio__lte=filtros["fechaHasta"])
        if filtros["encargado"]:
            pruebas_maquinas = pruebas_maquinas.filter(idPrueba__idEncargado=filtros["encargado"])
        if filtros["tipoPrueba"]:
            pruebas_maquinas = pruebas_maquinas.filter(idPrueba__idTipoPrueba=filtros["tipoPrueba"])
        if filtros["resultado"]:
            pruebas_maquinas = pruebas_maquinas.filter(idPrueba__idResultado=filtros["resultado"])
        if filtros["estado"]:
            pruebas_maquinas = pruebas_maquinas.filter(idPrueba__idEstado=filtros["estado"])
        if filtros["proveedor"]:
            pruebas_maquinas = pruebas_maquinas.filter(idProveedor=filtros["proveedor"])
        if filtros["juego"]:
            pruebas_maquinas = pruebas_maquinas.filter(idJuego=filtros["juego"])
        if filtros["maquina"]:
            pruebas_maquinas = pruebas_maquinas.filter(idMaquina=filtros["maquina"])

    return render(request, "maquinas/PruebasMaquinas.html", {
        "pruebas_maquinas": pruebas_maquinas,
        "formulario_registro": formulario_registro,
        "formulario_filtro": formulario_filtro,
        "mostrar_registro": request.method == "POST" and bool(formulario_registro.errors),
        "mostrar_filtros": bool(request.GET),
    })


def inicioPruebasAplicativos(request):
    formulario_registro = FormularioPruebaAplicativo(request.POST or None)

    if request.method == "POST" and formulario_registro.is_valid():
        datos = formulario_registro.cleaned_data
        with transaction.atomic():
            prueba = Pruebas.objects.create(
                idEncargado=datos["idEncargado"],
                idTipoPrueba=datos["idTipoPrueba"],
                idResultado=datos["idResultado"],
                idEstado=datos["idEstado"],
                observaciones=datos["observaciones"],
                fechaPuestaPunto=datos["fechaPuestaPunto"],
                fechaInicio=datos["fechaInicio"],
                fechaFin=datos["fechaFin"],
            )
            PruebasAplicativos.objects.create(
                idPrueba=prueba,
                idTipoAplicativo=datos["idTipoAplicativo"],
                idDesarrollador=datos["idDesarrollador"],
                codigoPrueba=datos["codigoPrueba"],
            )
        return redirect("pruebas:PruebasAplicativos")

    pruebas_aplicativos = PruebasAplicativos.objects.select_related(
        "idPrueba__idEncargado",
        "idPrueba__idTipoPrueba",
        "idPrueba__idResultado",
        "idPrueba__idEstado",
        "idTipoAplicativo",
        "idDesarrollador",
    ).order_by("-idPrueba__fechaInicio", "-idPruebaAplicativo")

    formulario_filtro = FiltroPruebaAplicativo(request.GET or None)
    if formulario_filtro.is_valid():
        filtros = formulario_filtro.cleaned_data
        if filtros["codigo"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(codigoPrueba__icontains=filtros["codigo"])
        if filtros["fechaDesde"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(idPrueba__fechaInicio__gte=filtros["fechaDesde"])
        if filtros["fechaHasta"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(idPrueba__fechaInicio__lte=filtros["fechaHasta"])
        if filtros["encargado"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(idPrueba__idEncargado=filtros["encargado"])
        if filtros["desarrollador"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(idDesarrollador=filtros["desarrollador"])
        if filtros["tipoPrueba"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(idPrueba__idTipoPrueba=filtros["tipoPrueba"])
        if filtros["tipoAplicativo"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(idTipoAplicativo=filtros["tipoAplicativo"])
        if filtros["resultado"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(idPrueba__idResultado=filtros["resultado"])
        if filtros["estado"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(idPrueba__idEstado=filtros["estado"])

    return render(request, "aplicativos/PruebasAplicativos.html", {
        "pruebas_aplicativos": pruebas_aplicativos,
        "formulario_registro": formulario_registro,
        "formulario_filtro": formulario_filtro,
        "mostrar_registro": request.method == "POST" and bool(formulario_registro.errors),
        "mostrar_filtros": bool(request.GET),
    })

def inicioEstadisticasPruebas(request):
    return render(request, "estadisticas/estadisticas.html")