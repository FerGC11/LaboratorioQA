from django import forms
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from apps.maquinas.models import JuegosMaquinas, Maquinas, Posiciones
from apps.usuarios.models import Areas, Cargos
from .models import (Estados, FamiliasJuegos, Juegos, Protocolo, Proveedores,
                     Proyectos, Resultados, TipoJuego, TiposAplicativos, TiposPruebas)

# Explicit registry: only catalog data may be managed through this page.
CATALOGOS = {
    "proveedores": ("Proveedores", Proveedores, ("nombreProveedor", "activo")),
    "familias": ("Familias de juegos", FamiliasJuegos, ("nombreFamilia", "activo")),
    "juegos": ("Juegos", Juegos, ("nombreJuego", "idFamilia", "version", "activo")),
    "tipos-juego": ("Tipos de juego", TipoJuego, ("nombre", "activo")),
    "protocolos": ("Protocolos", Protocolo, ("nombreProtocolo", "activo")),
    "tipos-prueba": ("Tipos de prueba", TiposPruebas, ("nombreTipoPrueba", "activo")),
    "estados": ("Estados", Estados, ("nombreEstado", "activo")),
    "resultados": ("Resultados", Resultados, ("nombreResultado", "activo")),
    "tipos-aplicativo": ("Tipos de aplicativo", TiposAplicativos, ("nombreTipoAplicativo", "activo")),
    "proyectos": ("Proyectos", Proyectos, ("nombreProyecto", "activo")),
    "maquinas": ("M\u00e1quinas / gabinetes", Maquinas, ("nombreGabinete", "numeroSerie", "idProveedor", "idPosicion", "activo")),
    "posiciones": ("Posiciones", Posiciones, ("numeroPosicion", "fila", "columna", "activo")),
    "juegos-maquinas": ("Juegos por m\u00e1quina", JuegosMaquinas, ("idJuego", "idMaquina")),
    "cargos": ("Cargos", Cargos, ("nombreCargo", "activo")),
    "areas": ("\u00c1reas", Areas, ("nombreArea", "activo")),
}
ETIQUETAS = {
    "nombreProveedor": "Proveedor", "nombreFamilia": "Familia", "nombreJuego": "Juego",
    "nombre": "Nombre", "nombreProtocolo": "Protocolo", "nombreTipoPrueba": "Tipo de prueba",
    "nombreEstado": "Estado", "nombreResultado": "Resultado", "nombreTipoAplicativo": "Tipo de aplicativo",
    "nombreProyecto": "Proyecto", "nombreGabinete": "Gabinete", "numeroSerie": "N\u00famero de serie",
    "numeroPosicion": "Posici\u00f3n", "nombreCargo": "Cargo", "nombreArea": "\u00c1rea",
    "idFamilia": "Familia", "idProveedor": "Proveedor", "idPosicion": "Posici\u00f3n",
    "idJuego": "Juego", "idMaquina": "M\u00e1quina", "version": "Versi\u00f3n",
    "fila": "Fila", "columna": "Columna", "activo": "Activo",
}


@require_http_methods(["GET", "POST"])
def detalles_generales(request, catalogo="proveedores"):
    if catalogo not in CATALOGOS:
        raise Http404("Cat\u00e1logo no disponible")
    titulo, modelo, campos = CATALOGOS[catalogo]
    registros = modelo.objects.all()
    relaciones = [nombre for nombre in campos if modelo._meta.get_field(nombre).many_to_one]
    if relaciones:
        registros = registros.select_related(*relaciones)
    registro = None
    identificador = request.POST.get("registro_id") if request.method == "POST" else request.GET.get("editar")
    if identificador:
        if not identificador.isdecimal():
            raise Http404("Registro no disponible")
        registro = get_object_or_404(modelo, pk=identificador)
    Formulario = modelform_factory(modelo, fields=campos, labels=ETIQUETAS)
    formulario = Formulario(request.POST if request.method == "POST" else None, instance=registro)
    for campo in formulario.fields.values():
        if isinstance(campo, forms.ModelChoiceField):
            campo.widget.attrs["data-catalog-search"] = campo.label
    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        return redirect(reverse("pruebas:Catalogo", kwargs={"catalogo": catalogo}) + "?guardado=1")
    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("activo", "")
    if busqueda:
        consulta = Q()
        for nombre in campos:
            campo = modelo._meta.get_field(nombre)
            if campo.get_internal_type() in ("CharField", "TextField"):
                consulta |= Q(**{nombre + "__icontains": busqueda})
            elif campo.many_to_one:
                for relacionado in campo.related_model._meta.fields:
                    if relacionado.get_internal_type() == "CharField":
                        consulta |= Q(**{nombre + "__" + relacionado.name + "__icontains": busqueda})
        registros = registros.filter(consulta)
    if "activo" in campos and estado in ("1", "0"):
        registros = registros.filter(activo=estado == "1")
    pagina = Paginator(registros.order_by("pk"), 25).get_page(request.GET.get("pagina"))
    filas = []
    for objeto in pagina:
        celdas = []
        for nombre in campos:
            valor = getattr(objeto, nombre)
            celdas.append(("Activo" if valor else "Inactivo") if nombre == "activo" else str(valor))
        filas.append({"id": objeto.pk, "celdas": celdas})
    parametros = request.GET.copy()
    parametros.pop("pagina", None)
    parametros.pop("editar", None)
    parametros.pop("guardado", None)
    return render(request, "catalogos/detalles_generales.html", {
        "catalogos": [{"slug": slug, "titulo": datos[0]} for slug, datos in CATALOGOS.items()],
        "catalogo": catalogo, "titulo_catalogo": titulo, "formulario": formulario,
        "registro": registro, "filas": filas, "pagina": pagina, "busqueda": busqueda,
        "estado_filtro": estado, "tiene_activo": "activo" in campos,
        "encabezados": [ETIQUETAS[nombre] for nombre in campos], "columnas": len(campos) + 2,
        "querystring": parametros.urlencode(), "guardado": request.GET.get("guardado") == "1",
    })
