from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from apps.usuarios.models import Usuario

from .forms import (
    FiltroEstadisticas,
    FiltroEstadisticasAplicativos,
    FiltroEstadisticasMaquinas,
    FiltroPruebaAplicativo,
    FiltroPruebaMaquina,
    FormularioPruebaAplicativo,
    FormularioEditarPruebaAplicativo,
    FormularioEditarPruebaMaquina,
    FormularioPruebaMaquina,
)
from .models import Estados, Pruebas, PruebasAplicativos, PruebasMaquinas, TiposPruebas


def guardarPruebaMaquina(request):
    es_edicion = request.method == "POST" and request.POST.get("accion") == "editar"
    formulario_registro = FormularioPruebaMaquina(None if es_edicion else (request.POST or None))
    registro_edicion = None
    formulario_edicion = None

    id_edicion = request.POST.get("idPruebaMaquina") if es_edicion else request.GET.get("editar")
    if id_edicion:
        registro_edicion = get_object_or_404(
            PruebasMaquinas.objects.select_related("idPrueba"),
            pk=id_edicion,
        )
        formulario_edicion = FormularioEditarPruebaMaquina(
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
        prueba.numAprobado = formulario_edicion.cleaned_data["numAprobado"]
        prueba.numNoAprobado = formulario_edicion.cleaned_data["numNoAprobado"]
        prueba.numAprobadoMenos = formulario_edicion.cleaned_data["numAprobadoMenos"]
        prueba.numCasosPrueba = formulario_edicion.cleaned_data["numCasosPrueba"]
        casos_ejecutados = prueba.numAprobado + prueba.numNoAprobado + prueba.numAprobadoMenos
        prueba.porcentajeAvance = (
            (Decimal(casos_ejecutados) * Decimal("100")) / Decimal(prueba.numCasosPrueba)
            if prueba.numCasosPrueba
            else Decimal("0")
        ).quantize(Decimal("0.01"))
        registro_edicion.nombreJuego = formulario_edicion.cleaned_data["nombreJuego"] or None
        with transaction.atomic():
            registro_edicion.save(update_fields=["nombreJuego"])
            prueba.save(update_fields=["idEstado", "idResultado", "fechaInicio", "fechaFin", "fechaPuestaPunto", "documentoPruebas", "observaciones", "numAprobado", "numNoAprobado", "numAprobadoMenos", "numCasosPrueba", "porcentajeAvance"])
        return redirect("pruebas:PruebasMaquinas")

    if request.method == "POST" and not es_edicion and formulario_registro.is_valid():
        datos = formulario_registro.cleaned_data
        with transaction.atomic():
            prueba = Pruebas.objects.create(
                idEncargado=datos["idEncargado"],
                idTipoPrueba_id=1,
                idResultado=datos["idResultado"],
                idEstado=datos["idEstado"],
                fechaPuestaPunto=datos["fechaPuestaPunto"],
                fechaInicio=datos["fechaInicio"],
                fechaFin=datos["fechaFin"],
                documentoPruebas=datos["documentoPruebas"] or None,
                observaciones=datos["observaciones"],
                numAprobado=datos["numAprobado"],
                numNoAprobado=datos["numNoAprobado"],
                numAprobadoMenos=datos["numAprobadoMenos"],
                numCasosPrueba=datos["numCasosPrueba"],
                porcentajeAvance=(
                    Decimal(datos["numAprobado"] + datos["numNoAprobado"] + datos["numAprobadoMenos"])
                    * Decimal("100") / Decimal(datos["numCasosPrueba"])
                    if datos["numCasosPrueba"] else Decimal("0")
                ).quantize(Decimal("0.01")),
            )
            PruebasMaquinas.objects.create(
                idPrueba=prueba,
                idFamilia=datos["idFamilia"],
                idMaquina=datos["idMaquina"],
                codigoPrueba=datos["codigoPrueba"],
                idTipoJuego=datos["idTipoJuego"],
                idProtocolo=datos["idProtocolo"],
                versionSistemaCaja=datos["versionSistemaCaja"],
                versionNexus=datos["versionNexus"],
                nombreJuego=datos["nombreJuego"] or None,
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
        "idProtocolo",
    ).order_by("-idPrueba__fechaInicio", "-idPruebaMaquina")

    formulario_filtro = FiltroPruebaMaquina(request.GET or None)
    if formulario_filtro.is_valid():
        filtros = formulario_filtro.cleaned_data
        if filtros["nombreJuego"]:
            pruebas_maquinas = pruebas_maquinas.filter(nombreJuego__icontains=filtros["nombreJuego"])
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
        "mostrar_filtros": bool(request.GET) and not registro_edicion,
        "registro_edicion": registro_edicion,
        "formulario_edicion": formulario_edicion,
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
        prueba.numAprobado = formulario_edicion.cleaned_data["numAprobado"]
        prueba.numNoAprobado = formulario_edicion.cleaned_data["numNoAprobado"]
        prueba.numAprobadoMenos = formulario_edicion.cleaned_data["numAprobadoMenos"]
        prueba.numCasosPrueba = formulario_edicion.cleaned_data["numCasosPrueba"]
        casos_ejecutados = prueba.numAprobado + prueba.numNoAprobado + prueba.numAprobadoMenos
        prueba.porcentajeAvance = (
            (Decimal(casos_ejecutados) * Decimal("100")) / Decimal(prueba.numCasosPrueba)
            if prueba.numCasosPrueba
            else Decimal("0")
        ).quantize(Decimal("0.01"))
        with transaction.atomic():
            prueba.save(update_fields=["idEstado", "idResultado", "fechaInicio", "fechaFin", "fechaPuestaPunto", "documentoPruebas", "observaciones", "numAprobado", "numNoAprobado", "numAprobadoMenos", "numCasosPrueba", "porcentajeAvance"])
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
    pruebas = Pruebas.objects.select_related(
        "idEncargado", "idTipoPrueba", "idEstado", "idResultado"
    )

    categorias = {"generales": ("Generales", FiltroEstadisticas),
                  "aplicativos": ("Aplicativos", FiltroEstadisticasAplicativos),
                  "maquinas": ("Máquinas", FiltroEstadisticasMaquinas)}
    categoria = request.GET.get("categoria", "generales")
    if categoria not in categorias:
        categoria = "generales"
    categoria_nombre, clase_filtro = categorias[categoria]
    parametros = request.GET.copy()
    hoy = timezone.localdate()
    parametros.setdefault("fecha_desde", (hoy - timedelta(days=30)).isoformat())
    parametros.setdefault("fecha_hasta", hoy.isoformat())
    formulario_filtro = clase_filtro(parametros)

    if categoria == "aplicativos":
        registros = PruebasAplicativos.objects.all()
    elif categoria == "maquinas":
        registros = PruebasMaquinas.objects.all()

    if formulario_filtro.is_valid():
        datos = formulario_filtro.cleaned_data
        for parametro, campo in {"fecha_desde": "fechaPuestaPunto__gte", "fecha_hasta": "fechaPuestaPunto__lte",
                                 "encargado": "idEncargado", "tipo": "idTipoPrueba", "estado": "idEstado", "resultado": "idResultado"}.items():
            if datos.get(parametro):
                pruebas = pruebas.filter(**{campo: datos[parametro]})
        campos_especificos = {
            "aplicativos": {"proyecto": "idProyecto", "tipoAplicativo": "idTipoAplicativo"},
            "maquinas": {"maquina": "idMaquina", "familia": "idFamilia", "tipoJuego": "idTipoJuego", "protocolo": "idProtocolo"},
        }
        for parametro, campo in campos_especificos.get(categoria, {}).items():
            if datos.get(parametro):
                registros = registros.filter(**{campo: datos[parametro]})
    else:
        pruebas = pruebas.none()
    if categoria != "generales":
        pruebas = pruebas.filter(pk__in=registros.values("idPrueba_id"))

    opciones_estadisticas = []
    for clave, (nombre, _) in categorias.items():
        comunes = parametros.copy()
        for campo in list(comunes):
            if campo not in {"fecha_desde", "fecha_hasta", "encargado", "estado", "resultado"}:
                comunes.pop(campo)
        comunes["categoria"] = clave
        opciones_estadisticas.append({"clave": clave, "nombre": nombre, "url": "?" + comunes.urlencode()})

    total = pruebas.count()
    finalizadas = pruebas.filter(fechaFin__isnull=False).count()
    en_curso = pruebas.filter(fechaInicio__isnull=False, fechaFin__isnull=True).count()
    pendientes = pruebas.filter(fechaInicio__isnull=True).count()

    meses_nombres = ("Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic")
    datos_meses = list(
        pruebas.exclude(fechaPuestaPunto__isnull=True)
        .annotate(mes=TruncMonth("fechaPuestaPunto"))
        .values("mes")
        .annotate(total=Count("idPrueba"))
        .order_by("mes")
    )[-6:]
    max_mes = max((dato["total"] for dato in datos_meses), default=1)
    meses = [{
        "etiqueta": f'{meses_nombres[dato["mes"].month - 1]} {str(dato["mes"].year)[2:]}',
        "total": dato["total"],
        "porcentaje": round(dato["total"] * 100 / max_mes),
    } for dato in datos_meses]

    colores = ("#59e0ba", "#5d8dff", "#f6b85e", "#e86fa8", "#9b7cff", "#45b9d7")
    estados_datos = list(
        pruebas.values("idEstado__nombreEstado")
        .annotate(total=Count("idPrueba"))
        .order_by("-total")
    )
    estados = []
    inicio_segmento = 0
    segmentos = []
    for indice, dato in enumerate(estados_datos):
        porcentaje = round(dato["total"] * 100 / total, 1) if total else 0
        fin_segmento = inicio_segmento + porcentaje
        color = colores[indice % len(colores)]
        estados.append({"nombre": dato["idEstado__nombreEstado"], "total": dato["total"], "porcentaje": porcentaje, "color": color})
        segmentos.append(f"{color} {inicio_segmento}% {fin_segmento}%")
        inicio_segmento = fin_segmento
    gradiente_estados = ", ".join(segmentos) if segmentos else "#26364f 0 100%"

    pruebas_por_categoria = []
    if categoria == "generales":
        for nombre, modelo in (("Aplicativos", PruebasAplicativos), ("Máquinas", PruebasMaquinas)):
            cantidad = pruebas.filter(pk__in=modelo.objects.values("idPrueba_id")).count()
            pruebas_por_categoria.append({"nombre": nombre, "total": cantidad})
        max_categoria = max((dato["total"] for dato in pruebas_por_categoria), default=0) or 1
        for dato in pruebas_por_categoria:
            dato["porcentaje"] = round(dato["total"] * 100 / max_categoria)

    tipos_juego_estadisticas = []
    proveedores_estadisticas = []
    protocolos_estadisticas = []
    gradiente_protocolos = "#26364f 0 100%"
    total_protocolos = 0
    if categoria == "maquinas":
        maquinas_filtradas = registros.filter(idPrueba_id__in=pruebas.values("pk"))

        def agrupar_maquinas(campo, sin_nombre):
            grupos = maquinas_filtradas.values(campo).annotate(
                total=Count("idPrueba_id", distinct=True)
            ).order_by("-total", campo)
            return [{"nombre": grupo[campo] or sin_nombre, "total": grupo["total"]} for grupo in grupos]

        tipos_juego_estadisticas = agrupar_maquinas("idTipoJuego__nombre", "Sin tipo de juego")
        proveedores_estadisticas = agrupar_maquinas("idMaquina__idProveedor__nombreProveedor", "Sin proveedor")
        for grupos in (tipos_juego_estadisticas, proveedores_estadisticas):
            maximo = max((grupo["total"] for grupo in grupos), default=0) or 1
            for grupo in grupos:
                grupo["porcentaje"] = round(grupo["total"] * 100 / maximo)

        protocolos_estadisticas = agrupar_maquinas("idProtocolo__nombreProtocolo", "Sin protocolo")
        total_protocolos = sum(grupo["total"] for grupo in protocolos_estadisticas)
        segmentos_protocolos = []
        acumulado = 0
        for indice, grupo in enumerate(protocolos_estadisticas):
            inicio = acumulado * 100 / total_protocolos
            acumulado += grupo["total"]
            fin = acumulado * 100 / total_protocolos
            grupo["porcentaje"] = round(grupo["total"] * 100 / total_protocolos, 1)
            grupo["color"] = colores[indice % len(colores)]
            segmentos_protocolos.append(f'{grupo["color"]} {inicio}% {fin}%')
        if segmentos_protocolos:
            gradiente_protocolos = ", ".join(segmentos_protocolos)

    proyectos_estadisticas = []
    tipos_aplicativo_estadisticas = []
    gradiente_tipos_aplicativo = "#26364f 0 100%"
    total_tipos_aplicativo = 0
    if categoria == "aplicativos":
        aplicativos_filtrados = registros.filter(idPrueba_id__in=pruebas.values("pk"))
        proyectos = aplicativos_filtrados.values("idProyecto__nombreProyecto").annotate(
            total=Count("idPrueba_id", distinct=True)
        ).order_by("-total", "idProyecto__nombreProyecto")
        proyectos_estadisticas = [{"nombre": dato["idProyecto__nombreProyecto"], "total": dato["total"]} for dato in proyectos]
        maximo = max((dato["total"] for dato in proyectos_estadisticas), default=0) or 1
        for dato in proyectos_estadisticas:
            dato["porcentaje"] = round(dato["total"] * 100 / maximo)
        tipos = aplicativos_filtrados.values("idTipoAplicativo__nombreTipoAplicativo").annotate(
            total=Count("idPrueba_id", distinct=True)
        ).order_by("-total", "idTipoAplicativo__nombreTipoAplicativo")
        tipos_aplicativo_estadisticas = [{"nombre": dato["idTipoAplicativo__nombreTipoAplicativo"], "total": dato["total"]} for dato in tipos]
        total_tipos_aplicativo = sum(dato["total"] for dato in tipos_aplicativo_estadisticas)
        segmentos_tipos = []
        acumulado = 0
        for indice, dato in enumerate(tipos_aplicativo_estadisticas):
            inicio = acumulado * 100 / total_tipos_aplicativo
            acumulado += dato["total"]
            fin = acumulado * 100 / total_tipos_aplicativo
            dato["porcentaje"] = round(dato["total"] * 100 / total_tipos_aplicativo, 1)
            dato["color"] = colores[indice % len(colores)]
            segmentos_tipos.append(f'{dato["color"]} {inicio}% {fin}%')
        if segmentos_tipos:
            gradiente_tipos_aplicativo = ", ".join(segmentos_tipos)

    pruebas_casos = pruebas
    casos = pruebas_casos.aggregate(
        aprobados=Sum("numAprobado"),
        no_aprobados=Sum("numNoAprobado"),
        aprobados_menos=Sum("numAprobadoMenos"),
    )
    casos_resultado = [
        {"nombre": "Aprobados", "total": casos["aprobados"] or 0},
        {"nombre": "No aprobados", "total": casos["no_aprobados"] or 0},
        {"nombre": "Aprobados menos", "total": casos["aprobados_menos"] or 0},
    ]
    max_casos = max((dato["total"] for dato in casos_resultado), default=1) or 1
    for dato in casos_resultado:
        dato["porcentaje"] = round(dato["total"] * 100 / max_casos)

    resultados_estadisticas = []
    resultados_agrupados = pruebas.values("idResultado", "idResultado__nombreResultado").annotate(
        total=Count("idPrueba")
    ).order_by("-total", "idResultado__nombreResultado")
    resultados_estadisticas = [
        {"nombre": dato["idResultado__nombreResultado"] or "Pendiente", "total": dato["total"]}
        for dato in resultados_agrupados
    ]
    max_resultado = max((dato["total"] for dato in resultados_estadisticas), default=0) or 1
    for dato in resultados_estadisticas:
        dato["porcentaje"] = round(dato["total"] * 100 / max_resultado)

    gradiente_resultados = "#26364f 0 100%"
    if categoria == "generales" and total:
        segmentos_resultados = []
        acumulado = 0
        for indice, dato in enumerate(resultados_estadisticas):
            inicio = acumulado * 100 / total
            acumulado += dato["total"]
            fin = acumulado * 100 / total
            dato["porcentaje_total"] = round(dato["total"] * 100 / total, 1)
            dato["color"] = colores[indice % len(colores)]
            segmentos_resultados.append(f'{dato["color"]} {inicio}% {fin}%')
        if segmentos_resultados:
            gradiente_resultados = ", ".join(segmentos_resultados)

    responsables_datos = list(
        pruebas.values("idEncargado__first_name", "idEncargado__last_name", "idEncargado__username")
        .annotate(total=Count("idPrueba"))
        .order_by("-total")[:6]
    )
    max_responsable = max((dato["total"] for dato in responsables_datos), default=1)
    responsables = []
    for dato in responsables_datos:
        nombre = f'{dato["idEncargado__first_name"]} {dato["idEncargado__last_name"]}'.strip() or dato["idEncargado__username"]
        responsables.append({"nombre": nombre, "total": dato["total"], "porcentaje": round(dato["total"] * 100 / max_responsable)})

    detalle_pruebas = []
    pruebas_detalle = pruebas.prefetch_related("pruebas_aplicativos", "pruebas_maquinas").order_by(
        "-fechaPuestaPunto", "-idPrueba"
    )
    for prueba in pruebas_detalle:
        aplicativo = next(iter(prueba.pruebas_aplicativos.all()), None)
        maquina = next(iter(prueba.pruebas_maquinas.all()), None)
        detalle_pruebas.append({
            "id": prueba.pk,
            "codigo": aplicativo.codigoPrueba if aplicativo else (maquina.codigoPrueba if maquina else f"Prueba {prueba.pk}"),
            "nombre": aplicativo.nombrePrueba if aplicativo else (maquina.nombreJuego if maquina else None),
            "encargado": prueba.idEncargado.get_full_name() or prueba.idEncargado.username,
            "estado": prueba.idEstado.nombreEstado,
            "resultado": prueba.idResultado.nombreResultado if prueba.idResultado else "Pendiente",
            "casos": prueba.numCasosPrueba,
            "aprobados": prueba.numAprobado or 0,
            "no_aprobados": prueba.numNoAprobado or 0,
            "aprobados_menos": prueba.numAprobadoMenos or 0,
            "porcentaje_aprobado": prueba.porcentajeAprobado,
            "avance": prueba.porcentajeAvance,
            "avance_css": float(prueba.porcentajeAvance or 0),
        })

    parametros_filtro = parametros.copy()
    parametros_filtro["categoria"] = categoria
    id_detalle = parametros_filtro.pop("detalle", [None])[0]
    querystring_filtros = parametros_filtro.urlencode()
    detalle_seleccionado = None
    detalle_aplicativo = None
    detalle_maquina = None
    if id_detalle:
        detalle_seleccionado = get_object_or_404(pruebas_detalle, pk=id_detalle)
        detalle_aplicativo = next(iter(detalle_seleccionado.pruebas_aplicativos.all()), None)
        detalle_maquina = next(iter(detalle_seleccionado.pruebas_maquinas.all()), None)

    return render(request, "estadisticas/estadisticas.html", {
        "total": total,
        "finalizadas": finalizadas,
        "en_curso": en_curso,
        "pendientes": pendientes,
        "porcentaje_finalizadas": round(finalizadas * 100 / total) if total else 0,
        "meses": meses,
        "estados": estados,
        "gradiente_estados": gradiente_estados,
        "casos_resultado": casos_resultado,
        "pruebas_por_categoria": pruebas_por_categoria,
        "tipos_juego_estadisticas": tipos_juego_estadisticas,
        "proveedores_estadisticas": proveedores_estadisticas,
        "protocolos_estadisticas": protocolos_estadisticas,
        "gradiente_protocolos": gradiente_protocolos,
        "total_protocolos": total_protocolos,
        "proyectos_estadisticas": proyectos_estadisticas,
        "tipos_aplicativo_estadisticas": tipos_aplicativo_estadisticas,
        "gradiente_tipos_aplicativo": gradiente_tipos_aplicativo,
        "total_tipos_aplicativo": total_tipos_aplicativo,
        "responsables": responsables,
        "resultados_estadisticas": resultados_estadisticas,
        "gradiente_resultados": gradiente_resultados,
        "detalle_pruebas": detalle_pruebas,
        "detalle_seleccionado": detalle_seleccionado,
        "detalle_aplicativo": detalle_aplicativo,
        "detalle_maquina": detalle_maquina,
        "querystring_filtros": querystring_filtros,
        "encargados": Usuario.objects.filter(is_active=True, activo=True).order_by("first_name", "last_name", "username"),
        "tipos_prueba": TiposPruebas.objects.filter(activo=True).order_by("nombreTipoPrueba"),
        "estados_catalogo": Estados.objects.filter(activo=True).order_by("nombreEstado"),
        "categoria": categoria,
        "categoria_nombre": categoria_nombre,
        "opciones_estadisticas": opciones_estadisticas,
        "formulario_filtro": formulario_filtro,
        "mostrar_filtros": bool(formulario_filtro.errors),
    })


