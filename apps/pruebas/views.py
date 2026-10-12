from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    FiltroPruebaAplicativo,
    FiltroPruebaMaquina,
    FormularioPruebaAplicativo,
    FormularioEditarPruebaAplicativo,
    FormularioPruebaMaquina,
)
from .models import Pruebas, PruebasAplicativos, PruebasMaquinas


def guardarPruebaMaquina(request):
    formulario_registro = FormularioPruebaMaquina(request.POST or None, request.FILES or None)

    if request.method == "POST" and formulario_registro.is_valid():
        datos = formulario_registro.cleaned_data
        with transaction.atomic():
            prueba = Pruebas.objects.create(
                idEncargado=datos["idEncargado"],
                idTipoPrueba_id=1,
                idResultado=None,
                idEstado=datos["idEstado"],
                fechaPuestaPunto=datos["fechaPuestaPunto"],
            )
            PruebasMaquinas.objects.create(
                idPrueba=prueba,
                idFamilia=datos["idFamilia"],
                idMaquina=datos["idMaquina"],
                codigoPrueba=datos["codigoPrueba"],
                idTipoJuego=datos["idTipoJuego"],
                versionSistemaCaja=datos["versionSistemaCaja"],
                versionNexus=datos["versionNexus"],
            )
        return redirect("pruebas:PruebasMaquinas")

    pruebas_maquinas = PruebasMaquinas.objects.select_related(
        "idPrueba__idEncargado",
        "idPrueba__idTipoPrueba",
        "idPrueba__idResultado",
        "idPrueba__idEstado",
        "idFamilia",
        "idMaquina",
        "idTipoJuego",
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
        if filtros["familia"]:
            pruebas_maquinas = pruebas_maquinas.filter(idFamilia=filtros["familia"])
        if filtros["tipoJuego"]:
            pruebas_maquinas = pruebas_maquinas.filter(idTipoJuego=filtros["tipoJuego"])
        if filtros["maquina"]:
            pruebas_maquinas = pruebas_maquinas.filter(idMaquina=filtros["maquina"])

    return render(request, "maquinas/PruebasMaquinas.html", {
        "pruebas_maquinas": pruebas_maquinas,
        "formulario_registro": formulario_registro,
        "formulario_filtro": formulario_filtro,
        "mostrar_registro": request.method == "POST" and bool(formulario_registro.errors),
        "mostrar_filtros": bool(request.GET),
    })


def guardarPruebaAplicativo(request):
    es_edicion = request.method == "POST" and request.POST.get("accion") == "editar"
    formulario_registro = FormularioPruebaAplicativo(None if es_edicion else (request.POST or None))
    registro_edicion = None
    formulario_edicion = None

    id_edicion = request.POST.get("idPruebaAplicativo") if es_edicion else request.GET.get("editar")
    if id_edicion:
        registro_edicion = get_object_or_404(
            PruebasAplicativos.objects.select_related("idPrueba"),
            pk=id_edicion,
        )
        formulario_edicion = FormularioEditarPruebaAplicativo(
            request.POST if es_edicion else None,
            prueba=registro_edicion.idPrueba,
            registro=registro_edicion,
        )

    if es_edicion and formulario_edicion and formulario_edicion.is_valid():
        prueba = registro_edicion.idPrueba
        prueba.idEstado = formulario_edicion.cleaned_data["idEstado"]
        prueba.idResultado = formulario_edicion.cleaned_data["idResultado"]
        prueba.fechaInicio = formulario_edicion.cleaned_data["fechaInicio"]
        prueba.fechaFin = formulario_edicion.cleaned_data["fechaFin"]
        prueba.fechaPuestaPunto = formulario_edicion.cleaned_data["fechaPuestaPunto"]
        prueba.documentoPruebas = formulario_edicion.cleaned_data["documentoPruebas"] or None
        prueba.observaciones = formulario_edicion.cleaned_data["observaciones"]
        registro_edicion.nombrePrueba = formulario_edicion.cleaned_data["nombrePrueba"] or None
        registro_edicion.versionAplicacion = formulario_edicion.cleaned_data["versionAplicacion"] or None
        registro_edicion.numAprobado = formulario_edicion.cleaned_data["numAprobado"]
        registro_edicion.numNoAprobado = formulario_edicion.cleaned_data["numNoAprobado"]
        registro_edicion.numAprobadoMenos = formulario_edicion.cleaned_data["numAprobadoMenos"]
        with transaction.atomic():
            prueba.save(update_fields=["idEstado", "idResultado", "fechaInicio", "fechaFin", "fechaPuestaPunto", "documentoPruebas", "observaciones"])
            registro_edicion.save(update_fields=["nombrePrueba", "versionAplicacion", "numAprobado", "numNoAprobado", "numAprobadoMenos"])
        return redirect("pruebas:PruebasAplicativos")

    if request.method == "POST" and not es_edicion and formulario_registro.is_valid():
        datos = formulario_registro.cleaned_data
        with transaction.atomic():
            prueba = Pruebas.objects.create(
                idEncargado=datos["idEncargado"],
                idTipoPrueba_id=2,
                idResultado=None,
                idEstado=datos["idEstado"],
                fechaPuestaPunto=datos["fechaPuestaPunto"],
            )
            PruebasAplicativos.objects.create(
                idPrueba=prueba,
                idTipoAplicativo=datos["idTipoAplicativo"],
                idProyecto=datos["idProyecto"],
                codigoPrueba=datos["codigoPrueba"],
                nombrePrueba=datos["nombrePrueba"] or None,
                versionAplicacion=datos["versionAplicacion"] or None,
                numAprobado=0,
                numNoAprobado=0,
                numAprobadoMenos=0,
            )
        return redirect("pruebas:PruebasAplicativos")

    pruebas_aplicativos = PruebasAplicativos.objects.select_related(
        "idPrueba__idEncargado",
        "idPrueba__idTipoPrueba",
        "idPrueba__idResultado",
        "idPrueba__idEstado",
        "idTipoAplicativo",
        "idProyecto",
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
        if filtros["proyecto"]:
            pruebas_aplicativos = pruebas_aplicativos.filter(idProyecto=filtros["proyecto"])
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
        "mostrar_filtros": bool(request.GET) and not registro_edicion,
        "registro_edicion": registro_edicion,
        "formulario_edicion": formulario_edicion,
    })

def inicioEstadisticasPruebas(request):
    return render(request, "estadisticas/estadisticas.html")


